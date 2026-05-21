from __future__ import annotations

from collections import Counter


def validate_relationships(
    suppliers: list[dict[str, object]],
    warehouses: list[dict[str, object]],
    products: list[dict[str, object]],
    inventory: list[dict[str, object]],
    orders: list[dict[str, object]],
    shipments: list[dict[str, object]],
) -> None:
    supplier_ids = {row["supplier_id"] for row in suppliers}
    warehouse_ids = {row["warehouse_id"] for row in warehouses}
    product_ids = {row["product_id"] for row in products}
    order_ids = {row["order_id"] for row in orders}

    _assert_references("products.primary_supplier_id", products, "primary_supplier_id", supplier_ids)
    _assert_references("inventory.product_id", inventory, "product_id", product_ids)
    _assert_references("inventory.warehouse_id", inventory, "warehouse_id", warehouse_ids)
    _assert_references("orders.supplier_id", orders, "supplier_id", supplier_ids)
    _assert_references("orders.warehouse_id", orders, "warehouse_id", warehouse_ids)
    _assert_references("orders.product_id", orders, "product_id", product_ids)
    _assert_references("shipments.order_id", shipments, "order_id", order_ids)

    duplicate_orders = _duplicates(row["order_id"] for row in orders)
    duplicate_shipments = _duplicates(row["shipment_id"] for row in shipments)
    if duplicate_orders:
        raise ValueError(f"Duplicate order IDs found: {duplicate_orders[:5]}")
    if duplicate_shipments:
        raise ValueError(f"Duplicate shipment IDs found: {duplicate_shipments[:5]}")


def validate_operational_metrics(shipments: list[dict[str, object]], min_rows: int) -> dict[str, object]:
    delivered = [row for row in shipments if row["shipment_status"] == "delivered"]
    delayed = [row for row in delivered if row["is_delayed"] is True]

    if len(shipments) < min_rows:
        raise ValueError(f"Expected at least {min_rows} shipment rows, found {len(shipments)}")
    if not delivered:
        raise ValueError("No delivered shipments generated")

    delay_rate = len(delayed) / len(delivered)
    if not 0.15 <= delay_rate <= 0.55:
        raise ValueError(f"Delay rate {delay_rate:.1%} is outside realistic configured range")

    reason_counts = Counter(row["delay_reason"] for row in delayed if row["delay_reason"])
    return {
        "shipment_rows": len(shipments),
        "delivered_rows": len(delivered),
        "delay_rate": round(delay_rate, 4),
        "top_delay_reasons": dict(reason_counts.most_common(5)),
    }


def _assert_references(
    name: str,
    rows: list[dict[str, object]],
    column: str,
    valid_values: set[object],
) -> None:
    invalid = [row[column] for row in rows if row[column] not in valid_values]
    if invalid:
        raise ValueError(f"Invalid references in {name}: {invalid[:5]}")


def _duplicates(values: object) -> list[object]:
    counts = Counter(values)
    return [value for value, count in counts.items() if count > 1]

