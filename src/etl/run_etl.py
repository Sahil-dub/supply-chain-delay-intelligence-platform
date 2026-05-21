from __future__ import annotations

import argparse
import logging

from src.etl.config import EtlConfig
from src.etl.extract import read_existing_processed_tables, read_raw_tables
from src.etl.load import write_etl_summary, write_processed_tables
from src.etl.transform import transform_tables
from src.etl.validation import validate_source_tables

LOGGER = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CSV ETL pipeline for supply chain analytics tables.")
    parser.add_argument("--raw-dir", default="data/raw", help="Directory containing raw Phase 2 CSV files.")
    parser.add_argument("--processed-dir", default="data/processed", help="Directory for cleaned ETL outputs.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = EtlConfig.from_paths(args.raw_dir, args.processed_dir)

    LOGGER.info("Starting ETL pipeline")
    raw_tables = read_raw_tables(config.raw_data_dir)
    processed_inputs = read_existing_processed_tables(config.processed_data_dir)
    LOGGER.info("Read %s optional processed input tables", len(processed_inputs))

    validate_source_tables(raw_tables)
    analytics_tables, summary = transform_tables(raw_tables)

    write_processed_tables(analytics_tables, config.processed_data_dir)
    write_etl_summary(summary, config.processed_data_dir)
    LOGGER.info("ETL pipeline completed successfully")


if __name__ == "__main__":
    main()

