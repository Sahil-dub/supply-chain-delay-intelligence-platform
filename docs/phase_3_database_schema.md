# Phase 3: PostgreSQL Database Schema

## What We Built

Phase 3 adds the PostgreSQL database layer for the synthetic supply chain datasets created in Phase 2.

Created SQL files:

- `sql/schema.sql`: tables, primary keys, foreign keys, check constraints, and business comments.
- `sql/indexes.sql`: indexes for common analytics query patterns.
- `sql/load_data.sql`: CSV loading commands and validation queries.

This phase intentionally does not add ETL orchestration, API endpoints, machine learning, or dashboards.

## Tables

### `suppliers`

Supplier master data used to analyze supplier reliability and delay risk.

Important columns:

- `supplier_id`: primary key.
- `reliability_score`: synthetic reliability score between 0 and 1.
- `reliability_band`: high, medium, or low reliability group.
- `standard_lead_time_days`: typical supplier lead time.

### `warehouses`

Warehouse master data used to analyze capacity pressure and fulfillment bottlenecks.

Important columns:

- `warehouse_id`: primary key.
- `daily_capacity_units`: expected daily outbound capacity.
- `storage_capacity_units`: approximate inventory storage capacity.
- `overload_risk_band`: low, medium, or high capacity risk.

### `products`

Product master data used for category, supplier, and inventory analysis.

Important columns:

- `product_id`: primary key.
- `primary_supplier_id`: foreign key to `suppliers`.
- `unit_cost_eur`: synthetic unit cost.
- `reorder_point`: stock threshold for replenishment and risk analysis.

### `inventory`

Inventory snapshot by product and warehouse.

Important columns:

- `inventory_id`: primary key.
- `product_id`: foreign key to `products`.
- `warehouse_id`: foreign key to `warehouses`.
- `on_hand_units`: physically available stock.
- `reserved_units`: stock already committed to demand.
- `reorder_point`: threshold for stockout-risk review.

### `orders`

Customer demand records linking products, suppliers, warehouses, and shipment outcomes.

Important columns:

- `order_id`: primary key.
- `product_id`: foreign key to `products`.
- `supplier_id`: foreign key to `suppliers`.
- `warehouse_id`: foreign key to `warehouses`.
- `order_date`: used for trend and seasonality analysis.
- `priority`: standard, expedited, or critical.

### `shipments`

Shipment execution records used for delay KPIs and future prediction labels.

Important columns:

- `shipment_id`: primary key.
- `order_id`: unique foreign key to `orders`.
- `promised_delivery_date`: promised date, sometimes missing in raw data.
- `actual_delivery_date`: delivery date for completed shipments.
- `delay_days`: actual minus promised delivery date.
- `is_delayed`: boolean KPI and model label.
- `delay_reason`: main operational reason for delayed delivered shipments.
- `stockout_flag`: whether available inventory was insufficient.
- `warehouse_overload_flag`: whether capacity pressure was simulated.

## Relationship Model

```mermaid
erDiagram
    SUPPLIERS ||--o{ PRODUCTS : supplies
    SUPPLIERS ||--o{ ORDERS : fulfills
    WAREHOUSES ||--o{ INVENTORY : stores
    WAREHOUSES ||--o{ ORDERS : fulfills_from
    PRODUCTS ||--o{ INVENTORY : stocked_as
    PRODUCTS ||--o{ ORDERS : ordered_as
    ORDERS ||--|| SHIPMENTS : has
```

## Index Strategy

Indexes are added for the analytics questions expected in later phases:

- Supplier performance: `shipments(supplier_id, is_delayed)` and `orders(supplier_id)`.
- Warehouse bottlenecks: `shipments(warehouse_id, is_delayed)` and `orders(warehouse_id)`.
- Product-level delay analysis: `shipments(product_id, is_delayed)` and `orders(product_id)`.
- Monthly trends: `orders(order_date)`, `shipments(promised_delivery_date)`, and `shipments(actual_delivery_date)`.
- Inventory risk: `inventory(warehouse_id, product_id, on_hand_units, reorder_point)`.
- Delay reasons: partial index on `shipments(delay_reason)`.

## Terminal Commands

From the project root, start PostgreSQL:

```powershell
docker compose up -d postgres
```

Set the connection string:

```powershell
$env:DATABASE_URL="postgresql://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay"
```

Create the schema:

```powershell
psql $env:DATABASE_URL -f sql/schema.sql
```

Load generated CSV data:

```powershell
psql $env:DATABASE_URL -f sql/load_data.sql
```

Create indexes:

```powershell
psql $env:DATABASE_URL -f sql/indexes.sql
```

Run a quick validation query:

```powershell
psql $env:DATABASE_URL -c "SELECT COUNT(*) FROM shipments;"
```

## Expected Output Examples

Expected row counts after loading the Phase 2 default dataset:

```text
 table_name | row_count
------------+-----------
 inventory  |      1440
 orders     |     12000
 products   |       180
 shipments  |     12000
 suppliers  |        24
 warehouses |         8
```

Expected relationship validation result:

```text
 check_name                  | invalid_rows
----------------------------+--------------
 inventory_missing_product   |            0
 inventory_missing_warehouse |            0
 orders_missing_product      |            0
 orders_missing_supplier     |            0
 orders_missing_warehouse    |            0
 products_missing_supplier   |            0
 shipments_missing_order     |            0
```

Expected operational validation from the generated dataset:

```text
 delivered_shipments | delayed_percentage | average_delay_days_for_late_shipments
--------------------+--------------------+---------------------------------------
              11243 |              28.23 |                                  3.87
```

The raw shipment file intentionally contains some delay-label inconsistencies so later cleaning work can demonstrate data quality handling. `sql/load_data.sql` surfaces this as a validation query:

```text
 inconsistent_delay_labels
---------------------------
                      1309
```

## Suggested Phase 3 Commits

```text
feat: add PostgreSQL schema for supply chain tables
feat: add foreign keys and business constraints
feat: add CSV loading script with validation queries
perf: add analytics indexes for delay analysis
docs: document database schema and loading workflow
```
