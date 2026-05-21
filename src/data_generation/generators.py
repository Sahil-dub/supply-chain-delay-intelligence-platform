from __future__ import annotations

import random
from datetime import date, datetime, timedelta

from src.data_generation.config import GenerationConfig

SUPPLIER_NAMES = [
    "Rhine Components",
    "Baltic Packaging",
    "Alpine Industrial Parts",
    "Nordic Freight Supplies",
    "Main River Electronics",
    "Elbe Manufacturing",
    "Danube Tools",
    "Hanseatic Materials",
    "Ruhr Mechanical",
    "Black Forest Plastics",
    "Saxon Metals",
    "Bavaria Textile Group",
]

WAREHOUSE_CITIES = [
    ("Berlin", "BE"),
    ("Hamburg", "HH"),
    ("Munich", "BY"),
    ("Cologne", "NW"),
    ("Frankfurt", "HE"),
    ("Leipzig", "SN"),
    ("Stuttgart", "BW"),
    ("Dortmund", "NW"),
]

PRODUCT_CATEGORIES = {
    "Electronics": ["Sensor", "Controller", "Cable", "Scanner"],
    "Packaging": ["Carton", "Pallet Wrap", "Label Roll", "Foam Insert"],
    "Mechanical": ["Bearing", "Bracket", "Valve", "Gear"],
    "Textiles": ["Work Gloves", "Safety Vest", "Strap", "Cover Sheet"],
    "Raw Materials": ["Steel Sheet", "Plastic Resin", "Aluminium Rod", "Rubber Seal"],
}

DELAY_REASONS = [
    "supplier_late_dispatch",
    "warehouse_capacity_constraint",
    "carrier_delay",
    "inventory_shortage",
    "customs_documentation",
    "weather_disruption",
    "quality_hold",
]

COUNTRIES = ["Germany", "Poland", "Czech Republic", "Netherlands", "Italy", "France"]
CUSTOMER_REGIONS = ["DE-North", "DE-South", "DE-West", "DE-East", "DE-Central"]


def generate_suppliers(config: GenerationConfig, rng: random.Random) -> list[dict[str, object]]:
    suppliers = []
    reliability_bands = ["high", "medium", "low"]
    band_weights = [0.45, 0.4, 0.15]

    for index in range(1, config.num_suppliers + 1):
        band = rng.choices(reliability_bands, weights=band_weights, k=1)[0]
        if band == "high":
            reliability_score = round(rng.uniform(0.88, 0.98), 3)
        elif band == "medium":
            reliability_score = round(rng.uniform(0.72, 0.87), 3)
        else:
            reliability_score = round(rng.uniform(0.55, 0.71), 3)

        suppliers.append(
            {
                "supplier_id": f"SUP-{index:03d}",
                "supplier_name": SUPPLIER_NAMES[(index - 1) % len(SUPPLIER_NAMES)],
                "country": rng.choice(COUNTRIES),
                # Business meaning: expected supplier consistency before shipment execution.
                "reliability_score": reliability_score,
                "reliability_band": band,
                "standard_lead_time_days": rng.randint(2, 12),
                "active_flag": True,
            }
        )

    return suppliers


def generate_warehouses(config: GenerationConfig, rng: random.Random) -> list[dict[str, object]]:
    warehouses = []

    for index in range(1, config.num_warehouses + 1):
        city, state = WAREHOUSE_CITIES[(index - 1) % len(WAREHOUSE_CITIES)]
        capacity = rng.randint(650, 1800)
        warehouses.append(
            {
                "warehouse_id": f"WH-{index:03d}",
                "warehouse_name": f"{city} Distribution Center",
                "city": city,
                "state": state,
                # Business meaning: maximum daily outbound shipment volume before bottlenecks increase.
                "daily_capacity_units": capacity,
                "storage_capacity_units": capacity * rng.randint(18, 35),
                "overload_risk_band": rng.choices(["low", "medium", "high"], weights=[0.35, 0.45, 0.2], k=1)[0],
            }
        )

    return warehouses


