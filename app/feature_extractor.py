"""Feature extraction module for AvocaScan AI Service.

Consolidates HSV color histogram and GLCM texture extraction into a single module.
"""
import time
import cv2
import numpy as np
import torch
from PIL import Image
from skimage.feature import graycomatrix, graycoprops
from app.config import get_settings, Settings
from app.exceptions import ImagePreprocessingException
from app.utils import setup_logger

logger = setup_logger()
_EXPECTED_FEATURES = 196


def extract_hsv(image_np: np.ndarray, settings: Settings | None = None) -> np.ndarray:
    """Compute per-channel HSV colour histogram from an RGB NumPy array."""
    cfg = settings or get_settings()
    if image_np.ndim != 3 or image_np.shape[2] != 3 or image_np.dtype != np.uint8:
        raise ImagePreprocessingException(
            f"HSV expects uint8 RGB image of shape (H,W,3), got {image_np.shape} {image_np.dtype}"
        )
    try:
        hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
        features = []
        for i in range(3):
            hist = cv2.calcHist([hsv], [i], None, [cfg.hsv_histogram_bins], cfg.hsv_histogram_range)
            features.extend(hist.flatten())
        return np.array(features, dtype=np.float32)
    except Exception as exc:
        raise ImagePreprocessingException(f"HSV feature extraction failed: {exc}")


def extract_glcm(image_np: np.ndarray, settings: Settings | None = None) -> np.ndarray:
    """Compute GLCM texture statistics from an RGB NumPy array."""
    cfg = settings or get_settings()
    if image_np.ndim != 3 or image_np.shape[2] != 3 or image_np.dtype != np.uint8:
        raise ImagePreprocessingException(
            f"GLCM expects uint8 RGB image of shape (H,W,3), got {image_np.shape} {image_np.dtype}"
        )
    try:
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        glcm = graycomatrix(
            gray,
            distances=cfg.glcm_distances,
            angles=cfg.glcm_angles,
            levels=cfg.glcm_levels,
            symmetric=cfg.glcm_symmetric,
            normed=cfg.glcm_normed
        )
        values = [float(graycoprops(glcm, prop)[0, 0]) for prop in cfg.glcm_properties]
        return np.array(values, dtype=np.float32)
    except Exception as exc:
        raise ImagePreprocessingException(f"GLCM feature extraction failed: {exc}")


def extract_features(cropped_pil: Image.Image, settings: Settings | None = None) -> torch.Tensor:
    """Combine HSV and GLCM features into a single 196-dimensional tensor."""
    cfg = settings or get_settings()
    start_time = time.perf_counter()
    if not isinstance(cropped_pil, Image.Image):
        raise ImagePreprocessingException(f"extract_features expects a PIL Image, got {type(cropped_pil).__name__}")
    if cropped_pil.mode != "RGB":
        raise ImagePreprocessingException(f"PIL Image must be in RGB mode, got '{cropped_pil.mode}'")
    try:
        image_np = np.array(cropped_pil, dtype=np.uint8)
    except Exception as exc:
        raise ImagePreprocessingException(f"Failed to convert PIL Image to NumPy array: {exc}")

    hsv_start = time.perf_counter()
    hsv_features = extract_hsv(image_np, cfg)
    hsv_time = (time.perf_counter() - hsv_start) * 1000

    glcm_start = time.perf_counter()
    glcm_features = extract_glcm(image_np, cfg)
    glcm_time = (time.perf_counter() - glcm_start) * 1000

    combined = np.concatenate([hsv_features, glcm_features]).astype(np.float32)
    if len(combined) != _EXPECTED_FEATURES:
        raise ImagePreprocessingException(
            f"Feature count mismatch: expected {_EXPECTED_FEATURES}, got {len(combined)}"
        )

    tensor = torch.tensor(combined, dtype=torch.float32)
    total_time = (time.perf_counter() - start_time) * 1000
    logger.info(
        "Features extracted: hsv=%d (%.2f ms), glcm=%d (%.2f ms), total=%d (%.2f ms)",
        len(hsv_features), hsv_time, len(glcm_features), glcm_time, len(combined), total_time
    )
    return tensor
