from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GenerationConfig:
    """Settings that control the size and shape of generated datasets."""

    seed: int
    num_suppliers: int
    num_warehouses: int
    num_products: int
    num_orders: int
    start_date: str
    end_date: str
    raw_data_dir: Path
    processed_data_dir: Path
    sample_data_dir: Path


def load_config(config_path: str | Path) -> GenerationConfig:
    """Load generation settings from a JSON file."""

    path = Path(config_path)
    with path.open("r", encoding="utf-8") as file:
        values = json.load(file)

    return GenerationConfig(
        seed=int(values["seed"]),
        num_suppliers=int(values["num_suppliers"]),
        num_warehouses=int(values["num_warehouses"]),
        num_products=int(values["num_products"]),
        num_orders=int(values["num_orders"]),
        start_date=str(values["start_date"]),
        end_date=str(values["end_date"]),
        raw_data_dir=Path(values["raw_data_dir"]),
        processed_data_dir=Path(values["processed_data_dir"]),
        sample_data_dir=Path(values["sample_data_dir"]),
    )

