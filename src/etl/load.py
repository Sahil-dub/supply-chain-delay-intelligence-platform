from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

LOGGER = logging.getLogger(__name__)


def write_processed_tables(tables: dict[str, pd.DataFrame], processed_data_dir: Path) -> None:
    processed_data_dir.mkdir(parents=True, exist_ok=True)

    for table_name, dataframe in tables.items():
        output_path = processed_data_dir / f"{table_name}.csv"
        dataframe.to_csv(output_path, index=False)
        LOGGER.info("Wrote %s rows to %s", len(dataframe), output_path)


def write_etl_summary(summary: dict[str, object], processed_data_dir: Path) -> None:
    output_path = processed_data_dir / "etl_summary.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)
    LOGGER.info("Wrote ETL summary to %s", output_path)

