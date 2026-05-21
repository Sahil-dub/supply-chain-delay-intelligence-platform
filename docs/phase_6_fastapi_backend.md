# Phase 6: FastAPI Backend

## What We Built

Phase 6 adds a modular FastAPI backend for serving supply chain KPIs and SQL analytics results as JSON.

Created backend modules:

- `api/main.py`: FastAPI app factory, route registration, and exception handlers.
- `api/config.py`: environment-based configuration.
- `api/database.py`: SQLAlchemy engine, session management, and database health check.
- `api/schemas.py`: Pydantic response models.
- `api/dependencies.py`: dependency injection for the service layer.
- `api/services/analytics_service.py`: business analytics service methods.
- `api/services/query_helpers.py`: reusable SQL execution helpers.
- `api/routes/health.py`: health check route.
- `api/routes/analytics.py`: KPI and analytics routes.

This phase does not add frontend, dashboard, ML prediction endpoints, authentication, or authorization.

## Architecture

```text
FastAPI route
  -> dependency injection
  -> AnalyticsService
  -> reusable query helper
  -> SQLAlchemy session
  -> PostgreSQL KPI views
  -> JSON response model
```

## Required Database Objects

The API expects the Phase 5 views to exist in PostgreSQL:

- `vw_delivery_performance_overview`
- `vw_monthly_delay_trends`
- `vw_top_delay_reasons`
- `vw_supplier_reliability_ranking`
- `vw_warehouse_bottlenecks`
- `vw_inventory_stockout_risk`
- `vw_high_risk_shipments`

## Endpoints

### `GET /health`

Checks whether the API is running and whether PostgreSQL is reachable.

Example response:

```json
{
  "status": "ok",
  "app_name": "Supply Chain Delay Intelligence Platform",
  "environment": "local",
  "database_connected": true
}
```

### `GET /kpis/overview`

Returns executive delivery KPI metrics.

Example response:

```json
{
  "total_shipments": 12000,
  "delivered_shipments": 11243,
  "in_transit_shipments": 757,
  "delayed_shipments": 4483,
  "on_time_delivery_rate_pct": 60.13,
  "delayed_delivery_rate_pct": 39.87,
  "avg_delivery_variance_days": 0.82,
  "avg_delay_days": 3.03,
  "total_order_value_eur": "2450000.00"
}
```

### `GET /analytics/delay-trends`

Returns monthly delivery and delay trends.

### `GET /analytics/top-delay-reasons`

Returns the most common delay reasons.

Optional query parameter:

```text
limit=10
```

### `GET /analytics/supplier-performance`

Returns supplier delivery performance rankings.

Optional query parameter:

```text
limit=25
```

### `GET /analytics/warehouse-performance`

Returns warehouse bottleneck performance metrics.

### `GET /analytics/inventory-risk`

Returns product and warehouse combinations with medium or high stockout risk.

Optional query parameter:

```text
limit=50
```

### `GET /analytics/high-risk-shipments`

Returns shipments that should be reviewed first by operations.

Optional query parameter:

```text
limit=50
```

## Environment Configuration

The API reads configuration from environment variables or `.env`:

```text
APP_NAME="Supply Chain Delay Intelligence Platform"
APP_ENV=local
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg2://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay
```

## Local Run Instructions

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

Load schema, data, indexes, and KPI views:

```powershell
$env:DATABASE_URL="postgresql://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay"

psql $env:DATABASE_URL -f sql/schema.sql
psql $env:DATABASE_URL -f sql/load_data.sql
psql $env:DATABASE_URL -f sql/indexes.sql
psql $env:DATABASE_URL -f sql/kpi_views.sql
```

Set the SQLAlchemy database URL for FastAPI:

```powershell
$env:DATABASE_URL="postgresql+psycopg2://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay"
```

Run the API locally:

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

Try endpoints:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/kpis/overview
Invoke-RestMethod "http://127.0.0.1:8000/analytics/top-delay-reasons?limit=5"
```

## Testing

Run tests:

```powershell
python -m pytest
```

Run lint checks:

```powershell
ruff check .
```

The API tests use dependency overrides, so they do not require a live PostgreSQL database in CI.

## Expected Test Output

```text
10 passed
All checks passed!
```

## Realistic Commit Sequence

```text
feat: add FastAPI app configuration and database session management
feat: add analytics service layer for KPI views
feat: add health and reporting API routes
test: add FastAPI endpoint tests with service overrides
docs: document backend setup and API examples
```

