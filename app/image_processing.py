"""Image processing module for AvocaScan AI Service.

Handles image loading, validation, and stage-specific preprocessing.
"""
import io
import time
from functools import lru_cache

import cv2
import numpy as np
import torch
from PIL import Image, ImageOps, UnidentifiedImageError
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
    """Load image bytes into a PIL Image and convert to RGB."""
    if not image_bytes:
        raise ImageLoadException(f"Image file '{filename}' is empty.")
    try:
        image = Image.open(io.BytesIO(image_bytes))
        return ImageOps.exif_transpose(image).convert("RGB")
    except Exception as exc:
        raise ImageLoadException(f"Failed to decode image '{filename}': {exc}")


def load_image_from_path(image_path: str, convert_rgb: bool = True) -> Image.Image:
    """Load an image from a path into a PIL Image."""
    try:
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)
        return img.convert("RGB") if convert_rgb else img
    except Exception as exc:
        raise ImageLoadException(f"Failed to open image from path '{image_path}': {exc}")


@lru_cache(maxsize=1)
def _get_rembg_session():
    """Create one reusable U2-Net session, matching dataset preprocessing."""
    from rembg import new_session

    return new_session("u2net")


def remove_background(image: Image.Image, bg_color: tuple = (255, 255, 255)) -> Image.Image:
    """Menghapus background gambar menggunakan library rembg dan menggantinya dengan background putih serapi mungkin."""
    try:
        from rembg import remove
    except ImportError:
        logger.warning("Library rembg belum terinstall. Tetap menggunakan gambar asli.")
        return image

    start_time = time.perf_counter()
    try:
        # 1. Hapus background gambar (hasilnya RGBA transparan)
        # post_process_mask=True merapikan tepi objek agar potongannya halus dan rapi
        rgba_img = remove(
            image.convert("RGB"),
            session=_get_rembg_session(),
            post_process_mask=True,
        ).convert("RGBA")

        # 2. Buat kanvas background putih baru sesuai ukuran gambar asli
        white_bg = Image.new("RGBA", rgba_img.size, bg_color + (255,))

        # 3. Gabungkan objek alpukat ke atas background putih
        white_bg.alpha_composite(rgba_img)

        # 4. Ubah kembali ke RGB (3 channel) agar bisa diproses oleh model
        result_img = white_bg.convert("RGB")

        elapsed = (time.perf_counter() - start_time) * 1000
        logger.info("Remove background selesai dalam %.2f ms", elapsed)
        return result_img
    except Exception as exc:
        logger.error("Gagal melakukan remove background: %s. Tetap menggunakan gambar asli.", exc)
        return image


def _object_bbox(
    image: Image.Image,
    white_threshold: int,
    min_component_ratio: float,
) -> tuple[int, int, int, int]:
    """Find the foreground bounding box using the same rules as training data."""
    image_np = np.asarray(image.convert("RGB"))
    mask = (np.min(image_np, axis=2) < white_threshold).astype(np.uint8)
    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask, connectivity=8
    )
    if component_count <= 1:
        raise ImagePreprocessingException("Stage 2 object was not detected")

    largest_area = int(stats[1:, cv2.CC_STAT_AREA].max())
    minimum_area = max(50, round(largest_area * min_component_ratio))
    kept_mask = np.zeros_like(mask)
    for label in range(1, component_count):
        if stats[label, cv2.CC_STAT_AREA] >= minimum_area:
            kept_mask[labels == label] = 1

    ys, xs = np.nonzero(kept_mask)
    if len(xs) == 0:
        raise ImagePreprocessingException("Stage 2 object components were not detected")
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def standardize_stage2_object_scale(
    pil_image: Image.Image,
    settings: Settings | None = None,
) -> Image.Image:
    """Center the object at 80% occupancy on the same 3:4 canvas as training."""
    cfg = settings or get_settings()
    start_time = time.perf_counter()
    if not 0.0 < cfg.stage2_object_occupancy <= 1.0:
        raise ImagePreprocessingException("stage2_object_occupancy must be in (0, 1]")

    try:
        image = pil_image.convert("RGB")
        left, top, right, bottom = _object_bbox(
            image,
            cfg.stage2_white_threshold,
            cfg.stage2_min_component_ratio,
        )
        subject = image.crop((left, top, right, bottom))
        subject_width, subject_height = subject.size
        scale = min(
            (cfg.stage2_canvas_width * cfg.stage2_object_occupancy)
            / subject_width,
            (cfg.stage2_canvas_height * cfg.stage2_object_occupancy)
            / subject_height,
        )
        output_size = (
            max(1, round(subject_width * scale)),
            max(1, round(subject_height * scale)),
        )
        subject = subject.resize(output_size, Image.Resampling.LANCZOS)
        canvas = Image.new(
            "RGB",
            (cfg.stage2_canvas_width, cfg.stage2_canvas_height),
            "white",
        )
        position = (
            (cfg.stage2_canvas_width - output_size[0]) // 2,
            (cfg.stage2_canvas_height - output_size[1]) // 2,
        )
        canvas.paste(subject, position)
    except ImagePreprocessingException:
        raise
    except Exception as exc:
        raise ImagePreprocessingException(
            f"Stage 2 object standardization failed: {exc}"
        ) from exc

    logger.info(
        "Stage 2 object standardization: source=%s, bbox=%s, output=%s, "
        "occupancy=%.2f in %.2f ms",
        pil_image.size,
        (left, top, right, bottom),
        canvas.size,
        cfg.stage2_object_occupancy,
        (time.perf_counter() - start_time) * 1000,
    )
    return canvas


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
