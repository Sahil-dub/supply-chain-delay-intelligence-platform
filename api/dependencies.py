from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from api.database import get_db_session
from api.services.analytics_service import AnalyticsService


def get_analytics_service(session: Session = Depends(get_db_session)) -> Generator[AnalyticsService, None, None]:
    yield AnalyticsService(session)

