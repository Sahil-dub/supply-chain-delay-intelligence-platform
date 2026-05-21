from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelConfig:
    input_path: Path = Path("data/processed/mart_shipment_analytics.csv")
    model_path: Path = Path("models/delay_risk_model.joblib")
    metrics_path: Path = Path("reports/model_metrics.json")
    feature_importance_path: Path = Path("reports/feature_importance.csv")
    test_size: float = 0.25
    random_state: int = 42
    delay_threshold: float = 0.5