def generate_products(
    config: GenerationConfig,
    rng: random.Random,
    suppliers: list[dict[str, object]],
) -> list[dict[str, object]]:
    products = []
    categories = list(PRODUCT_CATEGORIES.keys())

    for index in range(1, config.num_products + 1):
        category = rng.choice(categories)
        base_name = rng.choice(PRODUCT_CATEGORIES[category])
        unit_cost = round(rng.uniform(3.5, 450.0), 2)
        products.append(
            {
                "product_id": f"PRD-{index:04d}",
                "product_name": f"{base_name} {index:04d}",
                "category": category,
                "primary_supplier_id": rng.choice(suppliers)["supplier_id"],
                "unit_cost_eur": unit_cost,
                # Business meaning: minimum inventory level before a stockout warning is raised.
                "reorder_point": rng.randint(40, 450),
                "hazmat_flag": category == "Raw Materials" and rng.random() < 0.08,
            }
        )

    return products


def generate_inventory(
    products: list[dict[str, object]],
    warehouses: list[dict[str, object]],
    rng: random.Random,
) -> list[dict[str, object]]:
    inventory = []

    for product in products:
        for warehouse in warehouses:
            reorder_point = int(product["reorder_point"])
            shortage_pressure = rng.random()
            if shortage_pressure < 0.12:
                on_hand = rng.randint(0, max(1, reorder_point - 1))
            else:
                on_hand = rng.randint(reorder_point, reorder_point * rng.randint(2, 7))

            inventory.append(
                {
                    "inventory_id": f"INV-{product['product_id']}-{warehouse['warehouse_id']}",
                    "product_id": product["product_id"],
                    "warehouse_id": warehouse["warehouse_id"],
                    # Business meaning: units physically available at the warehouse snapshot date.
                    "on_hand_units": on_hand,
                    "reserved_units": rng.randint(0, max(1, int(on_hand * 0.35))),
                    "reorder_point": reorder_point,
                    "last_stock_count_date": _random_date(date(2025, 12, 1), date(2026, 1, 31), rng).isoformat(),
                }
            )

    return inventory


