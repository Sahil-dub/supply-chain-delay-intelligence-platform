from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.etl.schemas import REQUIRED_COLUMNS

LOGGER = logging.getLogger(__name__)


def read_csv_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    dataframe = pd.read_csv(path, keep_default_na=False)
    LOGGER.info("Read %s rows from %s", len(dataframe), path)
    return dataframe


def read_raw_tables(raw_data_dir: Path) -> dict[str, pd.DataFrame]:
    """Read Phase 2 raw CSV files."""

    return {table_name: read_csv_table(raw_data_dir / f"{table_name}.csv") for table_name in REQUIRED_COLUMNS}


def read_existing_processed_tables(processed_data_dir: Path) -> dict[str, pd.DataFrame]:
    """Read useful Phase 2 processed files when present for comparison and lineage checks."""

    optional_files = {
        "orders_clean_previous": processed_data_dir / "orders_clean.csv",
        "shipments_clean_previous": processed_data_dir / "shipments_clean.csv",
        "shipment_analytics_previous": processed_data_dir / "shipment_analytics.csv",
    }
    tables: dict[str, pd.DataFrame] = {}

    for table_name, path in optional_files.items():
        if path.exists():
            tables[table_name] = read_csv_table(path)
        else:
            LOGGER.warning("Optional processed input not found: %s", path)

    return tables

