from pathlib import Path

import pandas as pd

from src.models.config import ModelConfig
from src.models.features import (
    TARGET_COLUMN,
    add_historical_delay_features,
    prepare_modeling_frame,
)
from src.models.predict_delay_risk import predict_single_shipment
from src.models.train_model import train_delay_models


def test_prepare_modeling_frame_creates_binary_target() -> None:
    dataframe = _sample_mart()

    modeling_frame = prepare_modeling_frame(dataframe)

    assert TARGET_COLUMN in modeling_frame.columns
    assert set(modeling_frame[TARGET_COLUMN].unique()) == {0, 1}
    assert modeling_frame["shipment_status"].eq("delivered").all()


def test_historical_delay_features_are_train_derived() -> None:
    modeling_frame = prepare_modeling_frame(_sample_mart())
    train = modeling_frame.iloc[:3].copy()
    scoring = modeling_frame.iloc[3:].copy()

    train_with_features, scoring_with_features, maps = add_historical_delay_features(train, scoring)

    assert "supplier_historical_delay_rate" in train_with_features.columns
    assert "warehouse_historical_delay_rate" in scoring_with_features.columns
    assert "global_delay_rate" in maps


def test_training_pipeline_saves_artifacts_and_predicts(tmp_path: Path) -> None:
    input_path = tmp_path / "mart.csv"
    model_path = tmp_path / "delay_risk_model.joblib"
    metrics_path = tmp_path / "model_metrics.json"
    feature_importance_path = tmp_path / "feature_importance.csv"
    _larger_sample_mart().to_csv(input_path, index=False)

    train_delay_models(
        ModelConfig(
            input_path=input_path,
            model_path=model_path,
            metrics_path=metrics_path,
            feature_importance_path=feature_importance_path,
            test_size=0.3,
            random_state=42,
        )
    )

    prediction = predict_single_shipment(
        model_path,
        {
            "customer_region": "DE-East",
            "supplier_id": "SUP-001",
            "reliability_band": "low",
            "warehouse_id": "WH-001",
            "overload_risk_band": "high",
            "category": "Electronics",
            "priority": "standard",
            "reliability_score": 0.62,
            "order_quantity": 100,
            "order_value_eur": 9000.0,
            "stockout_risk_flag": 1,
            "warehouse_overload_flag": 1,
            "order_month": 11,
        },
    )

    assert model_path.exists()
    assert metrics_path.exists()
    assert feature_importance_path.exists()
    assert 0 <= prediction["delay_risk_probability"] <= 1


def _sample_mart() -> pd.DataFrame:
    rows = [
        _row("SHP-001", "SUP-001", "low", "WH-001", "high", "Electronics", "True", 0.62, 1, 1, 11),
        _row("SHP-002", "SUP-002", "high", "WH-002", "low", "Packaging", "False", 0.93, 0, 0, 2),
        _row("SHP-003", "SUP-001", "low", "WH-001", "high", "Electronics", "True", 0.62, 1, 0, 12),
        _row("SHP-004", "SUP-002", "high", "WH-002", "low", "Packaging", "False", 0.93, 0, 0, 3),
    ]
    return pd.DataFrame(rows)


def _larger_sample_mart() -> pd.DataFrame:
    rows = []
    for index in range(80):
        delayed = index % 3 == 0
        supplier_id = "SUP-001" if delayed else "SUP-002"
        warehouse_id = "WH-001" if index % 2 == 0 else "WH-002"
        rows.append(
            _row(
                shipment_id=f"SHP-{index:03d}",
                supplier_id=supplier_id,
                reliability_band="low" if delayed else "high",
                warehouse_id=warehouse_id,
                overload_risk_band="high" if delayed else "low",
                category="Electronics" if index % 2 == 0 else "Packaging",
                late_delivery_flag=str(delayed),
                reliability_score=0.62 if delayed else 0.93,
                stockout_risk_flag=int(delayed),
                warehouse_overload_flag=int(delayed),
                order_month=(index % 12) + 1,
            )
        )
    return pd.DataFrame(rows)


def _row(
    shipment_id: str,
    supplier_id: str,
    reliability_band: str,
    warehouse_id: str,
    overload_risk_band: str,
    category: str,
    late_delivery_flag: str,
    reliability_score: float,
    stockout_risk_flag: int,
    warehouse_overload_flag: int,
    order_month: int,
) -> dict[str, object]:
    return {
        "shipment_id": shipment_id,
        "order_id": shipment_id.replace("SHP", "ORD"),
        "order_date": f"2025-{order_month:02d}-01",
        "delivery_month": f"2025-{order_month:02d}",
        "customer_region": "DE-East",
        "supplier_id": supplier_id,
        "supplier_name": "Example Supplier",
        "reliability_score": reliability_score,
        "reliability_band": reliability_band,
        "warehouse_id": warehouse_id,
        "warehouse_name": "Example Warehouse",
        "city": "Berlin",
        "overload_risk_band": overload_risk_band,
        "product_id": "PRD-001",
        "product_name": "Example Product",
        "category": category,
        "order_quantity": 100,
        "order_value_eur": 9000.0,
        "priority": "standard",
        "shipment_status": "delivered",
        "promised_delivery_date": f"2025-{order_month:02d}-05",
        "actual_delivery_date": f"2025-{order_month:02d}-08",
        "delay_days": 3 if late_delivery_flag == "True" else -1,
        "late_delivery_flag": late_delivery_flag,
        "delay_reason": "carrier_delay" if late_delivery_flag == "True" else "",
        "stockout_risk_flag": stockout_risk_flag,
        "warehouse_overload_flag": warehouse_overload_flag,
    }

