# Phase 5: SQL Analytics and KPI Views

## What We Built

Phase 5 adds business-focused PostgreSQL analytics for the Supply Chain Delay Intelligence Platform.

Created files:

- `sql/kpi_views.sql`: reusable views for BI/reporting.
- `sql/analytics_queries.sql`: analyst-style SQL queries for common business questions.

This phase does not create API endpoints, machine learning, or a Power BI dashboard.

## Why This Matters

These SQL files show practical Data Analyst and BI Analyst skills:

- turning normalized operational tables into reporting views
- calculating business KPIs in SQL
- using joins, filters, grouping, window functions, and conditional aggregation
- explaining operational meaning through SQL comments
- preparing reusable views that can feed BI tools later

## Reusable Views

### `vw_shipment_analytics_base`

Shipment-level view that joins:

- shipments
- orders
- suppliers
- warehouses
- products
- inventory

This is the base reporting table for most analysis.

### `vw_delivery_performance_overview`

Executive delivery KPI snapshot:

- total shipments
- delivered shipments
- in-transit shipments
- delayed shipments
- on-time delivery rate
- delayed delivery rate
- average delay days
- total order value

### `vw_supplier_reliability_ranking`

Supplier performance ranking using observed delivery outcomes and supplier reliability score.

Useful for answering:

```text
Which suppliers should operations review first?
```

### `vw_warehouse_bottlenecks`

Warehouse performance view focused on:

- delay rate
- overload flag rate
- average delay days
- capacity risk band

Useful for identifying fulfillment bottlenecks.

### `vw_inventory_stockout_risk`

Inventory risk view classifying product and warehouse combinations as:

- high risk
- medium risk
- low risk

### `vw_monthly_delay_trends`

Monthly performance trend view for seasonal analysis.

### `vw_product_category_delay_analysis`

Category-level delay and stockout analysis.

### `vw_top_delay_reasons`

Delay reason breakdown with share of total delays.

### `vw_high_risk_shipments`

Exception list for shipments that should be reviewed first by an operations analyst.

## Business Questions Covered

The queries in `sql/analytics_queries.sql` answer:

- How healthy is delivery performance overall?
- What is the on-time delivery rate?
- What are the average delay days?
- Which suppliers are least reliable?
- Which warehouses look overloaded?
- Which inventory items show stockout risk?
- Are delays increasing during seasonal peaks?
- Which product categories have the highest delay rate?
- What are the top delay reasons?
- Which shipments should operations review first?

## Terminal Commands

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

Set the connection string:

```powershell
$env:DATABASE_URL="postgresql://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay"
```

Create tables and load data:

```powershell
psql $env:DATABASE_URL -f sql/schema.sql
psql $env:DATABASE_URL -f sql/load_data.sql
psql $env:DATABASE_URL -f sql/indexes.sql
```

Create KPI views:

```powershell
psql $env:DATABASE_URL -f sql/kpi_views.sql
```

Run analytics queries:

```powershell
psql $env:DATABASE_URL -f sql/analytics_queries.sql
```

Run one specific validation query:

```powershell
psql $env:DATABASE_URL -c "SELECT * FROM vw_delivery_performance_overview;"
```

## Expected Output Examples

Based on the cleaned Phase 4 ETL data, the expected overall delivery performance is approximately:

```text
 total_shipments | delivered_shipments | in_transit_shipments | delayed_shipments | on_time_delivery_rate_pct | delayed_delivery_rate_pct | avg_delay_days
----------------+---------------------+----------------------+-------------------+---------------------------+---------------------------+---------------
          12000 |               11243 |                  757 |              4483 |                     60.13 |                     39.87 |          3.03
```

Top delay reasons:

```text
 delay_reason                  | delayed_shipments
------------------------------+------------------
 warehouse_capacity_constraint |              763
 supplier_late_dispatch        |              714
 inventory_shortage            |              656
 carrier_delay                 |              508
 customs_documentation         |              216
```

Example supplier ranking output:

```text
 supplier_id | supplier_name       | delay_rate_pct
-------------+---------------------+---------------
 SUP-011     | Saxon Metals        |         49.07
 SUP-001     | Rhine Components    |         47.89
 SUP-008     | Hanseatic Materials |         46.30
```

## Validation Query Examples

Confirm the base reporting view has one row per shipment:

```sql
SELECT
    (SELECT COUNT(*) FROM shipments) AS shipment_table_rows,
    (SELECT COUNT(*) FROM vw_shipment_analytics_base) AS analytics_base_rows;
```

Expected result:

```text
 shipment_table_rows | analytics_base_rows
--------------------+--------------------
              12000 |              12000
```

Confirm there are no duplicate shipment IDs in the reporting view:

```sql
SELECT
    COUNT(*) AS duplicate_shipment_ids
FROM (
    SELECT shipment_id
    FROM vw_shipment_analytics_base
    GROUP BY shipment_id
    HAVING COUNT(*) > 1
) duplicates;
```

Expected result:

```text
 duplicate_shipment_ids
-----------------------
                     0
```

## Suggested Phase 5 Commits

```text
feat: add reusable KPI views for delivery analytics
feat: add supplier warehouse and inventory SQL analysis
feat: add monthly trend and delay reason queries
feat: add high-risk shipment exception query
docs: document SQL analytics workflow and KPI examples
```

