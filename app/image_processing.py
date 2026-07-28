"""Image processing module for AvocaScan AI Service.

Handles image loading, validation, and stage-specific preprocessing.
"""
import io
import time
import torch
from PIL import Image, UnidentifiedImageError
from torchvision import transforms
from torchvision.transforms import InterpolationMode
from app.config import get_settings, Settings
from app.exceptions import ImageValidationException, ImageLoadException, ImagePreprocessingException
from app.utils import setup_logger

logger = setup_logger()

_PILLOW_FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


def validate_image(image_bytes: bytes, filename: str = "upload", settings: Settings | None = None) -> str:
    """Validate image bytes for non-emptiness, maximum size, and supported format."""
    cfg = settings or get_settings()
    if not image_bytes:
        raise ImageValidationException(f"Uploaded file '{filename}' is empty.")
    if len(image_bytes) > cfg.max_file_size:
        raise ImageValidationException(f"File '{filename}' exceeds size limit.")
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            pillow_format = img.format or ""
    except (UnidentifiedImageError, Exception) as exc:
        raise ImageValidationException(f"File '{filename}' is not a valid image: {exc}")

    mime_type = _PILLOW_FORMAT_TO_MIME.get(pillow_format.upper(), "")
    if mime_type not in cfg.supported_image_formats:
        raise ImageValidationException(f"Format '{pillow_format}' is not supported.")
    return mime_type


def load_image_from_bytes(image_bytes: bytes, filename: str = "upload") -> Image.Image:
    """Load image bytes into a PIL Image, downsampling high-res photos to max 800px to save RAM."""
    if not image_bytes:
        raise ImageLoadException(f"Image file '{filename}' is empty.")
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # Scale down high-resolution mobile photos (e.g., 4000x3000 -> max 800x800) to save 80%+ RAM
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        return img
    except Exception as exc:
        raise ImageLoadException(f"Failed to decode image '{filename}': {exc}")


def remove_background(image: Image.Image, bg_color: tuple = (255, 255, 255)) -> Image.Image:
    """Menghapus background gambar menggunakan OpenCV Otsu thresholding (0 MB extra RAM, tanpa ONNX, 100% bebas OOM)."""
    import numpy as np
    import cv2

    start_time = time.perf_counter()
    try:
        img_np = np.array(image)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Thresholding Otsu untuk memisahkan latar belakang dari objek alpukat
        _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Pembersihan tepi mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # Buat background putih
        white_bg = np.full_like(img_np, bg_color, dtype=np.uint8)

        # Penggabungan (alpha blend)
        mask_3d = (mask[:, :, np.newaxis] / 255.0)
        result_np = (img_np * mask_3d + white_bg * (1.0 - mask_3d)).astype(np.uint8)

        elapsed = (time.perf_counter() - start_time) * 1000
        logger.info("Remove background (OpenCV light) selesai dalam %.2f ms", elapsed)
        return Image.fromarray(result_np)
    except Exception as exc:
        logger.error("Gagal melakukan remove background OpenCV: %s. Tetap menggunakan gambar asli.", exc)
        return image


def build_stage1_transform(settings: Settings | None = None) -> transforms.Compose:
    """Build the Stage 1 transform pipeline."""
    cfg = settings or get_settings()
    return transforms.Compose([
        transforms.Resize((cfg.stage1_resize_height, cfg.stage1_resize_width), interpolation=InterpolationMode.BILINEAR, antialias=True),
        transforms.ToTensor(),
        transforms.Normalize(mean=cfg.normalize_mean, std=cfg.normalize_std),
    ])


def apply_stage1_transform(pil_image: Image.Image, settings: Settings | None = None) -> torch.Tensor:
    """Apply Stage 1 transform to a PIL Image, adding a batch dimension."""
    cfg = settings or get_settings()
    start_time = time.perf_counter()
    try:
        tensor = build_stage1_transform(cfg)(pil_image).unsqueeze(0)
    except Exception as exc:
        raise ImagePreprocessingException(f"Stage 1 preprocessing failed: {exc}")
    logger.info("Stage 1 prep: size=%s -> tensor=%s in %.2f ms", pil_image.size, tuple(tensor.shape), (time.perf_counter() - start_time) * 1000)
    return tensor


def build_stage2_base_transform(settings: Settings | None = None) -> transforms.Compose:
    """Build the Stage 2 base transform pipeline (Resize -> CenterCrop)."""
    cfg = settings or get_settings()
    return transforms.Compose([
        transforms.Resize((cfg.stage2_resize_height, cfg.stage2_resize_width), interpolation=InterpolationMode.BILINEAR, antialias=True),
        transforms.CenterCrop(cfg.stage2_crop_size),
    ])


def build_stage2_tensor_transform(settings: Settings | None = None) -> transforms.Compose:
    """Build the Stage 2 tensor transform pipeline (ToTensor -> Normalize)."""
    cfg = settings or get_settings()
    return transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=cfg.normalize_mean, std=cfg.normalize_std),
    ])


def apply_stage2_base_transform(pil_image: Image.Image, settings: Settings | None = None) -> Image.Image:
    """Apply Stage 2 base transform (Resize + CenterCrop) to a PIL Image."""
    cfg = settings or get_settings()
    start_time = time.perf_counter()
    try:
        cropped = build_stage2_base_transform(cfg)(pil_image)
    except Exception as exc:
        raise ImagePreprocessingException(f"Stage 2 base transform failed: {exc}")
    logger.info("Stage 2 base prep: size=%s -> cropped=%s in %.2f ms", pil_image.size, cropped.size, (time.perf_counter() - start_time) * 1000)
    return cropped


def apply_stage2_tensor_transform(pil_image_cropped: Image.Image, settings: Settings | None = None) -> torch.Tensor:
    """Apply Stage 2 tensor transform to a cropped PIL Image, adding a batch dimension."""
    cfg = settings or get_settings()
    start_time = time.perf_counter()
    try:
        tensor = build_stage2_tensor_transform(cfg)(pil_image_cropped).unsqueeze(0)
    except Exception as exc:
        raise ImagePreprocessingException(f"Stage 2 tensor transform failed: {exc}")
    logger.info("Stage 2 tensor prep: shape=%s in %.2f ms", tuple(tensor.shape), (time.perf_counter() - start_time) * 1000)
    return tensor
