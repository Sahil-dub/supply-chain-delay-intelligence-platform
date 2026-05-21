from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ApiSettings:
    app_name: str
    app_env: str
    database_url: str
    log_level: str


def get_settings() -> ApiSettings:
    return ApiSettings(
        app_name=os.getenv("APP_NAME", "Supply Chain Delay Intelligence Platform"),
        app_env=os.getenv("APP_ENV", "local"),
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay",
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )

