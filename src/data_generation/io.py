from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def ensure_directories(*directories: Path) -> None:
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: Iterable[str]) -> None:
    """Write rows to CSV using a stable column order."""

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def write_sample(path: Path, rows: list[dict[str, object]], fieldnames: Iterable[str], limit: int = 100) -> None:
    write_csv(path, rows[:limit], fieldnames)

