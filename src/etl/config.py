from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EtlConfig:
    """Filesystem settings for the CSV-based ETL pipeline."""

    raw_data_dir: Path = Path("data/raw")
    processed_data_dir: Path = Path("data/processed")

    @classmethod
    def from_paths(cls, raw_data_dir: str, processed_data_dir: str) -> "EtlConfig":
        return cls(raw_data_dir=Path(raw_data_dir), processed_data_dir=Path(processed_data_dir))

