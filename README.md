# Supply Chain Delay Intelligence Platform

**End-to-end supply chain analytics platform for identifying shipment delays, supplier performance issues, warehouse bottlenecks, inventory risk, and shipment delay risk.**\n\n**Live recruiter demo:** https://sahil-dub.github.io/supply-chain-delay-intelligence-platform/

Built with **Python, PostgreSQL, SQL, FastAPI, Power BI, scikit-learn, Docker, and pytest**.

![KPI Overview](assets/screenshots/kpi_overview.png)

## Project at a glance

| Area | Implementation |
|---|---|
| Dataset | 12,000 orders + 12,000 shipments |
| Suppliers | 24 |
| Warehouses | 8 |
| Products | 180 |
| Inventory snapshots | 1,440 |
| Data pipeline | Python ETL + validation |
| Database | PostgreSQL |
| Analytics | SQL KPI views + analytical queries |
| API | FastAPI |
| BI | Power BI |
| Prediction | Logistic Regression + Random Forest |
| Quality | pytest + Ruff + GitHub Actions |
| Local infrastructure | Docker |

## What it does

The platform transforms raw operational data into an analytics layer for logistics and operations teams.

It answers practical questions such as:

- Which suppliers have the weakest delivery performance?
- Which warehouses show bottleneck signals?
- Which products and inventory locations have stockout risk?
- What are the most common shipment delay reasons?
- Which shipments should be reviewed first?
- Can historical operational features help flag shipment delay risk earlier?

## Architecture

```mermaid
flowchart LR
    A["Raw CSV Data"] --> B["Python ETL"]
    B --> C["PostgreSQL"]
    C --> D["SQL Analytics Layer"]
    D --> E["FastAPI"]
    D --> F["Power BI"]
    C --> G["Delay Risk Model"]
    G --> E
```

## Engineering highlights

### Data Engineering

- Built a reproducible synthetic supply-chain dataset covering suppliers, warehouses, products, orders, shipments, and inventory.
- Developed a modular ETL pipeline for validation, cleaning, transformation, and analytics-mart generation.
- Standardized dates, booleans, numeric fields, and categorical values.
- Recalculated delay measures and corrected inconsistent delay labels.
- Produced fact, dimension, and analytics-mart CSV outputs ready for database loading and BI.

### SQL & PostgreSQL

- Designed relational source tables and analytics-ready structures.
- Added reusable KPI views and business-focused SQL queries.
- Analyzed supplier performance, warehouse bottlenecks, inventory risk, delay reasons, and shipment priority.

### API

FastAPI exposes the analytics layer through typed JSON endpoints:

```text
GET /health
GET /kpis/overview
GET /analytics/delay-trends
GET /analytics/top-delay-reasons
GET /analytics/supplier-performance
GET /analytics/warehouse-performance
GET /analytics/inventory-risk
GET /analytics/high-risk-shipments
```

Interactive Swagger documentation is available locally at:

```text
http://127.0.0.1:8000/docs
```

### Power BI

The project includes a Power BI dashboard covering:

- Executive Overview
- Supplier Analytics
- Warehouse Operations
- Shipment Risk Monitoring

Dashboard-ready SQL queries and KPI definitions are included alongside the `.pbix` dashboard file.

### Predictive analytics

The project includes two baseline classifiers:

- Logistic Regression
- Random Forest

The modeling pipeline includes preprocessing, categorical encoding, numerical scaling, historical delay features, train/test evaluation, confusion matrices, ROC-AUC, feature importance, model serialization, and inference.

**Important:** the model is intentionally presented as a portfolio baseline rather than a production AI system. The training data is synthetic, and the current validation results are not strong enough to claim production-level predictive performance.

## Model results

The current held-out test results are:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 57.99% | 47.70% | 55.58% | 51.34% | 0.6079 |
| Random Forest | 58.09% | 47.75% | 53.88% | 50.63% | 0.5960 |

These results are included for transparency. The project treats the model as an experimentation and decision-support component, not as a production-ready predictor.

## Dashboard & API

### KPI Overview

![KPI Overview](assets/screenshots/kpi_overview.png)

### Supplier Performance

![Supplier Performance](assets/screenshots/supplier_performance.png)

### High-Risk Shipments

![High Risk Shipments](assets/screenshots/high_risk_shipments.png)

### Swagger API

![Swagger](assets/screenshots/swagger_overview.png)

### Delay Reasons

![Delay Reasons](assets/screenshots/top_delay_reasons.png)

## Data model

