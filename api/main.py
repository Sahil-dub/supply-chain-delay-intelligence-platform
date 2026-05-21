from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.config import get_settings
from api.exceptions import AnalyticsServiceError
from api.routes.analytics import router as analytics_router
from api.routes.health import router as health_router

settings = get_settings()
logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
LOGGER = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.6.0",
        description="FastAPI backend for supply chain delay KPI and analytics reporting.",
    )

    app.include_router(health_router)
    app.include_router(analytics_router)

    @app.exception_handler(AnalyticsServiceError)
    async def analytics_service_exception_handler(
        _request: Request,
        exc: AnalyticsServiceError,
    ) -> JSONResponse:
        LOGGER.exception("Analytics service error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        LOGGER.exception("Unhandled API error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


app = create_app()

