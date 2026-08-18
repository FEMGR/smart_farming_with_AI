"""Aggregate model comparison and selection across prediction tasks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
import math
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.core.constants import (  # noqa: E402
    ARTIFACTS_DIR,
    DISEASE_ARTIFACT_DIR,
    DISEASE_MODEL_ORDER,
    DISEASE_MODELS,
    DISEASE_PROBLEM_TYPE,
    DISEASE_TARGET_COLUMN,
    DISEASE_TASK_LABEL,
    DISEASE_TASK_NAME,
    GROWTH_ARTIFACT_DIR,
    GROWTH_MODEL_ORDER,
    GROWTH_MODELS,
    GROWTH_PROBLEM_TYPE,
    GROWTH_TARGET_COLUMN,
    GROWTH_TASK_LABEL,
    GROWTH_TASK_NAME,
    IRRIGATION_ARTIFACT_DIR,
    IRRIGATION_MODEL_ORDER,
    IRRIGATION_MODELS,
    IRRIGATION_PROBLEM_TYPE,
    IRRIGATION_TARGET_COLUMN,
    IRRIGATION_TASK_LABEL,
    IRRIGATION_TASK_NAME,
    YIELD_ARTIFACT_DIR,
    YIELD_MODEL_ORDER,
    YIELD_MODELS,
    YIELD_PROBLEM_TYPE,
    YIELD_TARGET_COLUMN,
    YIELD_TASK_LABEL,
    YIELD_TASK_NAME,
)


MODEL_SELECTION_DIR = ARTIFACTS_DIR / "model_selection"
STANDARDIZED_RESULTS_FILE = MODEL_SELECTION_DIR / "standardized_evaluation_results.json"
STANDARDIZED_RESULTS_CSV = MODEL_SELECTION_DIR / "standardized_evaluation_results.csv"
FEATURE_IMPORTANCE_FILE = MODEL_SELECTION_DIR / "feature_importance_comparison.json"
MODEL_SELECTION_FILE = MODEL_SELECTION_DIR / "model_selection_results.json"


@dataclass(frozen=True)
class TaskComparisonConfig:
    task_name: str
    task_label: str
    artifact_dir: Path
    model_order: tuple[str, ...]
    models: dict[str, dict[str, Any]]
    problem_type: str
    target_column: str


TASKS = (
    TaskComparisonConfig(
        task_name=IRRIGATION_TASK_NAME,
        task_label=IRRIGATION_TASK_LABEL,
        artifact_dir=IRRIGATION_ARTIFACT_DIR,
        model_order=IRRIGATION_MODEL_ORDER,
        models=IRRIGATION_MODELS,
        problem_type=IRRIGATION_PROBLEM_TYPE,
        target_column=IRRIGATION_TARGET_COLUMN,
    ),
    TaskComparisonConfig(
        task_name=GROWTH_TASK_NAME,
        task_label=GROWTH_TASK_LABEL,
        artifact_dir=GROWTH_ARTIFACT_DIR,
        model_order=GROWTH_MODEL_ORDER,
        models=GROWTH_MODELS,
        problem_type=GROWTH_PROBLEM_TYPE,
        target_column=GROWTH_TARGET_COLUMN,
    ),
    TaskComparisonConfig(
        task_name=DISEASE_TASK_NAME,
        task_label=DISEASE_TASK_LABEL,
        artifact_dir=DISEASE_ARTIFACT_DIR,
        model_order=DISEASE_MODEL_ORDER,
        models=DISEASE_MODELS,
        problem_type=DISEASE_PROBLEM_TYPE,
        target_column=DISEASE_TARGET_COLUMN,
    ),
    TaskComparisonConfig(
        task_name=YIELD_TASK_NAME,
        task_label=YIELD_TASK_LABEL,
        artifact_dir=YIELD_ARTIFACT_DIR,
        model_order=YIELD_MODEL_ORDER,
        models=YIELD_MODELS,
        problem_type=YIELD_PROBLEM_TYPE,
        target_column=YIELD_TARGET_COLUMN,
    ),
)


def compare_all_tasks(top_n_features: int = 10) -> dict[str, Any]:
    """Compare saved model artifacts for every configured prediction task."""

    MODEL_SELECTION_DIR.mkdir(parents=True, exist_ok=True)

    standardized_results = []
    feature_importance_results = {}
    selections = []

    for task_config in TASKS:
        task_records = load_task_records(task_config, top_n_features=top_n_features)
        trained_records = [record for record in task_records if record["status"] == "trained"]
        best_record = select_best_record(trained_records)

        standardized_results.extend(task_records)
        feature_importance_results[task_config.task_name] = build_feature_importance_comparison(task_records)
        selections.append(build_selection_record(task_config, task_records, best_record))

    results = {
        "standardized_results": standardized_results,
        "feature_importance": feature_importance_results,
        "model_selection": selections,
    }

    save_json(STANDARDIZED_RESULTS_FILE, standardized_results)
    save_standardized_csv(STANDARDIZED_RESULTS_CSV, standardized_results)
    save_json(FEATURE_IMPORTANCE_FILE, feature_importance_results)
    save_json(MODEL_SELECTION_FILE, selections)

    return results


def load_task_records(
    task_config: TaskComparisonConfig,
    top_n_features: int,
) -> list[dict[str, Any]]:
    """Load standardized model records for one prediction task."""

    records = []
    for rank_order, model_name in enumerate(task_config.model_order):
        model_config = task_config.models[model_name]
        model_dir = task_config.artifact_dir / model_name
        metrics_path = model_dir / "metrics.json"
        metadata_path = model_dir / "metadata.json"
        feature_importance_path = model_dir / "feature_importance.csv"

        if not metrics_path.exists() or not metadata_path.exists():
            records.append(
                build_missing_record(
                    task_config=task_config,
                    model_name=model_name,
                    model_config=model_config,
                    rank_order=rank_order,
                    model_dir=model_dir,
                )
            )
            continue

        metrics = load_json(metrics_path)
        metadata = load_json(metadata_path)
        primary_metric = model_config.get("primary_metric") or metadata.get("primary_metric") or default_primary_metric(task_config.problem_type)
        primary_metric_value = metrics.get(primary_metric)
        feature_importance = load_feature_importance(feature_importance_path, top_n=top_n_features)

        records.append(
            {
                "task": task_config.task_name,
                "task_label": task_config.task_label,
                "model_name": model_name,
                "algorithm": model_config.get("algorithm", metadata.get("algorithm", model_name)),
                "status": "trained",
                "problem_type": metadata.get("problem_type", task_config.problem_type),
                "target": metadata.get("target", task_config.target_column),
                "primary_metric": primary_metric,
                "primary_metric_value": primary_metric_value,
                "greater_is_better": model_config.get("greater_is_better", True),
                "metrics": metrics,
                "feature_importance_available": feature_importance_path.exists(),
                "top_features": feature_importance,
                "artifact_dir": str(model_dir),
                "metrics_path": str(metrics_path),
                "metadata_path": str(metadata_path),
                "feature_importance_path": str(feature_importance_path) if feature_importance_path.exists() else None,
                "rank_order": rank_order,
            }
        )

    return records


def build_missing_record(
    task_config: TaskComparisonConfig,
    model_name: str,
    model_config: dict[str, Any],
    rank_order: int,
    model_dir: Path,
) -> dict[str, Any]:
    """Build a standardized record for a configured model without artifacts."""

    return {
        "task": task_config.task_name,
        "task_label": task_config.task_label,
        "model_name": model_name,
        "algorithm": model_config.get("algorithm", model_name),
        "status": "missing_artifacts",
        "problem_type": task_config.problem_type,
        "target": task_config.target_column,
        "primary_metric": model_config.get("primary_metric") or default_primary_metric(task_config.problem_type),
        "primary_metric_value": None,
        "greater_is_better": model_config.get("greater_is_better", True),
        "metrics": {},
        "feature_importance_available": False,
        "top_features": [],
        "artifact_dir": str(model_dir),
        "metrics_path": str(model_dir / "metrics.json"),
        "metadata_path": str(model_dir / "metadata.json"),
        "feature_importance_path": None,
        "rank_order": rank_order,
    }


def select_best_record(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Select the best trained model record for a task."""

    if not records:
        raise ValueError("Cannot select a best model without trained records.")

    greater_is_better = records[0]["greater_is_better"]
    best_record = records[0]

    for record in records[1:]:
        current_value = record["primary_metric_value"]
        best_value = best_record["primary_metric_value"]
        if current_value is None:
            continue
        if best_value is None:
            best_record = record
            continue

        if greater_is_better and current_value > best_value:
            best_record = record
        elif not greater_is_better and current_value < best_value:
            best_record = record

    return best_record


