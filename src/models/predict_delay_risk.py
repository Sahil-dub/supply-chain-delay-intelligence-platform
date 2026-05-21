from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from src.models.features import add_historical_features_for_prediction

DEFAULT_EXAMPLE = {
    "customer_region": "DE-East",
    "supplier_id": "SUP-008",
    "reliability_band": "low",
    "warehouse_id": "WH-001",
    "overload_risk_band": "medium",
    "category": "Textiles",
    "priority": "standard",
    "reliability_score": 0.604,
    "order_quantity": 82,
    "order_value_eur": 9776.86,
    "stockout_risk_flag": 0,
    "warehouse_overload_flag": 1,
    "order_month": 3,
}


def predict_single_shipment(model_path: Path, shipment: dict[str, object]) -> dict[str, object]:
    artifact = joblib.load(model_path)
    enriched = add_historical_features_for_prediction(shipment, artifact["historical_maps"])
    feature_frame = pd.DataFrame([enriched])[artifact["feature_columns"]]
    probability = float(artifact["model"].predict_proba(feature_frame)[0][1])
    threshold = float(artifact.get("threshold", 0.5))
    return {
        "delay_risk_probability": round(probability, 4),
        "delay_risk_label": "likely_delayed" if probability >= threshold else "likely_on_time",
        "threshold": threshold,
        "input_features": enriched,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict delay risk for one shipment-like example.")
    parser.add_argument("--model-path", default="models/delay_risk_model.joblib")
    parser.add_argument("--input-json", help="Optional JSON string with shipment features.")
    args = parser.parse_args()

    shipment = json.loads(args.input_json) if args.input_json else DEFAULT_EXAMPLE
    prediction = predict_single_shipment(Path(args.model_path), shipment)
    print(json.dumps(prediction, indent=2))


if __name__ == "__main__":
    main()

