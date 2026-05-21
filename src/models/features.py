from __future__ import annotations

import pandas as pd

CATEGORICAL_FEATURES = [
    "customer_region",
    "supplier_id",
    "reliability_band",
    "warehouse_id",
    "overload_risk_band",
    "category",
    "priority",
]

NUMERICAL_FEATURES = [
    "reliability_score",
    "order_quantity",
    "order_value_eur",
    "stockout_risk_flag",
    "warehouse_overload_flag",
    "order_month",
    "supplier_historical_delay_rate",
    "warehouse_historical_delay_rate",
    "category_historical_delay_rate",
]

TARGET_COLUMN = "delayed_flag"


def prepare_modeling_frame(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create a clean modeling dataset from the shipment analytics mart."""

    delivered = dataframe.loc[dataframe["shipment_status"].astype(str).str.lower().eq("delivered")].copy()
    delivered[TARGET_COLUMN] = delivered["late_delivery_flag"].map(_to_bool).astype(int)
    delivered["order_date"] = pd.to_datetime(delivered["order_date"], errors="coerce")
    delivered["order_month"] = delivered["order_date"].dt.month

    for column in ["stockout_risk_flag", "warehouse_overload_flag"]:
        delivered[column] = delivered[column].map(_to_bool).astype(int)

    delivered["reliability_score"] = pd.to_numeric(delivered["reliability_score"], errors="coerce")
    delivered["order_quantity"] = pd.to_numeric(delivered["order_quantity"], errors="coerce")
    delivered["order_value_eur"] = pd.to_numeric(delivered["order_value_eur"], errors="coerce")

    required_columns = CATEGORICAL_FEATURES + NUMERICAL_FEATURES[:6] + [TARGET_COLUMN]
    return delivered.dropna(subset=required_columns).reset_index(drop=True)


def add_historical_delay_features(
    train_data: pd.DataFrame,
    scoring_data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Add train-derived historical delay rates without using test labels."""

    train = train_data.copy()
    scoring = scoring_data.copy()
    global_delay_rate = float(train[TARGET_COLUMN].mean())

    maps = {
        "supplier_historical_delay_rate": _rate_map(train, "supplier_id"),
        "warehouse_historical_delay_rate": _rate_map(train, "warehouse_id"),
        "category_historical_delay_rate": _rate_map(train, "category"),
    }

    for feature_name, mapping in maps.items():
        key_column = feature_name.replace("_historical_delay_rate", "_id")
        if feature_name == "category_historical_delay_rate":
            key_column = "category"
        train[feature_name] = train[key_column].map(mapping).fillna(global_delay_rate)
        scoring[feature_name] = scoring[key_column].map(mapping).fillna(global_delay_rate)

    artifact_maps = {name: {str(key): float(value) for key, value in mapping.items()} for name, mapping in maps.items()}
    artifact_maps["global_delay_rate"] = global_delay_rate

    return train, scoring, artifact_maps


def add_historical_features_for_prediction(
    shipment: dict[str, object],
    historical_maps: dict[str, object],
) -> dict[str, object]:
    enriched = shipment.copy()
    global_rate = float(historical_maps.get("global_delay_rate", 0.4))

    feature_sources = {
        "supplier_historical_delay_rate": "supplier_id",
        "warehouse_historical_delay_rate": "warehouse_id",
        "category_historical_delay_rate": "category",
    }
    for feature_name, source_column in feature_sources.items():
        mapping = historical_maps.get(feature_name, {})
        if isinstance(mapping, dict):
            enriched[feature_name] = float(mapping.get(str(enriched.get(source_column)), global_rate))
        else:
            enriched[feature_name] = global_rate

    return enriched


def get_feature_columns() -> list[str]:
    return CATEGORICAL_FEATURES + NUMERICAL_FEATURES


def _rate_map(dataframe: pd.DataFrame, group_column: str) -> dict[object, float]:
    return dataframe.groupby(group_column)[TARGET_COLUMN].mean().to_dict()


def _to_bool(value: object) -> bool:
    normalized = str(value).strip().lower()
    return normalized in {"true", "1", "yes", "y"}

