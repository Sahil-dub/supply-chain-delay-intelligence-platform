import random

from src.data_generation.config import GenerationConfig
from src.data_generation.generators import (
    generate_inventory,
    generate_orders_and_shipments,
    generate_products,
    generate_suppliers,
    generate_warehouses,
)
from src.data_generation.validation import validate_operational_metrics, validate_relationships


def test_generated_tables_have_valid_relationships(tmp_path) -> None:
    config = GenerationConfig(
        seed=7,
        num_suppliers=6,
        num_warehouses=3,
        num_products=20,
        num_orders=250,
        start_date="2025-01-01",
        end_date="2025-12-31",
        raw_data_dir=tmp_path / "raw",
        processed_data_dir=tmp_path / "processed",
        sample_data_dir=tmp_path / "sample",
    )
    rng = random.Random(config.seed)

    suppliers = generate_suppliers(config, rng)
    warehouses = generate_warehouses(config, rng)
    products = generate_products(config, rng, suppliers)
    inventory = generate_inventory(products, warehouses, rng)
    orders, shipments = generate_orders_and_shipments(config, suppliers, warehouses, products, inventory, rng)

    validate_relationships(suppliers, warehouses, products, inventory, orders, shipments)


def test_generated_delay_rate_stays_realistic(tmp_path) -> None:
    config = GenerationConfig(
        seed=42,
        num_suppliers=8,
        num_warehouses=4,
        num_products=30,
        num_orders=1000,
        start_date="2025-01-01",
        end_date="2025-12-31",
        raw_data_dir=tmp_path / "raw",
        processed_data_dir=tmp_path / "processed",
        sample_data_dir=tmp_path / "sample",
    )
    rng = random.Random(config.seed)

    suppliers = generate_suppliers(config, rng)
    warehouses = generate_warehouses(config, rng)
    products = generate_products(config, rng, suppliers)
    inventory = generate_inventory(products, warehouses, rng)
    _, shipments = generate_orders_and_shipments(config, suppliers, warehouses, products, inventory, rng)

    metrics = validate_operational_metrics(shipments, min_rows=1000)

    assert 0.15 <= metrics["delay_rate"] <= 0.55
