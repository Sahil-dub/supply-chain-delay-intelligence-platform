# Phase 8: Delay-Risk Prediction Model

## What We Built

Phase 8 adds a practical shipment delay-risk modeling layer.

Created files:

- `src/models/config.py`
- `src/models/features.py`
- `src/models/train_model.py`
- `src/models/predict_delay_risk.py`
- `tests/test_model_pipeline.py`
- `models/delay_risk_model.joblib`
- `reports/model_metrics.json`
- `reports/feature_importance.csv`

This phase does not add a FastAPI prediction endpoint, frontend, dashboard, deep learning, or LLM-based modeling.

## Business Goal

The model estimates whether a shipment is likely to be delayed using operational signals that would be available before delivery:

- supplier reliability
- warehouse and overload risk
- product category
- shipment priority
- order quantity and order value
- inventory/stockout risk
- historical delay patterns by supplier, warehouse, and category

The purpose is not to automate decisions. It is to help analysts and operations users prioritize shipments for review.

## Target Variable

The target is:

```text
delayed_flag = 1 when late_delivery_flag is true
delayed_flag = 0 when late_delivery_flag is false
```

Only delivered shipments are used for training because in-transit shipments do not have a final delay outcome.

## Models

Two interpretable baseline models are trained:

- Logistic Regression
- Random Forest Classifier

The saved model artifact uses the Random Forest pipeline because it also provides feature importance. Logistic Regression remains in the metrics file as a transparent baseline comparison.

## Features

Categorical features:

- `customer_region`
- `supplier_id`
- `reliability_band`
- `warehouse_id`
- `overload_risk_band`
- `category`
- `priority`

Numerical features:

- `reliability_score`
- `order_quantity`
- `order_value_eur`
- `stockout_risk_flag`
- `warehouse_overload_flag`
- `order_month`
- `supplier_historical_delay_rate`
- `warehouse_historical_delay_rate`
- `category_historical_delay_rate`

Excluded leakage fields:

- actual delivery date
- delay days
- delay reason
- shipment status as a predictor

## Training Command

```powershell
python -m src.models.train_model `
  --input-path data/processed/mart_shipment_analytics.csv `
  --model-path models/delay_risk_model.joblib `
  --metrics-path reports/model_metrics.json `
  --feature-importance-path reports/feature_importance.csv
```

## Prediction Command

Use the default sample shipment:

```powershell
python -m src.models.predict_delay_risk --model-path models/delay_risk_model.joblib
```

Use a custom JSON shipment:

```powershell
python -m src.models.predict_delay_risk --model-path models/delay_risk_model.joblib --input-json '{"customer_region":"DE-East","supplier_id":"SUP-008","reliability_band":"low","warehouse_id":"WH-001","overload_risk_band":"medium","category":"Textiles","priority":"standard","reliability_score":0.604,"order_quantity":82,"order_value_eur":9776.86,"stockout_risk_flag":0,"warehouse_overload_flag":1,"order_month":3}'
```

## Expected Prediction Output

```json
{
  "delay_risk_probability": 0.6558,
  "delay_risk_label": "likely_delayed",
  "threshold": 0.5
}
```

## Model Metrics

Current metrics are saved in:

```text
reports/model_metrics.json
```

Example metrics from the synthetic dataset:

```json
{
  "logistic_regression": {
    "accuracy": 0.5799,
    "precision": 0.477,
    "recall": 0.5558,
    "f1_score": 0.5134,
    "roc_auc": 0.6079
  },
  "random_forest": {
    "accuracy": 0.5809,
    "precision": 0.4775,
    "recall": 0.5388,
    "f1_score": 0.5063,
    "roc_auc": 0.596
  }
}
```

These are modest baseline results, which is realistic for a synthetic operational dataset with noisy delay behavior.

## Feature Importance

Feature importance is saved in:

```text
reports/feature_importance.csv
```

Top example features:

```text
order_value_eur
order_quantity
supplier_historical_delay_rate
reliability_score
order_month
stockout_risk_flag
warehouse_historical_delay_rate
warehouse_overload_flag
```

## How This Helps Business Users

Operations manager:

- sees which shipments deserve proactive attention
- understands whether risks come from supplier, warehouse, inventory, or order characteristics

Logistics analyst:

- uses probability scores to prioritize exception review
- compares risk drivers through feature importance

Warehouse manager:

- sees whether overload and stockout indicators are linked to delay risk

Business analyst:

- can explain model limitations and avoid overclaiming model performance

## Limitations

- The data is synthetic and should not be treated as real company behavior.
- The model is a baseline decision-support tool, not an automated decision system.
- Historical delay-rate features must be recalculated carefully in production to avoid leakage.
- The model does not know real-world causes such as strikes, weather, traffic, or supplier capacity unless those fields are added.
- Performance should be re-evaluated on real data before using this approach operationally.

## Tests

Run:

```powershell
python -m pytest tests/test_model_pipeline.py
```

Full project checks:

```powershell
python -m pytest
ruff check .
```

## Realistic Commit Sequence

```text
feat: add delay-risk model feature preparation
feat: train logistic regression and random forest baselines
feat: save model metrics and feature importance reports
feat: add single-shipment delay risk prediction script
test: add model pipeline tests
docs: document model limitations and business use cases
```

