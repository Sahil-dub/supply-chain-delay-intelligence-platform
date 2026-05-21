from __future__ import annotations

from fastapi import APIRouter

from api.config import get_settings
from api.database import check_database_connection
from api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    database_connected = check_database_connection()
    return HealthResponse(
        status="ok" if database_connected else "degraded",
        app_name=settings.app_name,
        environment=settings.app_env,
        database_connected=database_connected,
    )

