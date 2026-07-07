"""Router and response schemas for AvocaScan AI Service.

Exposes GET /, GET /health, and POST /predict endpoints.
"""
import time
from fastapi import APIRouter, File, UploadFile, status
from pydantic import BaseModel, Field
from app.prediction_service import PredictionService
from app.exceptions import AIServiceException
from app.utils import setup_logger

logger = setup_logger()
router = APIRouter(tags=["Prediction"])
prediction_service = PredictionService()


class RootResponse(BaseModel):
    """Response schema for service root endpoint."""
    service: str = Field(..., description="Name of the service", example="AvocaScan AI Service")
    status: str = Field(..., description="Service running status", example="running")


class HealthResponse(BaseModel):
    """Response schema for service health check endpoint."""
    status: str = Field(..., description="Service health status", example="healthy")


class PredictionResponse(BaseModel):
    """Response schema for avocado classification prediction."""
    success: bool = Field(..., description="Indicates if the request was successful")
    message: str = Field(..., description="Descriptive status message of the prediction")
    data: dict = Field(..., description="Prediction results containing stage 1 and stage 2 outputs")


@router.get("/", response_model=RootResponse, status_code=status.HTTP_200_OK)
async def root() -> RootResponse:
    """Return identification and running status of the service."""
    return RootResponse(service="AvocaScan AI Service", status="running")


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health() -> HealthResponse:
    """Return health check status for system monitoring."""
    return HealthResponse(status="healthy")


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict(image: UploadFile = File(...)) -> PredictionResponse:
    """Run two-stage avocado prediction pipeline on uploaded image file."""
    start_time = time.perf_counter()
    filename = image.filename or "upload"
    try:
        image_bytes = await image.read()
        result = prediction_service.predict(image_bytes, filename=filename)
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "Endpoint POST /predict completed in %.2f ms - Status: success",
            duration_ms
        )

        message = "Prediction completed." if result["is_avocado"] else "Object is not an avocado."

        return PredictionResponse(
            success=True,
            message=message,
            data=result,
        )
    except AIServiceException as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.error(
            "Endpoint POST /predict failed in %.2f ms - Status: failed - Error: %s",
            duration_ms, exc.message
        )
        raise exc

