from __future__ import annotations

import logging

import pandas as pd

from src.etl.schemas import BOOLEAN_COLUMNS, DATE_COLUMNS, NON_NEGATIVE_COLUMNS, NUMERIC_COLUMNS, REQUIRED_COLUMNS
from src.etl.validation import summarize_delay_label_issues, validate_non_negative

LOGGER = logging.getLogger(__name__)


def transform_tables(raw_tables: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    """Clean raw source tables and build analytics-ready outputs."""

    tables = {name: dataframe.copy() for name, dataframe in raw_tables.items()}

    for table_name, dataframe in tables.items():
        _strip_text_values(dataframe)
        _standardize_categorical_values(table_name, dataframe)
        _coerce_dates(table_name, dataframe)
        _coerce_numbers(table_name, dataframe)
        _coerce_booleans(table_name, dataframe)
        dataframe.drop_duplicates(inplace=True)
        validate_non_negative(table_name, dataframe, NON_NEGATIVE_COLUMNS.get(table_name, []))

    inconsistent_delay_labels_before = summarize_delay_label_issues(tables["shipments"])
    _clean_shipments(tables["shipments"])
    inconsistent_delay_labels_after = summarize_delay_label_issues(tables["shipments"])

    analytics_tables = {
        "dim_suppliers": tables["suppliers"][REQUIRED_COLUMNS["suppliers"]].copy(),
        "dim_warehouses": tables["warehouses"][REQUIRED_COLUMNS["warehouses"]].copy(),
        "dim_products": tables["products"][REQUIRED_COLUMNS["products"]].copy(),
        "fact_inventory": tables["inventory"][REQUIRED_COLUMNS["inventory"]].copy(),
        "fact_orders": tables["orders"][REQUIRED_COLUMNS["orders"]].copy(),
        "fact_shipments": tables["shipments"][REQUIRED_COLUMNS["shipments"]].copy(),
    }
    analytics_tables["mart_shipment_analytics"] = _build_shipment_mart(analytics_tables)

    summary = {
        "inconsistent_delay_labels_before": inconsistent_delay_labels_before,
        "inconsistent_delay_labels_after": inconsistent_delay_labels_after,
        "fact_orders_rows": len(analytics_tables["fact_orders"]),
        "fact_shipments_rows": len(analytics_tables["fact_shipments"]),
        "mart_shipment_analytics_rows": len(analytics_tables["mart_shipment_analytics"]),
    }
    LOGGER.info("ETL transformation summary: %s", summary)

    return analytics_tables, summary


def _strip_text_values(dataframe: pd.DataFrame) -> None:
    text_columns = dataframe.select_dtypes(include="object").columns
    for column in text_columns:
        dataframe[column] = dataframe[column].astype(str).str.strip()
        dataframe.loc[dataframe[column].isin({"", "nan", "None"}), column] = pd.NA


def _standardize_categorical_values(table_name: str, dataframe: pd.DataFrame) -> None:
    lower_case_columns = {
        "suppliers": ["reliability_band"],
        "warehouses": ["overload_risk_band"],
        "orders": ["priority", "order_status"],
        "shipments": ["shipment_status", "delay_reason"],
    }
    title_case_columns = {
        "suppliers": ["country"],
        "products": ["category"],
        "orders": ["customer_region"],
    }

    for column in lower_case_columns.get(table_name, []):
        dataframe[column] = dataframe[column].astype("string").str.strip().str.lower()

    for column in title_case_columns.get(table_name, []):
        dataframe[column] = dataframe[column].astype("string").str.strip()


def _coerce_dates(table_name: str, dataframe: pd.DataFrame) -> None:
    for column in DATE_COLUMNS.get(table_name, []):
        dataframe[column] = pd.to_datetime(dataframe[column], errors="coerce").dt.date


def _coerce_numbers(table_name: str, dataframe: pd.DataFrame) -> None:
    for column in NUMERIC_COLUMNS.get(table_name, []):
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")


def _coerce_booleans(table_name: str, dataframe: pd.DataFrame) -> None:
    for column in BOOLEAN_COLUMNS.get(table_name, []):
        dataframe[column] = dataframe[column].map(_to_nullable_bool).astype("boolean")


def _clean_shipments(shipments: pd.DataFrame) -> None:
    delivered = shipments["shipment_status"].eq("delivered")
    in_transit = shipments["shipment_status"].eq("in_transit")
    has_promised_and_actual = shipments["promised_delivery_date"].notna() & shipments["actual_delivery_date"].notna()

    recalculated_delay_days = (
        pd.to_datetime(shipments["actual_delivery_date"]) - pd.to_datetime(shipments["promised_delivery_date"])
    ).dt.days

    shipments.loc[delivered & has_promised_and_actual, "delay_days"] = recalculated_delay_days
    shipments.loc[delivered & shipments["delay_days"].notna(), "is_delayed"] = shipments["delay_days"] > 0
    shipments.loc[delivered & shipments["is_delayed"].eq(False), "delay_reason"] = pd.NA
    shipments.loc[in_transit, ["actual_delivery_date", "delay_days", "is_delayed", "delay_reason"]] = pd.NA


def _build_shipment_mart(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    shipments = tables["fact_shipments"]
    orders = tables["fact_orders"]
    suppliers = tables["dim_suppliers"]
    warehouses = tables["dim_warehouses"]
    products = tables["dim_products"]

    mart = (
        shipments.merge(
            orders[
                [
                    "order_id",
                    "customer_region",
                    "order_date",
                    "order_quantity",
                    "order_value_eur",
                    "priority",
                    "order_status",
                ]
            ],
            on="order_id",
            how="left",
        )
        .merge(suppliers[["supplier_id", "supplier_name", "reliability_score", "reliability_band"]], on="supplier_id")
        .merge(warehouses[["warehouse_id", "warehouse_name", "city", "overload_risk_band"]], on="warehouse_id")
        .merge(products[["product_id", "product_name", "category", "unit_cost_eur", "reorder_point"]], on="product_id")
    )

    mart["delivery_month"] = (
        pd.to_datetime(mart["promised_delivery_date"], errors="coerce").dt.to_period("M").astype(str)
    )
    mart["stockout_risk_flag"] = mart["stockout_flag"]
    mart["late_delivery_flag"] = mart["is_delayed"]

    return mart[
        [
            "shipment_id",
            "order_id",
            "order_date",
            "delivery_month",
            "customer_region",
            "supplier_id",
            "supplier_name",
            "reliability_score",
            "reliability_band",
            "warehouse_id",
            "warehouse_name",
            "city",
            "overload_risk_band",
            "product_id",
            "product_name",
            "category",
            "order_quantity",
            "order_value_eur",
            "priority",
            "shipment_status",
            "promised_delivery_date",
            "actual_delivery_date",
            "delay_days",
            "late_delivery_flag",
            "delay_reason",
            "stockout_risk_flag",
            "warehouse_overload_flag",
        ]
    ]


def _to_nullable_bool(value: object) -> bool | None:
    if pd.isna(value) or value == "":
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    return None
