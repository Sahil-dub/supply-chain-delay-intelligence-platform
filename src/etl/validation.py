from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.etl.schemas import REQUIRED_COLUMNS


class EtlValidationError(ValueError):
    """Raised when source data fails an ETL validation rule."""


@dataclass(frozen=True)
class RelationshipRule:
    child_table: str
    child_column: str
    parent_table: str
    parent_column: str


RELATIONSHIP_RULES = [
    RelationshipRule("products", "primary_supplier_id", "suppliers", "supplier_id"),
    RelationshipRule("inventory", "product_id", "products", "product_id"),
    RelationshipRule("inventory", "warehouse_id", "warehouses", "warehouse_id"),
    RelationshipRule("orders", "product_id", "products", "product_id"),
    RelationshipRule("orders", "supplier_id", "suppliers", "supplier_id"),
    RelationshipRule("orders", "warehouse_id", "warehouses", "warehouse_id"),
    RelationshipRule("shipments", "order_id", "orders", "order_id"),
    RelationshipRule("shipments", "product_id", "products", "product_id"),
    RelationshipRule("shipments", "supplier_id", "suppliers", "supplier_id"),
    RelationshipRule("shipments", "warehouse_id", "warehouses", "warehouse_id"),
]


def validate_required_columns(table_name: str, dataframe: pd.DataFrame, required_columns: list[str]) -> None:
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        raise EtlValidationError(f"{table_name} is missing required columns: {missing_columns}")


def validate_not_empty(table_name: str, dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        raise EtlValidationError(f"{table_name} is empty")


def validate_unique_key(table_name: str, dataframe: pd.DataFrame, key_column: str) -> None:
    duplicates = dataframe.loc[dataframe[key_column].duplicated(), key_column].head(5).tolist()
    if duplicates:
        raise EtlValidationError(f"{table_name}.{key_column} contains duplicate values: {duplicates}")


def validate_relationship(
    child_table: str,
    child_dataframe: pd.DataFrame,
    child_column: str,
    parent_table: str,
    parent_dataframe: pd.DataFrame,
    parent_column: str,
) -> None:
    parent_values = set(parent_dataframe[parent_column].dropna().astype(str))
    invalid_values = (
        child_dataframe.loc[~child_dataframe[child_column].astype(str).isin(parent_values), child_column]
        .drop_duplicates()
        .head(5)
        .tolist()
    )
    if invalid_values:
        raise EtlValidationError(
            f"{child_table}.{child_column} contains values not found in "
            f"{parent_table}.{parent_column}: {invalid_values}"
        )


def validate_non_negative(table_name: str, dataframe: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        if column not in dataframe.columns:
            continue
        numeric_values = pd.to_numeric(dataframe[column], errors="coerce")
        invalid_count = int((numeric_values < 0).sum())
        if invalid_count:
            raise EtlValidationError(f"{table_name}.{column} contains {invalid_count} negative values")


def validate_source_tables(tables: dict[str, pd.DataFrame]) -> None:
    for table_name, required_columns in REQUIRED_COLUMNS.items():
        if table_name not in tables:
            raise EtlValidationError(f"Missing source table: {table_name}")
        validate_not_empty(table_name, tables[table_name])
        validate_required_columns(table_name, tables[table_name], required_columns)

    validate_unique_key("suppliers", tables["suppliers"], "supplier_id")
    validate_unique_key("warehouses", tables["warehouses"], "warehouse_id")
    validate_unique_key("products", tables["products"], "product_id")
    validate_unique_key("inventory", tables["inventory"], "inventory_id")
    validate_unique_key("orders", tables["orders"], "order_id")
    validate_unique_key("shipments", tables["shipments"], "shipment_id")

    for rule in RELATIONSHIP_RULES:
        validate_relationship(
            rule.child_table,
            tables[rule.child_table],
            rule.child_column,
            rule.parent_table,
            tables[rule.parent_table],
            rule.parent_column,
        )


def summarize_delay_label_issues(shipments: pd.DataFrame) -> int:
    delivered = shipments["shipment_status"].astype(str).str.strip().str.lower().eq("delivered")
    promised_date = pd.to_datetime(shipments["promised_delivery_date"], errors="coerce")
    actual_date = pd.to_datetime(shipments["actual_delivery_date"], errors="coerce")
    date_based_delay_days = (actual_date - promised_date).dt.days
    source_delay_days = pd.to_numeric(shipments["delay_days"], errors="coerce")
    delay_days = date_based_delay_days.fillna(source_delay_days)
    is_delayed = shipments["is_delayed"].map(_to_nullable_bool)
    inconsistent = delivered & delay_days.notna() & is_delayed.notna() & (is_delayed != (delay_days > 0))
    return int(inconsistent.sum())


def _to_nullable_bool(value: object) -> bool | None:
    if pd.isna(value) or value == "":
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    return None
