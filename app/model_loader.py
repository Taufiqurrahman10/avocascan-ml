"""Model loader module for AvocaScan AI Service.

Loads Stage 1 and Stage 2 PyTorch models into memory once at application startup.
"""
import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Any
import torch
import torch.nn as nn
from torchvision import models
from app.config import get_settings, Settings
from app.exceptions import ModelNotFoundException, ModelLoadException
from app.utils import setup_logger

logger = setup_logger()


class HybridModel(nn.Module):
    """Hybrid PyTorch Model combining visual MobileNetV3 small features and HSV/GLCM features."""

    def __init__(self, num_manual_features: int = 196, num_classes: int = 3) -> None:
        super().__init__()
        backbone = models.mobilenet_v3_small(weights=None)
        # Freeze parameters
        for param in backbone.parameters():
            param.requires_grad = False
        backbone.classifier = nn.Identity()
        self.backbone = backbone

        self.manual_branch = nn.Sequential(
            nn.BatchNorm1d(num_manual_features),
            nn.Linear(num_manual_features, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
        )

        self.classifier = nn.Sequential(
            nn.Linear(576 + 64, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes),
        )

    def forward(self, image: torch.Tensor, manual_feat: torch.Tensor) -> torch.Tensor:
        visual_out = self.backbone(image)
        manual_out = self.manual_branch(manual_feat)
        combined = torch.cat([visual_out, manual_out], dim=1)
        return self.classifier(combined)


class ModelLoader:
    """Singleton helper class for managing PyTorch models and labels in memory."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._stage1_model: Any = None
        self._stage1_class_names: list[str] | None = None
        self._stage2_model: Any = None
        self._stage2_class_names: list[str] | None = None
        self._is_loaded = False

    def load_models(self) -> None:
        """Load both models and class mappings from the paths specified in Settings."""
        if self._is_loaded:
            logger.info("Models are already loaded into memory. Skipping reload.")
            return

        logger.info("Initializing Model Loader and checking model artifacts...")
        self._load_stage1()
        self._load_stage2()
        self._is_loaded = True
        logger.info("All AI models and class mappings loaded successfully into memory.")

    def _load_stage1(self) -> None:
        model_path = Path(self._settings.model_stage1_path)
        class_names_path = Path(self._settings.model_stage1_class_names_path)

        if not model_path.is_file():
            raise ModelNotFoundException(f"Stage 1 model file not found: {model_path}")
        if not class_names_path.is_file():
            raise ModelNotFoundException(f"Stage 1 class_names.json not found: {class_names_path}")

        try:
            with open(class_names_path, "r", encoding="utf-8") as f:
                class_names = json.load(f)
            self._stage1_class_names = [str(c) for c in class_names]
        except Exception as exc:
            raise ModelLoadException(f"Failed to parse Stage 1 class_names.json: {exc}")

        start_time = time.perf_counter()
        try:
            checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
            model = models.mobilenet_v3_small(weights=None)
            model.classifier[2] = nn.Dropout(p=0.5)
            model.classifier[3] = nn.Linear(1024, 2)
            model.load_state_dict(checkpoint["model_state_dict"])
            model.eval()
            self._stage1_model = model
        except Exception as exc:
            raise ModelLoadException(f"Failed to load Stage 1 model: {exc}")
        logger.info("Stage 1 model loaded (classes: %d, time: %.2f ms)", len(self._stage1_class_names), (time.perf_counter() - start_time) * 1000)

    def _load_stage2(self) -> None:
        model_path = Path(self._settings.model_stage2_path)
        class_names_path = Path(self._settings.model_stage2_class_names_path)

        if not model_path.is_file():
            raise ModelNotFoundException(f"Stage 2 model file not found: {model_path}")
        if not class_names_path.is_file():
            raise ModelNotFoundException(f"Stage 2 class_names.json not found: {class_names_path}")

        try:
            with open(class_names_path, "r", encoding="utf-8") as f:
                class_names = json.load(f)
            self._stage2_class_names = [str(c) for c in class_names]
        except Exception as exc:
            raise ModelLoadException(f"Failed to parse Stage 2 class_names.json: {exc}")

        start_time = time.perf_counter()
        try:
            checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
            num_manual_features = checkpoint.get("num_manual_features", 196)
            num_classes = checkpoint.get("num_classes", 3)
            model = HybridModel(num_manual_features=num_manual_features, num_classes=num_classes)
            model.load_state_dict(checkpoint["model_state_dict"])
            model.eval()
            self._stage2_model = model
        except Exception as exc:
            raise ModelLoadException(f"Failed to load Stage 2 model: {exc}")
        logger.info("Stage 2 model loaded (classes: %d, time: %.2f ms)", len(self._stage2_class_names), (time.perf_counter() - start_time) * 1000)

    def get_stage1_model(self) -> Any:
        """Get Stage 1 model."""
        if self._stage1_model is None:
            raise ModelLoadException("Stage 1 model not loaded.")
        return self._stage1_model

    def get_stage1_class_names(self) -> list[str]:
        """Get Stage 1 class names list."""
        if self._stage1_class_names is None:
            raise ModelLoadException("Stage 1 class names not loaded.")
        return self._stage1_class_names

    def get_stage2_model(self) -> Any:
        """Get Stage 2 model."""
        if self._stage2_model is None:
            raise ModelLoadException("Stage 2 model not loaded.")
        return self._stage2_model

    def get_stage2_class_names(self) -> list[str]:
        """Get Stage 2 class names list."""
        if self._stage2_class_names is None:
            raise ModelLoadException("Stage 2 class names not loaded.")
        return self._stage2_class_names

    @property
    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self._is_loaded


@lru_cache
def get_model_loader() -> ModelLoader:
    """Get the cached singleton model loader instance."""
    return ModelLoader()
