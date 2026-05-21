from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def fetch_one(session: Session, sql: str, parameters: dict[str, object] | None = None) -> dict[str, object] | None:
    row = session.execute(text(sql), parameters or {}).mappings().first()
    return dict(row) if row else None


def fetch_all(session: Session, sql: str, parameters: dict[str, object] | None = None) -> list[dict[str, object]]:
    rows = session.execute(text(sql), parameters or {}).mappings().all()
    return [dict(row) for row in rows]

