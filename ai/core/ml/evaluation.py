"""Shared model evaluation metrics."""

from pathlib import Path
from typing import Any
import json

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)


def evaluate_model(
    model,
    X_test,
    y_test,
    problem_type: str,
    average: str = "weighted",
) -> dict[str, Any]:
    """Evaluate a trained model using classification or regression metrics."""

    if problem_type == "classification":
        return evaluate_classification(model, X_test, y_test, average=average)

    if problem_type == "regression":
        return evaluate_regression(model, X_test, y_test)

    raise ValueError(f"Unsupported problem type: {problem_type}")


def evaluate_classification(
    model,
    X_test,
    y_test,
    average: str = "weighted",
) -> dict[str, Any]:
    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average=average, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average=average, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, average=average, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, zero_division=0, output_dict=True),
    }

    roc_auc = _classification_roc_auc(model, X_test, y_test)
    if roc_auc is not None:
        metrics["roc_auc"] = float(roc_auc)

    return _make_json_safe(metrics)


def evaluate_regression(model, X_test, y_test) -> dict[str, Any]:
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    return _make_json_safe(
        {
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "mse": float(mse),
            "rmse": float(np.sqrt(mse)),
            "r2": float(r2_score(y_test, y_pred)),
        }
    )


def save_metrics(metrics: dict[str, Any], path: str | Path) -> Path:
    """Save metrics as JSON."""

    metrics_path = Path(path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8") as file:
        json.dump(_make_json_safe(metrics), file, indent=4)
    return metrics_path


def _classification_roc_auc(model, X_test, y_test) -> float | None:
    try:
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(X_test)
            if probabilities.ndim == 2 and probabilities.shape[1] == 2:
                return roc_auc_score(y_test, probabilities[:, 1])
            return roc_auc_score(y_test, probabilities, multi_class="ovr", average="weighted")

        if hasattr(model, "decision_function"):
            return roc_auc_score(y_test, model.decision_function(X_test))
    except ValueError:
        return None

    return None


def _make_json_safe(value):
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value
