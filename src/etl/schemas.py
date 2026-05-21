from __future__ import annotations

REQUIRED_COLUMNS: dict[str, list[str]] = {
    "suppliers": [
        "supplier_id",
        "supplier_name",
        "country",
        "reliability_score",
        "reliability_band",
        "standard_lead_time_days",
        "active_flag",
    ],
    "warehouses": [
        "warehouse_id",
        "warehouse_name",
        "city",
        "state",
        "daily_capacity_units",
        "storage_capacity_units",
        "overload_risk_band",
    ],
    "products": [
        "product_id",
        "product_name",
        "category",
        "primary_supplier_id",
        "unit_cost_eur",
        "reorder_point",
        "hazmat_flag",
    ],
    "inventory": [
        "inventory_id",
        "product_id",
        "warehouse_id",
        "on_hand_units",
        "reserved_units",
        "reorder_point",
        "last_stock_count_date",
    ],
    "orders": [
        "order_id",
        "customer_region",
        "product_id",
        "supplier_id",
        "warehouse_id",
        "order_date",
        "order_quantity",
        "order_value_eur",
        "priority",
        "order_status",
    ],
    "shipments": [
        "shipment_id",
        "order_id",
        "supplier_id",
        "warehouse_id",
        "product_id",
        "ship_date",
        "promised_delivery_date",
        "actual_delivery_date",
        "delay_days",
        "is_delayed",
        "delay_reason",
        "carrier",
        "shipment_status",
        "stockout_flag",
        "warehouse_overload_flag",
    ],
}


DATE_COLUMNS: dict[str, list[str]] = {
    "inventory": ["last_stock_count_date"],
    "orders": ["order_date"],
    "shipments": ["ship_date", "promised_delivery_date", "actual_delivery_date"],
}


BOOLEAN_COLUMNS: dict[str, list[str]] = {
    "suppliers": ["active_flag"],
    "products": ["hazmat_flag"],
    "shipments": ["is_delayed", "stockout_flag", "warehouse_overload_flag"],
}


NUMERIC_COLUMNS: dict[str, list[str]] = {
    "suppliers": ["reliability_score", "standard_lead_time_days"],
    "warehouses": ["daily_capacity_units", "storage_capacity_units"],
    "products": ["unit_cost_eur", "reorder_point"],
    "inventory": ["on_hand_units", "reserved_units", "reorder_point"],
    "orders": ["order_quantity", "order_value_eur"],
    "shipments": ["delay_days"],
}


NON_NEGATIVE_COLUMNS: dict[str, list[str]] = {
    "suppliers": ["reliability_score", "standard_lead_time_days"],
    "warehouses": ["daily_capacity_units", "storage_capacity_units"],
    "products": ["unit_cost_eur", "reorder_point"],
    "inventory": ["on_hand_units", "reserved_units", "reorder_point"],
    "orders": ["order_quantity", "order_value_eur"],
}
