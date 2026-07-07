"""Main entry point for AvocaScan AI Service FastAPI application."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.exceptions import AIServiceException
from app.model_loader import get_model_loader
from app.prediction import router
from app.utils import setup_logger

logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle events (startup and shutdown)."""
    settings = get_settings()
    logger.info(
        "Starting up %s (version: %s, env: %s)",
        settings.app_name,
        settings.app_version,
        settings.app_env,
    )
    try:
        model_loader = get_model_loader()
        model_loader.load_models()
        app.state.model_loader = model_loader
    except AIServiceException as exc:
        logger.error("Critical startup failure: Model Loader failed to initialize - %s", exc.message)
        raise exc

    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI Inference Service for AvocaScan two-stage avocado maturity classification.",
        lifespan=lifespan,
    )

    # Register routers
    app.include_router(router)

    # Register custom exception handlers
    @app.exception_handler(AIServiceException)
    async def ai_service_exception_handler(
        request: Request, exc: AIServiceException
    ) -> JSONResponse:
        """Handle custom AI Service exceptions consistently."""
        logger.error("AIServiceException occurred: %s", exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected global exceptions without exposing stack traces."""
        logger.exception("Unexpected error occurred: %s", str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error.",
            },
        )

    return app


app = create_app()

