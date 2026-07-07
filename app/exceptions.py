"""Custom exceptions for AvocaScan AI Service.

Consolidates all exception classes into a single file for simplicity.
"""

class AIServiceException(Exception):
    """Base exception for all AI Service errors."""
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ModelException(AIServiceException):
    """Base exception for model errors."""
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message, status_code)


class ModelNotFoundException(ModelException):
    """Raised when model files or configs are missing."""
    def __init__(self, message: str) -> None:
        super().__init__(message, 500)


class ModelLoadException(ModelException):
    """Raised when model loading into PyTorch fails."""
    def __init__(self, message: str) -> None:
        super().__init__(message, 500)


class ImageException(AIServiceException):
    """Base exception for image processing errors."""
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message, status_code)


class ImageLoadException(ImageException):
    """Raised when an image cannot be read or decoded."""
    def __init__(self, message: str) -> None:
        super().__init__(message, 400)


class ImageValidationException(ImageException):
    """Raised when image format, size, or content validation fails."""
    def __init__(self, message: str) -> None:
        super().__init__(message, 422)


class ImagePreprocessingException(ImageException):
    """Raised when image transforms or feature extraction fails."""
    def __init__(self, message: str) -> None:
        super().__init__(message, 500)
