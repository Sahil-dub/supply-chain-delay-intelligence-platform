from __future__ import annotations

from datetime import datetime, timedelta


def clean_orders(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    cleaned = []

    for row in rows:
        copied = row.copy()
        copied["order_quantity"] = int(copied["order_quantity"])
        copied["order_value_eur"] = round(float(copied["order_value_eur"]), 2)
        cleaned.append(copied)

    return cleaned


def clean_shipments(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    cleaned = []

    for row in rows:
        copied = row.copy()
        promised = str(copied["promised_delivery_date"])
        actual = str(copied["actual_delivery_date"])

        # Missing promised dates are imputed from ship date plus five days.
        # This creates a clean analytical file while preserving raw data quality issues.
        if not promised:
            ship_date = datetime.strptime(str(copied["ship_date"]), "%Y-%m-%d").date()
            copied["promised_delivery_date"] = (ship_date + timedelta(days=5)).isoformat()

        if actual:
            promised_date = datetime.strptime(str(copied["promised_delivery_date"]), "%Y-%m-%d").date()
            actual_date = datetime.strptime(actual, "%Y-%m-%d").date()
            delay_days = (actual_date - promised_date).days
            copied["delay_days"] = delay_days
            copied["is_delayed"] = delay_days > 0
            if delay_days <= 0:
                copied["delay_reason"] = ""
        else:
            copied["delay_days"] = ""
            copied["is_delayed"] = ""
            copied["delay_reason"] = ""

        cleaned.append(copied)

    return cleaned


def build_shipment_analytics(
    shipments: list[dict[str, object]],
    orders: list[dict[str, object]],
    suppliers: list[dict[str, object]],
    warehouses: list[dict[str, object]],
    products: list[dict[str, object]],
) -> list[dict[str, object]]:
    order_lookup = {row["order_id"]: row for row in orders}
    supplier_lookup = {row["supplier_id"]: row for row in suppliers}
    warehouse_lookup = {row["warehouse_id"]: row for row in warehouses}
    product_lookup = {row["product_id"]: row for row in products}

    analytics_rows = []
    for shipment in shipments:
        order = order_lookup[shipment["order_id"]]
        supplier = supplier_lookup[shipment["supplier_id"]]
        warehouse = warehouse_lookup[shipment["warehouse_id"]]
        product = product_lookup[shipment["product_id"]]
        analytics_rows.append(
            {
                "shipment_id": shipment["shipment_id"],
                "order_id": shipment["order_id"],
                "order_date": order["order_date"],
                "ship_date": shipment["ship_date"],
                "promised_delivery_date": shipment["promised_delivery_date"],
                "actual_delivery_date": shipment["actual_delivery_date"],
                "supplier_id": shipment["supplier_id"],
                "supplier_name": supplier["supplier_name"],
                "supplier_reliability_score": supplier["reliability_score"],
                "warehouse_id": shipment["warehouse_id"],
                "warehouse_name": warehouse["warehouse_name"],
                "warehouse_overload_flag": shipment["warehouse_overload_flag"],
                "product_id": shipment["product_id"],
                "category": product["category"],
                "customer_region": order["customer_region"],
                "order_quantity": order["order_quantity"],
                "priority": order["priority"],
                "shipment_status": shipment["shipment_status"],
                "stockout_flag": shipment["stockout_flag"],
                "delay_days": shipment["delay_days"],
                "is_delayed": shipment["is_delayed"],
                "delay_reason": shipment["delay_reason"],
            }
        )

    return analytics_rows