def generate_orders_and_shipments(
    config: GenerationConfig,
    suppliers: list[dict[str, object]],
    warehouses: list[dict[str, object]],
    products: list[dict[str, object]],
    inventory: list[dict[str, object]],
    rng: random.Random,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    start = datetime.strptime(config.start_date, "%Y-%m-%d").date()
    end = datetime.strptime(config.end_date, "%Y-%m-%d").date()
    inventory_lookup = {(row["product_id"], row["warehouse_id"]): row for row in inventory}
    supplier_lookup = {row["supplier_id"]: row for row in suppliers}
    product_lookup = {row["product_id"]: row for row in products}

    orders = []
    shipments = []

    for index in range(1, config.num_orders + 1):
        product = rng.choice(products)
        supplier = supplier_lookup[str(product["primary_supplier_id"])]
        warehouse = rng.choice(warehouses)
        order_date = _seasonal_order_date(start, end, rng)
        quantity = _order_quantity(product["category"], rng)
        priority = rng.choices(["standard", "expedited", "critical"], weights=[0.72, 0.22, 0.06], k=1)[0]
        promised_date = order_date + timedelta(days=int(supplier["standard_lead_time_days"]) + rng.randint(1, 5))

        inventory_row = inventory_lookup[(product["product_id"], warehouse["warehouse_id"])]
        stockout_flag = int(inventory_row["on_hand_units"]) < quantity
        overload_flag = _is_warehouse_overloaded(warehouse, order_date, rng)
        delay_probability = _delay_probability(supplier, warehouse, stockout_flag, overload_flag, order_date)
        delayed = rng.random() < delay_probability

        if delayed:
            delay_days = rng.choices([1, 2, 3, 4, 5, 6, 7, 10, 14], weights=[18, 20, 18, 14, 10, 7, 6, 4, 3], k=1)[0]
            delay_reason = _delay_reason(stockout_flag, overload_flag, supplier, rng)
        else:
            delay_days = rng.choice([-2, -1, 0, 0, 0, 1])
            delay_reason = ""

        actual_delivery_date = promised_date + timedelta(days=delay_days)
        shipment_status = rng.choices(["delivered", "in_transit"], weights=[0.94, 0.06], k=1)[0]
        if shipment_status == "in_transit":
            actual_delivery_value = ""
        else:
            actual_delivery_value = actual_delivery_date.isoformat()

        # A small missing-date rate gives later cleaning logic something realistic to handle.
        promised_value = "" if rng.random() < 0.012 else promised_date.isoformat()

        order_id = f"ORD-{index:06d}"
        shipment_id = f"SHP-{index:06d}"
        unit_cost = float(product_lookup[product["product_id"]]["unit_cost_eur"])

        orders.append(
            {
                "order_id": order_id,
                "customer_region": rng.choice(CUSTOMER_REGIONS),
                "product_id": product["product_id"],
                "supplier_id": supplier["supplier_id"],
                "warehouse_id": warehouse["warehouse_id"],
                "order_date": order_date.isoformat(),
                "order_quantity": quantity,
                "order_value_eur": round(quantity * unit_cost, 2),
                "priority": priority,
                "order_status": "open" if shipment_status == "in_transit" else "fulfilled",
            }
        )

        shipments.append(
            {
                "shipment_id": shipment_id,
                "order_id": order_id,
                "supplier_id": supplier["supplier_id"],
                "warehouse_id": warehouse["warehouse_id"],
                "product_id": product["product_id"],
                "ship_date": (order_date + timedelta(days=rng.randint(0, 3))).isoformat(),
                "promised_delivery_date": promised_value,
                "actual_delivery_date": actual_delivery_value,
                # Business meaning: numeric delay outcome used for KPIs and future model labels.
                "delay_days": delay_days if actual_delivery_value else "",
                "is_delayed": delayed if actual_delivery_value else "",
                "delay_reason": delay_reason if actual_delivery_value else "",
                "carrier": rng.choice(["DHL Freight", "DB Schenker", "Kuehne+Nagel", "DPD", "UPS"]),
                "shipment_status": shipment_status,
                "stockout_flag": stockout_flag,
                "warehouse_overload_flag": overload_flag,
            }
        )

    return orders, shipments


def _random_date(start: date, end: date, rng: random.Random) -> date:
    return start + timedelta(days=rng.randint(0, (end - start).days))


def _seasonal_order_date(start: date, end: date, rng: random.Random) -> date:
    """Generate more orders during Q4 and month-end, matching common logistics peaks."""

    while True:
        candidate = _random_date(start, end, rng)
        q4_multiplier = 2.1 if candidate.month in {10, 11, 12} else 1.0
        month_end_multiplier = 1.35 if candidate.day >= 24 else 1.0
        if rng.random() < min(1.0, 0.38 * q4_multiplier * month_end_multiplier):
            return candidate


def _order_quantity(category: str, rng: random.Random) -> int:
    if category == "Packaging":
        return rng.randint(50, 1200)
    if category == "Raw Materials":
        return rng.randint(20, 500)
    if category == "Electronics":
        return rng.randint(5, 160)
    return rng.randint(10, 350)


def _is_warehouse_overloaded(warehouse: dict[str, object], order_date: date, rng: random.Random) -> bool:
    base_risk = {"low": 0.08, "medium": 0.18, "high": 0.34}[str(warehouse["overload_risk_band"])]
    seasonal_pressure = 0.14 if order_date.month in {10, 11, 12} else 0.0
    return rng.random() < base_risk + seasonal_pressure


def _delay_probability(
    supplier: dict[str, object],
    warehouse: dict[str, object],
    stockout_flag: bool,
    overload_flag: bool,
    order_date: date,
) -> float:
    supplier_risk = 1.0 - float(supplier["reliability_score"])
    warehouse_risk = {"low": 0.02, "medium": 0.06, "high": 0.11}[str(warehouse["overload_risk_band"])]
    seasonal_risk = 0.05 if order_date.month in {10, 11, 12} else 0.0
    risk = 0.05 + supplier_risk * 0.55 + warehouse_risk + seasonal_risk

    if stockout_flag:
        risk += 0.16
    if overload_flag:
        risk += 0.12

    return min(0.65, risk)


def _delay_reason(
    stockout_flag: bool,
    overload_flag: bool,
    supplier: dict[str, object],
    rng: random.Random,
) -> str:
    reasons = DELAY_REASONS.copy()
    weights = [18, 16, 16, 12, 7, 6, 5]

    if stockout_flag:
        weights[reasons.index("inventory_shortage")] += 35
    if overload_flag:
        weights[reasons.index("warehouse_capacity_constraint")] += 35
    if str(supplier["reliability_band"]) == "low":
        weights[reasons.index("supplier_late_dispatch")] += 25

    return rng.choices(reasons, weights=weights, k=1)[0]
