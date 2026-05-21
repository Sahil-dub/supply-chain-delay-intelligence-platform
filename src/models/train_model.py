from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.models.config import ModelConfig
from src.models.features import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    TARGET_COLUMN,
    add_historical_delay_features,
    get_feature_columns,
    prepare_modeling_frame,
)

LOGGER = logging.getLogger(__name__)


def train_delay_models(config: ModelConfig) -> dict[str, object]:
    dataframe = pd.read_csv(config.input_path)
    modeling_frame = prepare_modeling_frame(dataframe)
    train_data, test_data = train_test_split(
        modeling_frame,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=modeling_frame[TARGET_COLUMN],
    )
    train_data, test_data, historical_maps = add_historical_delay_features(train_data, test_data)

    feature_columns = get_feature_columns()
    x_train = train_data[feature_columns]
    y_train = train_data[TARGET_COLUMN]
    x_test = test_data[feature_columns]
    y_test = test_data[TARGET_COLUMN]

    models = {
        "logistic_regression": Pipeline(
            steps=[
                ("preprocessor", _build_preprocessor()),
                (
                    "classifier",
                    LogisticRegression(max_iter=1000, class_weight="balanced", random_state=config.random_state),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocessor", _build_preprocessor()),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=150,
                        max_depth=10,
                        min_samples_leaf=20,
                        class_weight="balanced",
                        random_state=config.random_state,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }

    metrics: dict[str, object] = {
        "dataset": {
            "input_path": str(config.input_path),
            "rows_used": int(len(modeling_frame)),
            "train_rows": int(len(train_data)),
            "test_rows": int(len(test_data)),
            "positive_delay_rate": round(float(modeling_frame[TARGET_COLUMN].mean()), 4),
        },
        "models": {},
        "notes": [
            "Model is a practical portfolio baseline, not a production AI system.",
            "Training uses historical synthetic data and should be recalibrated on real company data.",
            "Actual delivery date, delay days, and delay reason are excluded to avoid target leakage.",
        ],
    }

    trained_models = {}
    for model_name, pipeline in models.items():
        LOGGER.info("Training %s", model_name)
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        probabilities = pipeline.predict_proba(x_test)[:, 1]
        metrics["models"][model_name] = _evaluate_model(y_test, predictions, probabilities)
        trained_models[model_name] = pipeline

    _write_feature_importance(trained_models["random_forest"], config.feature_importance_path)
    _save_model_artifact(
        config.model_path,
        trained_models["random_forest"],
        feature_columns,
        historical_maps,
        threshold=config.delay_threshold,
    )
    _write_json(config.metrics_path, metrics)
    LOGGER.info("Saved model artifact to %s", config.model_path)
    LOGGER.info("Saved metrics to %s", config.metrics_path)

    return metrics


def _build_preprocessor() -> ColumnTransformer:
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
            ("numerical", numerical_pipeline, NUMERICAL_FEATURES),
        ]
    )


def _evaluate_model(y_true: pd.Series, predictions: pd.Series, probabilities: pd.Series) -> dict[str, object]:
    matrix = confusion_matrix(y_true, predictions)
    return {
        "accuracy": round(float(accuracy_score(y_true, predictions)), 4),
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 4),
        "confusion_matrix": {
            "true_negative": int(matrix[0][0]),
            "false_positive": int(matrix[0][1]),
            "false_negative": int(matrix[1][0]),
            "true_positive": int(matrix[1][1]),
        },
    }


def _write_feature_importance(model: Pipeline, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    feature_names = model.named_steps["preprocessor"].get_feature_names_out()
    importances = model.named_steps["classifier"].feature_importances_
    importance_frame = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importances,
        }
    ).sort_values("importance", ascending=False)
    importance_frame.to_csv(output_path, index=False)


def _save_model_artifact(
    output_path: Path,
    model: Pipeline,
    feature_columns: list[str],
    historical_maps: dict[str, object],
    threshold: float,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_columns": feature_columns,
            "historical_maps": historical_maps,
            "threshold": threshold,
        },
        output_path,
    )


def _write_json(output_path: Path, payload: dict[str, object]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train shipment delay-risk models.")
    parser.add_argument("--input-path", default="data/processed/mart_shipment_analytics.csv")
    parser.add_argument("--model-path", default="models/delay_risk_model.joblib")
    parser.add_argument("--metrics-path", default="reports/model_metrics.json")
    parser.add_argument("--feature-importance-path", default="reports/feature_importance.csv")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = ModelConfig(
        input_path=Path(args.input_path),
        model_path=Path(args.model_path),
        metrics_path=Path(args.metrics_path),
        feature_importance_path=Path(args.feature_importance_path),
    )
    train_delay_models(config)


if __name__ == "__main__":
    main()

