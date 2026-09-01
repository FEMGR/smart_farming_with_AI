"""Shared model evaluation metrics, confusion matrix, and cross-validation utilities."""

from pathlib import Path
from typing import Any, Optional

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
from sklearn.model_selection import cross_val_score

from ai.core.file_status import write_json_with_status


def evaluate_model(
    model: Any,
    X_test: Any,
    y_test: Any,
    problem_type: str,
    X_train: Optional[Any] = None,
    y_train: Optional[Any] = None,
    cv_folds: int = 5,
    average: str = "weighted",
) -> dict[str, Any]:
    """Evaluate a trained model using test dataset metrics and optional cross-validation."""
    if problem_type == "classification":
        metrics = evaluate_classification(model, X_test, y_test, average=average)
    elif problem_type == "regression":
        metrics = evaluate_regression(model, X_test, y_test)
    else:
        raise ValueError(f"Unsupported problem type: {problem_type}")

    # Attach Cross-Validation results if full training/feature dataset is provided
    if X_train is not None and y_train is not None:
        metrics["cross_validation"] = evaluate_simple_cv(
            model=model,
            X=X_train,
            y=y_train,
            cv=cv_folds,
            scoring="f1_weighted" if problem_type == "classification" else "neg_root_mean_squared_error",
        )

    return _make_json_safe(metrics)


def evaluate_simple_cv(
    model: Any,
    X: Any,
    y: Any,
    cv: int = 5,
    scoring: str = "f1_weighted",  # Use "f1_weighted" or "f1_macro" for multiclass support
) -> dict[str, Any]:
    """Run cross_val_score on a model, print formatted results, and return metrics."""

    # Run cross-validation score
    scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)

    # Convert negative loss metrics back to positive values if applicable
    if scoring.startswith("neg_"):
        scores = -scores

    print(f"\nCross-validation {scoring} scores:")
    print(scores)
    print(f"\nMean {scoring}: {scores.mean():.4f}")
    print(f"Standard deviation: {scores.std():.4f}")

    return {
        "scoring": scoring,
        "scores": scores.tolist(),
        "mean": float(scores.mean()),
        "std": float(scores.std()),
    }


def evaluate_classification(
    model: Any,
    X_test: Any,
    y_test: Any,
    average: str = "weighted",
) -> dict[str, Any]:
    """Compute classification metrics including detailed confusion matrix."""
    y_pred = model.predict(X_test)
    labels = np.unique(np.concatenate((y_test, y_pred)))
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    with np.errstate(divide="ignore", invalid="ignore"):
        cm_percentages = np.nan_to_num((cm / cm.sum(axis=1, keepdims=True)) * 100).round(2)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average=average, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average=average, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, average=average, zero_division=0)),
        "confusion_matrix": {
            "labels": labels.tolist(),
            "matrix": cm.tolist(),
            "percentages": cm_percentages.tolist(),
        },
        "classification_report": classification_report(y_test, y_pred, zero_division=0, output_dict=True),
    }

    roc_auc = _classification_roc_auc(model, X_test, y_test)
    if roc_auc is not None:
        metrics["roc_auc"] = float(roc_auc)

    return _make_json_safe(metrics)


def evaluate_regression(model: Any, X_test: Any, y_test: Any) -> dict[str, Any]:
    """Compute regression metrics."""
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
    return write_json_with_status(
        _make_json_safe(metrics),
        metrics_path,
        description="model metrics",
        indent=4,
    )


def _classification_roc_auc(model: Any, X_test: Any, y_test: Any) -> float | None:
    """Safely calculate ROC-AUC score for binary or multiclass classification."""
    try:
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(X_test)
            if probabilities.ndim == 2 and probabilities.shape[1] == 2:
                return roc_auc_score(y_test, probabilities[:, 1])
            return roc_auc_score(y_test, probabilities, multi_class="ovr", average="weighted")

        if hasattr(model, "decision_function"):
            return roc_auc_score(y_test, model.decision_function(X_test))
    except (ValueError, AttributeError):
        return None

    return None


def _make_json_safe(value: Any) -> Any:
    """Recursively process data to ensure standard Python JSON serializability."""
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
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


def print_evaluation_summary(metrics: dict[str, Any], model_name: str = "Model", problem_type: str = "classification") -> None:
    """Pretty-print evaluation metrics including confusion matrix and cross-validation."""
    print("\n" + "=" * 60)
    print(f"EVALUATION RESULTS: {model_name.upper()}")
    print("=" * 60)

    # 1. Primary Metrics
    print("\n--- Summary Metrics ---")
    if problem_type == "classification":
        print(f"Accuracy  : {metrics.get('accuracy', 0.0):.4f}")
        print(f"Precision : {metrics.get('precision', 0.0):.4f}")
        print(f"Recall    : {metrics.get('recall', 0.0):.4f}")
        print(f"F1 Score  : {metrics.get('f1', 0.0):.4f}")
        if "roc_auc" in metrics:
            print(f"ROC-AUC   : {metrics['roc_auc']:.4f}")
    else:
        print(f"MAE       : {metrics.get('mae', 0.0):.4f}")
        print(f"MSE       : {metrics.get('mse', 0.0):.4f}")
        print(f"RMSE      : {metrics.get('rmse', 0.0):.4f}")
        print(f"R² Score  : {metrics.get('r2', 0.0):.4f}")

    # 2. Confusion Matrix (Classification only)
    if "confusion_matrix" in metrics and isinstance(metrics["confusion_matrix"], dict):
        cm_data = metrics["confusion_matrix"]
        labels = cm_data.get("labels", [])
        cm_matrix = cm_data.get("matrix", [])

        print("\n--- Confusion Matrix ---")
        if labels and cm_matrix:
            # Header
            header = "True \\ Pred | " + " | ".join(f"{str(lbl):^8}" for lbl in labels)
            print(header)
            print("-" * len(header))

            # Matrix Rows
            for idx, row in enumerate(cm_matrix):
                row_str = " | ".join(f"{val:^8d}" for val in row)
                print(f"{str(labels[idx]):^10} | {row_str}")

    # 3. Cross-Validation Scores (if available)
    if "cross_validation" in metrics:
        cv = metrics["cross_validation"]
        scoring = cv.get("scoring", "Metric")
        scores = cv.get("scores", [])
        mean = cv.get("mean", 0.0)
        std = cv.get("std", 0.0)

        print("\n--- Cross-Validation ---")
        print(f"Folds ({len(scores)}) : {[round(s, 4) for s in scores]}")
        print(f"Mean {scoring:<7}: {mean:.4f}")
        print(f"Std Dev     : {std:.4f}")

    print("=" * 60 + "\n")
