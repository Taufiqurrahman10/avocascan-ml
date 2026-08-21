"""Application configuration module using Pydantic BaseSettings."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application environment settings loaded from environment variables or defaults."""
    app_env: str = "development"
    app_name: str = "AvocaScan AI Service"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    api_token: str = ""
    log_level: str = "INFO"
    model_stage1_path: str = "models/stage1/best_model.pth"
    model_stage1_class_names_path: str = "models/stage1/class_names.json"
    model_stage2_path: str = "models/stage2/best_model.pth"
    model_stage2_class_names_path: str = "models/stage2/class_names.json"
    ai_service_timeout: int = 30
    max_file_size: int = 10485760  # 10 MB in bytes

    # --- Stage 1 Preprocessing Parameters (identik dengan training) ---
    # Resize langsung ke 224x224, tanpa center crop
    stage1_resize_height: int = 224
    stage1_resize_width: int = 224

    # --- Stage 2 Preprocessing Parameters (identik dengan training) ---
    # Resize ke 256x256, lalu CenterCrop ke 224x224
    stage2_resize_height: int = 256
    stage2_resize_width: int = 256
    stage2_crop_size: int = 224

    # Standardisasi objek Stage 2 (identik dengan dataset pelatihan)
    stage2_canvas_width: int = 1200
    stage2_canvas_height: int = 1600
    stage2_object_occupancy: float = 0.80
    stage2_white_threshold: int = 245
    stage2_min_component_ratio: float = 0.002

    # --- Normalization Parameters (ImageNet, digunakan oleh kedua stage) ---
    normalize_mean: list[float] = [0.485, 0.456, 0.406]
    normalize_std: list[float] = [0.229, 0.224, 0.225]

    # --- Supported Image MIME Types ---
    supported_image_formats: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # --- HSV Feature Extraction Parameters (identik dengan training) ---
    # cv2.calcHist bins per channel (H, S, V) — 3 channels × 64 bins = 192 features
    hsv_histogram_bins: int = 64
    # Range used for all three HSV channels in cv2.calcHist — identical to training
    # Note: OpenCV H channel is [0,179] for uint8, but training uses [0,256] for all
    # channels, so we must keep [0, 256] to produce identical bin distribution.
    hsv_histogram_range: list[int] = [0, 256]

    # --- GLCM Feature Extraction Parameters (identik dengan training) ---
    # skimage.feature.graycomatrix / graycoprops parameters
    glcm_distances: list[int] = [1]
    glcm_angles: list[float] = [0.0]
    glcm_levels: int = 256
    glcm_symmetric: bool = True
    glcm_normed: bool = True
    # Properties extracted via graycoprops — order must not change
    glcm_properties: list[str] = ["contrast", "energy", "homogeneity", "correlation"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )



@lru_cache
def get_settings() -> Settings:
    """Retrieve cached application settings instance.

    Returns:
        Settings: Cached application configuration instance.
    """
    return Settings()