```mermaid
erDiagram
    SUPPLIERS ||--o{ PRODUCTS : supplies
    SUPPLIERS ||--o{ ORDERS : fulfills
    WAREHOUSES ||--o{ INVENTORY : stores
    WAREHOUSES ||--o{ ORDERS : ships_from
    PRODUCTS ||--o{ INVENTORY : stocked_as
    PRODUCTS ||--o{ ORDERS : ordered_as
    ORDERS ||--|| SHIPMENTS : creates
```

## Dataset

The default data generator creates:

- 24 suppliers with different reliability bands.
- 8 German warehouse locations with different capacity-risk profiles.
- 180 products across electronics, packaging, mechanical, textiles, and raw materials.
- 1,440 inventory snapshots.
- 12,000 orders.
- 12,000 shipments.

The synthetic data intentionally contains operational edge cases such as delayed deliveries, missing promised delivery dates, in-transit shipments without actual delivery dates, supplier reliability variation, warehouse overload flags, stockout risk, and seasonal shipment pressure.

The generator uses random seed `42` for reproducibility.

## Data workflow

```text
Configuration
    ↓
Synthetic data generator
    ↓
data/raw/*.csv
    ↓
Validation + transformation
    ↓
data/processed/*.csv
    ↓
PostgreSQL
    ↓
SQL analytics
    ├── FastAPI
    └── Power BI

Shipment analytics mart
    ↓
Delay-risk model
    ↓
Prediction API
```

Generate the data:

```powershell
python -m src.data_generation.generate_data --config src/config/data_generation.json
```

Run the ETL:

```powershell
python -m src.etl.run_etl --raw-dir data/raw --processed-dir data/processed
```

The ETL produces:

```text
dim_suppliers.csv
dim_warehouses.csv
dim_products.csv
fact_inventory.csv
fact_orders.csv
fact_shipments.csv
mart_shipment_analytics.csv
etl_summary.json
```

## Quick start

### 1. Create the environment

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure the environment

```powershell
Copy-Item .env.example .env
```

### 4. Generate the dataset

```powershell
python -m src.data_generation.generate_data --config src/config/data_generation.json
```

### 5. Run the ETL pipeline

```powershell
python -m src.etl.run_etl --raw-dir data/raw --processed-dir data/processed
```

### 6. Start PostgreSQL

```powershell
docker compose up -d postgres
```

### 7. Run the API

```powershell
$env:DATABASE_URL="postgresql+psycopg2://supply_chain_user:supply_chain_password@localhost:5432/supply_chain_delay"
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 8. Run tests and linting

```powershell
pytest
ruff check .
```

## Train the delay-risk model

```powershell
python -m src.models.train_model --input-path data/processed/mart_shipment_analytics.csv --model-path models/delay_risk_model.joblib --metrics-path reports/model_metrics.json --feature-importance-path reports/feature_importance.csv
```

Run an example prediction:

```powershell
python -m src.models.predict_delay_risk --model-path models/delay_risk_model.joblib
```

## Repository structure

```text
.
├── api/                  # FastAPI application, routes, schemas and services
├── assets/screenshots/   # API and analytics screenshots
├── dashboards/           # Power BI dashboard and planning artifacts
├── data/
│   ├── raw/              # Generated/source CSV data
│   ├── processed/        # ETL outputs
│   └── sample/           # Small documentation samples
├── docs/                 # Architecture, schema, API and business documentation
├── notebooks/            # Optional exploration notebooks
├── reports/              # Model metrics and feature importance
├── sql/                  # Schema, KPI views and analytics queries
├── src/
│   ├── config/           # Configuration
│   ├── data_generation/  # Synthetic data generation
│   ├── database/         # Database utilities
│   ├── etl/              # Extraction, validation and transformation
│   ├── features/         # Feature engineering
│   └── models/           # Training and inference
├── tests/                # Automated tests
├── docker-compose.yml    # Local PostgreSQL service
├── requirements.txt      # Python dependencies
└── .github/workflows/    # CI workflow
```

## Quality & reproducibility

The repository includes:

- Unit and integration tests with pytest.
- Ruff linting.
- GitHub Actions for automated lint and test checks.
- Reproducible synthetic data generation using seed `42`.
- Configuration-driven ETL and model training.
- Dockerized PostgreSQL for local development.
- Validation checks for source data and transformations.

## Documentation

Detailed implementation notes remain available in:

- `docs/`
- `dashboards/powerbi_dashboard_plan.md`
- `sql/`
- `reports/`

The repository's commit history documents the progression from project setup through ETL, SQL analytics, API development, dashboard work, testing, and predictive modeling.