def build_selection_record(
    task_config: TaskComparisonConfig,
    task_records: list[dict[str, Any]],
    best_record: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact model-selection result for one task."""

    return {
        "task": task_config.task_name,
        "task_label": task_config.task_label,
        "problem_type": task_config.problem_type,
        "target": task_config.target_column,
        "primary_metric": best_record["primary_metric"],
        "greater_is_better": best_record["greater_is_better"],
        "best_model_name": best_record["model_name"],
        "best_algorithm": best_record["algorithm"],
        "best_primary_metric_value": best_record["primary_metric_value"],
        "best_artifact_dir": str(task_config.artifact_dir / "best_model"),
        "selected_model_artifact_dir": best_record["artifact_dir"],
        "models_compared": [
            {
                "model_name": record["model_name"],
                "algorithm": record["algorithm"],
                "status": record["status"],
                "primary_metric": record["primary_metric"],
                "primary_metric_value": record["primary_metric_value"],
                "feature_importance_available": record["feature_importance_available"],
            }
            for record in task_records
        ],
    }


def build_feature_importance_comparison(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare top feature importances for records where they are available."""

    available = [record for record in records if record["feature_importance_available"]]
    top_feature_sets = {record["model_name"]: [feature["feature"] for feature in record["top_features"]] for record in available}
    common_top_features = sorted(set.intersection(*(set(features) for features in top_feature_sets.values()))) if top_feature_sets else []

    return {
        "available_model_count": len(available),
        "models": {
            record["model_name"]: {
                "algorithm": record["algorithm"],
                "feature_importance_path": record["feature_importance_path"],
                "top_features": record["top_features"],
            }
            for record in available
        },
        "models_without_feature_importance": [
            record["model_name"] for record in records if record["status"] == "trained" and not record["feature_importance_available"]
        ],
        "common_top_features": common_top_features,
    }


def load_feature_importance(path: Path, top_n: int) -> list[dict[str, Any]]:
    """Load top feature-importance rows from a CSV artifact."""

    if not path.exists():
        return []

    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    normalized_rows = []
    for row in rows[:top_n]:
        normalized_rows.append(
            {
                "feature": row.get("feature"),
                "importance": parse_float(row.get("importance")),
                "importance_normalized": parse_float(row.get("importance_normalized")),
            }
        )

    return normalized_rows


def save_standardized_csv(path: Path, records: list[dict[str, Any]]) -> Path:
    """Save a flat CSV summary of standardized evaluation results."""

    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "task",
        "model_name",
        "algorithm",
        "status",
        "problem_type",
        "target",
        "primary_metric",
        "primary_metric_value",
        "greater_is_better",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "mae",
        "mse",
        "rmse",
        "r2",
        "feature_importance_available",
        "artifact_dir",
    ]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            metrics = record.get("metrics", {})
            writer.writerow(
                {
                    "task": record["task"],
                    "model_name": record["model_name"],
                    "algorithm": record["algorithm"],
                    "status": record["status"],
                    "problem_type": record["problem_type"],
                    "target": record["target"],
                    "primary_metric": record["primary_metric"],
                    "primary_metric_value": record["primary_metric_value"],
                    "greater_is_better": record["greater_is_better"],
                    "accuracy": metrics.get("accuracy"),
                    "precision": metrics.get("precision"),
                    "recall": metrics.get("recall"),
                    "f1": metrics.get("f1"),
                    "roc_auc": metrics.get("roc_auc"),
                    "mae": metrics.get("mae"),
                    "mse": metrics.get("mse"),
                    "rmse": metrics.get("rmse"),
                    "r2": metrics.get("r2"),
                    "feature_importance_available": record["feature_importance_available"],
                    "artifact_dir": record["artifact_dir"],
                }
            )

    return path


