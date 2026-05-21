import pandas as pd
import pytest

from src.etl.transform import transform_tables
from src.etl.validation import EtlValidationError, summarize_delay_label_issues, validate_relationship


def test_validate_relationship_raises_for_missing_parent_key() -> None:
    child = pd.DataFrame({"supplier_id": ["SUP-001", "SUP-999"]})
    parent = pd.DataFrame({"supplier_id": ["SUP-001"]})

    with pytest.raises(EtlValidationError):
        validate_relationship("orders", child, "supplier_id", "suppliers", parent, "supplier_id")


def test_transform_corrects_inconsistent_delay_label() -> None:
    raw_tables = _minimal_valid_tables()

    before_count = summarize_delay_label_issues(raw_tables["shipments"])
    analytics_tables, summary = transform_tables(raw_tables)
    fact_shipments = analytics_tables["fact_shipments"]

    assert before_count == 1
    assert summary["inconsistent_delay_labels_before"] == 1
    assert summary["inconsistent_delay_labels_after"] == 0
    assert bool(fact_shipments.loc[0, "is_delayed"]) is True
    assert int(fact_shipments.loc[0, "delay_days"]) == 2


def _minimal_valid_tables() -> dict[str, pd.DataFrame]:
    return {
        "suppliers": pd.DataFrame(
            [
                {
                    "supplier_id": "SUP-001",
                    "supplier_name": "Rhine Components",
                    "country": "Germany",
                    "reliability_score": "0.91",
                    "reliability_band": "High",
                    "standard_lead_time_days": "5",
                    "active_flag": "True",
                }
            ]
        ),
        "warehouses": pd.DataFrame(
            [
                {
                    "warehouse_id": "WH-001",
                    "warehouse_name": "Berlin Distribution Center",
                    "city": "Berlin",
                    "state": "BE",
                    "daily_capacity_units": "1000",
                    "storage_capacity_units": "25000",
                    "overload_risk_band": "Medium",
                }
            ]
        ),
        "products": pd.DataFrame(
            [
                {
                    "product_id": "PRD-0001",
                    "product_name": "Sensor 0001",
                    "category": "Electronics",
                    "primary_supplier_id": "SUP-001",
                    "unit_cost_eur": "49.90",
                    "reorder_point": "100",
                    "hazmat_flag": "False",
                }
            ]
        ),
        "inventory": pd.DataFrame(
            [
                {
                    "inventory_id": "INV-PRD-0001-WH-001",
                    "product_id": "PRD-0001",
                    "warehouse_id": "WH-001",
                    "on_hand_units": "250",
                    "reserved_units": "20",
                    "reorder_point": "100",
                    "last_stock_count_date": "2026-01-10",
                }
            ]
        ),
        "orders": pd.DataFrame(
            [
                {
                    "order_id": "ORD-000001",
                    "customer_region": "DE-East",
                    "product_id": "PRD-0001",
                    "supplier_id": "SUP-001",
                    "warehouse_id": "WH-001",
                    "order_date": "2025-05-01",
                    "order_quantity": "10",
                    "order_value_eur": "499.00",
                    "priority": "Standard",
                    "order_status": "Fulfilled",
                }
            ]
        ),
        "shipments": pd.DataFrame(
            [
                {
                    "shipment_id": "SHP-000001",
                    "order_id": "ORD-000001",
                    "supplier_id": "SUP-001",
                    "warehouse_id": "WH-001",
                    "product_id": "PRD-0001",
                    "ship_date": "2025-05-02",
                    "promised_delivery_date": "2025-05-07",
                    "actual_delivery_date": "2025-05-09",
                    "delay_days": "-1",
                    "is_delayed": "False",
                    "delay_reason": "carrier_delay",
                    "carrier": "DHL Freight",
                    "shipment_status": "Delivered",
                    "stockout_flag": "False",
                    "warehouse_overload_flag": "False",
                }
            ]
        ),
    }

