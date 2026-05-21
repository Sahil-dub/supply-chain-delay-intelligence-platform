# Phase 4: ETL Pipeline

## What We Built

Phase 4 adds a modular CSV-based ETL pipeline that prepares analytics-ready tables for later PostgreSQL loading and BI work.

Created ETL modules:

- `src/etl/config.py`: filesystem configuration for raw and processed data paths.
- `src/etl/extract.py`: reads raw Phase 2 CSVs and existing processed files for lineage checks.
- `src/etl/schemas.py`: required columns, date columns, boolean columns, and numeric validation rules.
- `src/etl/validation.py`: reusable schema, key, relationship, and data quality validation functions.
- `src/etl/transform.py`: standardizes values, fixes delay labels, and builds analytics tables.
- `src/etl/load.py`: writes cleaned outputs and summary JSON files.
- `src/etl/run_etl.py`: command-line entry point for the pipeline.

This phase does not create API endpoints, machine learning, or dashboards.

## Why This Matters

This phase demonstrates practical data engineering skills:

- Validating source files before transformation.
- Checking primary-key uniqueness and foreign-key relationships.
- Standardizing dates, booleans, and categorical values.
- Correcting inconsistent business labels using reliable date logic.
- Creating analytics-ready fact, dimension, and mart-style CSV outputs.
- Adding tests for reusable validation logic.

## Input Files

The ETL reads raw CSV files from `data/raw/`:

- `suppliers.csv`
- `warehouses.csv`
- `products.csv`
- `inventory.csv`
- `orders.csv`
- `shipments.csv`

It also reads existing Phase 2 processed files from `data/processed/` when present:

- `orders_clean.csv`
- `shipments_clean.csv`
- `shipment_analytics.csv`

Those processed files are used as optional lineage inputs. The ETL still treats `data/raw/` as the primary source of truth.

## Output Files

The ETL writes PostgreSQL-friendly analytics outputs to `data/processed/`:

- `dim_suppliers.csv`
- `dim_warehouses.csv`
- `dim_products.csv`
- `fact_inventory.csv`
- `fact_orders.csv`
- `fact_shipments.csv`
- `mart_shipment_analytics.csv`
- `etl_summary.json`

## Key Cleaning Rules

### Delay Label Correction

Raw shipment data can contain inconsistent labels where `is_delayed` does not match the actual delivery timing.

The ETL recalculates:

```text
delay_days = actual_delivery_date - promised_delivery_date
is_delayed = delay_days > 0
```

This reduced inconsistent delay labels from `1309` to `0` in the default dataset.

### Date Standardization

The ETL parses date columns as dates:

- `order_date`
- `ship_date`
- `promised_delivery_date`
- `actual_delivery_date`
- `last_stock_count_date`

### Categorical Standardization

The ETL standardizes operational categories such as:

- supplier reliability bands
- warehouse overload risk bands
- shipment status
- order priority
- order status
- delay reasons

### Relationship Validation

The ETL checks that:

- products reference valid suppliers
- inventory references valid products and warehouses
- orders reference valid products, suppliers, and warehouses
- shipments reference valid orders, products, suppliers, and warehouses

## Terminal Commands

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the ETL pipeline:

```powershell
python -m src.etl.run_etl --raw-dir data/raw --processed-dir data/processed
```

Run tests:

```powershell
python -m pytest
```

Run lint checks:

```powershell
ruff check .
```

## Expected Output Example

```text
INFO Starting ETL pipeline
INFO Read 12000 rows from data\raw\orders.csv
INFO Read 12000 rows from data\raw\shipments.csv
INFO ETL transformation summary: {'inconsistent_delay_labels_before': 1309, 'inconsistent_delay_labels_after': 0, 'fact_orders_rows': 12000, 'fact_shipments_rows': 12000, 'mart_shipment_analytics_rows': 12000}
INFO Wrote 12000 rows to data\processed\fact_orders.csv
INFO Wrote 12000 rows to data\processed\fact_shipments.csv
INFO Wrote 12000 rows to data\processed\mart_shipment_analytics.csv
INFO ETL pipeline completed successfully
```

Expected `etl_summary.json`:

```json
{
  "inconsistent_delay_labels_before": 1309,
  "inconsistent_delay_labels_after": 0,
  "fact_orders_rows": 12000,
  "fact_shipments_rows": 12000,
  "mart_shipment_analytics_rows": 12000
}
```

## Suggested Phase 4 Commits

```text
feat: add modular CSV extraction for ETL pipeline
feat: validate source schemas keys and relationships
fix: correct inconsistent shipment delay labels
feat: create analytics-ready fact dimension and mart outputs
test: add ETL validation tests
docs: document ETL workflow and expected outputs
```

