from __future__ import annotations

import argparse
import json
import logging
import random
from pathlib import Path

from src.data_generation.cleaning import build_shipment_analytics, clean_orders, clean_shipments
from src.data_generation.config import load_config
from src.data_generation.generators import (
    generate_inventory,
    generate_orders_and_shipments,
    generate_products,
    generate_suppliers,
    generate_warehouses,
)
from src.data_generation.io import ensure_directories, write_csv, write_sample
from src.data_generation.validation import validate_operational_metrics, validate_relationships


LOGGER = logging.getLogger(__name__)


RAW_COLUMNS = {
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

ANALYTICS_COLUMNS = [
    "shipment_id",
    "order_id",
    "order_date",
    "ship_date",
    "promised_delivery_date",
    "actual_delivery_date",
    "supplier_id",
    "supplier_name",
    "supplier_reliability_score",
    "warehouse_id",
    "warehouse_name",
    "warehouse_overload_flag",
    "product_id",
    "category",
    "customer_region",
    "order_quantity",
    "priority",
    "shipment_status",
    "stockout_flag",
    "delay_days",
    "is_delayed",
    "delay_reason",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic supply chain CSV datasets.")
    parser.add_argument(
        "--config",
        default="src/config/data_generation.json",
        help="Path to JSON generation config.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_config(args.config)
    rng = random.Random(config.seed)

    ensure_directories(config.raw_data_dir, config.processed_data_dir, config.sample_data_dir)
    LOGGER.info("Generating synthetic datasets with seed=%s", config.seed)

    suppliers = generate_suppliers(config, rng)
    warehouses = generate_warehouses(config, rng)
    products = generate_products(config, rng, suppliers)
    inventory = generate_inventory(products, warehouses, rng)
    orders, shipments = generate_orders_and_shipments(config, suppliers, warehouses, products, inventory, rng)

    validate_relationships(suppliers, warehouses, products, inventory, orders, shipments)

    raw_tables = {
        "suppliers": suppliers,
        "warehouses": warehouses,
        "products": products,
        "inventory": inventory,
        "orders": orders,
        "shipments": shipments,
    }

    for table_name, rows in raw_tables.items():
        write_csv(config.raw_data_dir / f"{table_name}.csv", rows, RAW_COLUMNS[table_name])
        write_sample(config.sample_data_dir / f"{table_name}_sample.csv", rows, RAW_COLUMNS[table_name])
        LOGGER.info("Wrote %s raw rows for %s", len(rows), table_name)

    cleaned_orders = clean_orders(orders)
    cleaned_shipments = clean_shipments(shipments)
    shipment_analytics = build_shipment_analytics(cleaned_shipments, cleaned_orders, suppliers, warehouses, products)

    processed_tables = {
        "orders_clean": (cleaned_orders, RAW_COLUMNS["orders"]),
        "shipments_clean": (cleaned_shipments, RAW_COLUMNS["shipments"]),
        "shipment_analytics": (shipment_analytics, ANALYTICS_COLUMNS),
    }

    for table_name, (rows, columns) in processed_tables.items():
        write_csv(config.processed_data_dir / f"{table_name}.csv", rows, columns)
        LOGGER.info("Wrote %s processed rows for %s", len(rows), table_name)

    metrics = validate_operational_metrics(cleaned_shipments, min_rows=10_000)
    _write_generation_summary(config.processed_data_dir / "generation_summary.json", metrics)
    LOGGER.info("Generation complete: %s", metrics)


def _write_generation_summary(path: Path, metrics: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)


if __name__ == "__main__":
    main()

