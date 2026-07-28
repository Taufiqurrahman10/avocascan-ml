"""Prediction service module for AvocaScan AI Service.

This module coordinates the two-stage classification pipeline: image loading,
validation, stage 1 prediction, feature extraction, stage 2 prediction, and response construction.
"""
import time
import torch
from app.config import get_settings
from app.exceptions import (
    AIServiceException,
    ModelLoadException,
    ImagePreprocessingException,
)
from app.feature_extractor import extract_features
from app.image_processing import (
    validate_image,
    load_image_from_bytes,
    remove_background,
    apply_stage1_transform,
    apply_stage2_base_transform,
    apply_stage2_tensor_transform,
)
from app.model_loader import get_model_loader
from app.utils import setup_logger

logger = setup_logger()


class PredictionService:
    """Service class encapsulating two-stage classification workflow logic."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.model_loader = get_model_loader()

    def predict(self, image_bytes: bytes, filename: str = "upload") -> dict:
        """Run the full two-stage classification pipeline on the input image bytes.

        Args:
            image_bytes: The raw image bytes.
            filename: The name of the file (used for logging and validation).

        Returns:
            A dictionary containing prediction labels and confidence scores.
        """
        total_start = time.perf_counter()

        # 1. Ensure models are loaded
        if not self.model_loader.is_loaded:
            try:
                self.model_loader.load_models()
            except Exception as exc:
                raise ModelLoadException(f"Failed to load models during inference: {exc}")

        # 2. Validate image
        validate_image(image_bytes, filename, self.settings)

        # 3. Load image
        pil_image = load_image_from_bytes(image_bytes, filename)

        # 4. Remove background agar hasil deteksi akurat & sesuai dataset WBG
        t_rembg_start = time.perf_counter()
        pil_image = remove_background(pil_image)
        t_rembg = (time.perf_counter() - t_rembg_start) * 1000

        # 5. Stage 1 Preprocessing
        t_prep1_start = time.perf_counter()
        try:
            image_tensor_s1 = apply_stage1_transform(pil_image, self.settings)
        except Exception as exc:
            raise ImagePreprocessingException(f"Stage 1 preprocessing failed: {exc}")
        t_prep1 = (time.perf_counter() - t_prep1_start) * 1000

        # 6. Stage 1 Inference
        t_s1_start = time.perf_counter()
        try:
            s1_model = self.model_loader.get_stage1_model()
            with torch.no_grad():
                s1_output = s1_model(image_tensor_s1)
                s1_probs = torch.softmax(s1_output, dim=1)
        except Exception as exc:
            raise AIServiceException(f"Stage 1 model inference failed: {exc}", 500)
        t_s1 = (time.perf_counter() - t_s1_start) * 1000

        s1_class_names = self.model_loader.get_stage1_class_names()
        s1_pred_idx = torch.argmax(s1_probs, dim=1).item()
        s1_label = s1_class_names[s1_pred_idx]
        s1_conf = s1_probs[0, s1_pred_idx].item()

        # 7. Decision Logic (Stage 1 == "alpukat")
        if s1_label != "alpukat":
            total_time = (time.perf_counter() - total_start) * 1000
            logger.info(
                "Predict non-avocado (stage1_prediction=%s, stage1_confidence=%.4f). "
                "Time breakdown: rembg=%.2f ms, prep_s1=%.2f ms, stage1=%.2f ms. Total inference time: %.2f ms",
                s1_label, s1_conf, t_rembg, t_prep1, t_s1, total_time
            )
            return {
                "is_avocado": False,
                "stage1_prediction": s1_label,
                "stage1_confidence": s1_conf,
                "stage2_prediction": None,
                "stage2_confidence": None,
            }

        # 7. Stage 2 Preprocessing & Feature Extraction
        # Base transform (Resize + CenterCrop)
        t_prep2_start = time.perf_counter()
        try:
            pil_cropped = apply_stage2_base_transform(pil_image, self.settings)
        except Exception as exc:
            raise ImagePreprocessingException(f"Stage 2 base transform failed: {exc}")
        t_prep2_base = (time.perf_counter() - t_prep2_start) * 1000

        # Feature extraction on cropped image
        t_feat_start = time.perf_counter()
        feat_tensor = extract_features(pil_cropped, self.settings)
        t_feat = (time.perf_counter() - t_feat_start) * 1000

        # Tensor transform (ToTensor + Normalize)
        t_prep2_tensor_start = time.perf_counter()
        try:
            image_tensor_s2 = apply_stage2_tensor_transform(pil_cropped, self.settings)
        except Exception as exc:
            raise ImagePreprocessingException(f"Stage 2 tensor transform failed: {exc}")
        t_prep2 = t_prep2_base + (time.perf_counter() - t_prep2_tensor_start) * 1000

        # 8. Stage 2 Inference
        t_s2_start = time.perf_counter()
        try:
            s2_model = self.model_loader.get_stage2_model()
            feat_tensor_batched = feat_tensor.unsqueeze(0)
            with torch.no_grad():
                s2_output = s2_model(image_tensor_s2, feat_tensor_batched)
                s2_probs = torch.softmax(s2_output, dim=1)
        except Exception as exc:
            raise AIServiceException(f"Stage 2 model inference failed: {exc}", 500)
        t_s2 = (time.perf_counter() - t_s2_start) * 1000

        s2_class_names = self.model_loader.get_stage2_class_names()
        s2_pred_idx = torch.argmax(s2_probs, dim=1).item()
        s2_label = s2_class_names[s2_pred_idx]
        s2_conf = s2_probs[0, s2_pred_idx].item()

        # 9. Log performance timings
        total_time = (time.perf_counter() - total_start) * 1000
        logger.info(
            "Predict avocado (stage1_prediction=%s, stage1_confidence=%.4f, "
            "stage2_prediction=%s, stage2_confidence=%.4f). "
            "Time breakdown: rembg=%.2f ms, prep_s1=%.2f ms, stage1=%.2f ms, prep_s2=%.2f ms, "
            "feat=%.2f ms, stage2=%.2f ms. Total inference time: %.2f ms",
            s1_label, s1_conf, s2_label, s2_conf,
            t_rembg, t_prep1, t_s1, t_prep2, t_feat, t_s2, total_time
        )

        import gc
        gc.collect()

        return {
            "is_avocado": True,
            "stage1_prediction": s1_label,
            "stage1_confidence": s1_conf,
            "stage2_prediction": s2_label,
            "stage2_confidence": s2_conf,
        }