def default_primary_metric(problem_type: str) -> str:
    """Return the default metric used for model selection."""

    if problem_type == "classification":
        return "f1"
    return "rmse"


def load_json(path: Path):
    """Load JSON from disk."""

    with path.open(encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data) -> Path:
    """Save JSON to disk."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(make_json_safe(data), file, indent=4)
    return path


def parse_float(value) -> float | None:
    """Parse a CSV value as float when possible."""

    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def make_json_safe(value):
    """Convert values into strict JSON-safe data."""

    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [make_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [make_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def print_selection_summary(selections: list[dict[str, Any]]) -> None:
    """Print a concise model-selection summary."""

    print("=" * 60)
    print("Model Selection Results")
    print("=" * 60)
    for selection in selections:
        print(f"{selection['task_label']}: " f"{selection['best_algorithm']} " f"({selection['primary_metric']}={selection['best_primary_metric_value']:.4f})")
    print("\nSaved:")
    print(MODEL_SELECTION_FILE)
    print(STANDARDIZED_RESULTS_FILE)
    print(STANDARDIZED_RESULTS_CSV)
    print(FEATURE_IMPORTANCE_FILE)


def main() -> dict[str, Any]:
    """CLI entry point."""

    results = compare_all_tasks()
    print_selection_summary(results["model_selection"])
    return results


if __name__ == "__main__":
    main()
