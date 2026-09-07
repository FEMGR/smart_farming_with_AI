"""Train, evaluate, compare, and persist yield prediction models."""

# ai/tasks/yield_prediction/train.py

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Callable, Optional

from data_bank.scripts.project_paths import PATHS
from ai.core.tabular.data_loader import load_dataset  # noqa: E402
from ai.core.ml.evaluation import evaluate_model, print_evaluation_summary, save_metrics  # noqa: E402
from ai.core.ml.feature_importance import extract_and_save_feature_importance  # noqa: E402
from ai.core.ml.metadata import create_model_metadata, save_metadata  # noqa: E402
from ai.core.ml.model_io import save_model, save_preprocessing_artifacts  # noqa: E402
from ai.core.tabular.preprocessing import PreprocessingConfig, preprocess_dataset  # noqa: E402
from ai.core.tabular.splitting import SplitConfig  # noqa: E402
from ai.core.ml.training import get_model_params, train_model  # noqa: E402

from ai.models.gradient_boosting import build_model as build_gradient_boosting_model  # noqa: E402
from ai.models.pytorch_mlp import build_model as build_pytorch_mlp_model  # noqa: E402
from ai.tasks.yield_prediction.config import (  # noqa: E402
    ARTIFACT_DIR,
    DATASET_PATH,
    MODEL_ORDER,
    MODELS,
    PROBLEM_TYPE,
    RANDOM_STATE,
    TARGET_CANDIDATES,
    TARGET_COLUMN,
    TASK_LABEL,
    TASK_NAME,
    TEST_SIZE,
)
from ai.core.file_prompter import (
    PROCESSED_DATA_DIR,
    choose_input_file,
    pause_for_user,
    prompt_menu_choice,
)
from ai.core.menu_runner import MenuItem, MenuRunner

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MODEL_BUILDERS = {
    "gradient_boosting": build_gradient_boosting_model,
    "pytorch_mlp": build_pytorch_mlp_model,
}


def prepare_training_data(dataset_path: Path = DATASET_PATH) -> dict[str, Any]:
    """Load yield training dataset (or default) and run shared preprocessing/splitting."""

    print(f"\nLoading dataset: {dataset_path}")
    df = load_dataset(dataset_path, required_columns=[TARGET_COLUMN])
    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    print("\nPreprocessing with shared ML core...")
    data = preprocess_dataset(
        df,
        config=PreprocessingConfig(
            target_column=TARGET_COLUMN,
            target_candidates=TARGET_CANDIDATES,
            problem_type=PROBLEM_TYPE,
        ),
        split_config=SplitConfig(
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=False,
        ),
    )

    print(f"Problem Type : {data['problem_type']}")
    print(f"Target       : {data['target']}")
    print(f"Features     : {len(data['features'])}")

    return data


def train_all_models(dataset_path: Path = DATASET_PATH) -> dict[str, Any]:
    """Train configured yield models and save the best available model."""

    print("=" * 60)
    print(f"{TASK_LABEL} Training")
    print("=" * 60)

    data = prepare_training_data(dataset_path=dataset_path)
    results = []
    skipped_models = []

    for model_name in MODEL_ORDER:
        model_config = MODELS.get(model_name, {})
        if not model_config.get("enabled", True):
            skipped_models.append(skip_model(model_name, model_config))
            continue

        results.append(
            train_and_evaluate_model(
                model_name=model_name,
                data=data,
                dataset_path=dataset_path,
            )
        )

    comparison = compare_models(results, skipped_models)
    best_result = comparison["best_model"]
    best_artifact_dir = save_best_model(best_result)
    comparison["best_artifact_dir"] = str(best_artifact_dir)
    save_comparison(comparison)

    print("\nModel comparison:")
    for result in results:
        metric = result["primary_metric"]
        print(f"- {result['algorithm']}: {metric}={result['primary_metric_value']:.4f}")
    for skipped_model in skipped_models:
        print(f"- {skipped_model['algorithm']}: skipped ({skipped_model['reason']})")

    print("\nBest model:")
    print(f"{best_result['algorithm']} ({best_result['primary_metric']}={best_result['primary_metric_value']:.4f})")
    print(best_artifact_dir)

    return {
        "data": data,
        "results": results,
        "skipped_models": skipped_models,
        "comparison": comparison,
        "best_model": best_result,
    }


def train_selected_model(model_name: str, dataset_path: Path = DATASET_PATH) -> dict[str, Any]:
    """Train and evaluate one configured yield model."""

    data = prepare_training_data(dataset_path=dataset_path)
    model_config = MODELS.get(model_name)
    if model_config is None:
        raise ValueError(f"Unknown yield model: {model_name}")
    if not model_config.get("enabled", True):
        raise ValueError(f"Yield model is not enabled yet: {model_name}")

    return train_and_evaluate_model(model_name, data, dataset_path=dataset_path)


def train_and_evaluate_model(
    model_name: str,
    data: dict[str, Any],
    dataset_path: Path = DATASET_PATH,
) -> dict[str, Any]:
    """Train, evaluate, and save one yield model."""

    if model_name not in MODELS:
        raise ValueError(f"Unknown yield model: {model_name}")
    if model_name not in MODEL_BUILDERS:
        raise ValueError(f"No model builder registered for: {model_name}")

    model_config = MODELS[model_name]
    algorithm = model_config["algorithm"]
    artifact_dir = ARTIFACT_DIR / model_name
    artifact_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "-" * 60)
    print(f"Training {algorithm}")
    print("-" * 60)

    model = MODEL_BUILDERS[model_name](
        data["problem_type"],
        params=model_config.get("params"),
    )
    training_result = train_model(
        model,
        data["X_train"],
        data["y_train"],
    )

    metrics = evaluate_model(
        training_result.model,
        data["X_test"],
        data["y_test"],
        data["problem_type"],
        X_train=data["X_train"],
        y_train=data["y_train"],
    )

    print_evaluation_summary(
        metrics,
        model_name=algorithm,
        problem_type=data["problem_type"],
    )

    primary_metric = select_primary_metric(data["problem_type"], model_config)
    primary_metric_value = metrics[primary_metric]

    model_path = save_model(training_result.model, artifact_dir / "model.pkl")
    preprocessing_path = save_preprocessing_artifacts(data["artifacts"], artifact_dir / "preprocessing.pkl")
    metrics_path = save_metrics(metrics, artifact_dir / "metrics.json")

    feature_importance_path = None
    try:
        feature_importance_path = extract_and_save_feature_importance(
            training_result.model,
            data["features"],
            artifact_dir / "feature_importance.csv",
        )
    except ValueError:
        feature_importance_path = None

    metadata = create_model_metadata(
        task_name=TASK_NAME,
        algorithm=algorithm,
        problem_type=data["problem_type"],
        target_column=data["target"],
        feature_columns=data["features"],
        training_rows=len(data["X_train"]),
        test_rows=len(data["X_test"]),
        model_params=get_model_params(training_result.model),
        preprocessing_config=data["artifacts"].config,
        metrics=metrics,
        extra={
            "model_name": model_name,
            "dataset": str(dataset_path),
            "primary_metric": primary_metric,
            "primary_metric_value": primary_metric_value,
            "training": {
                "started_at": training_result.started_at,
                "finished_at": training_result.finished_at,
                "duration_seconds": training_result.duration_seconds,
            },
        },
    )
    metadata_path = save_metadata(metadata, artifact_dir / "metadata.json")

    print(f"Artifacts saved to: {artifact_dir}")

    return {
        "model_name": model_name,
        "algorithm": algorithm,
        "model": training_result.model,
        "artifact_dir": artifact_dir,
        "model_path": model_path,
        "preprocessing_path": preprocessing_path,
        "metrics_path": metrics_path,
        "metadata_path": metadata_path,
        "feature_importance_path": feature_importance_path,
        "metrics": metrics,
        "primary_metric": primary_metric,
        "primary_metric_value": primary_metric_value,
        "greater_is_better": model_config.get("greater_is_better", True),
    }


def skip_model(model_name: str, model_config: dict[str, Any]) -> dict[str, Any]:
    """Record a model that is configured but not ready to train yet."""

    return {
        "model_name": model_name,
        "algorithm": model_config.get("algorithm", model_name),
        "status": model_config.get("status", "skipped"),
        "reason": model_config.get("reason", "Model is disabled in task configuration."),
    }


def compare_models(
    results: list[dict[str, Any]],
    skipped_models: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compare trained model metrics and include skipped future models."""

    if not results:
        raise ValueError("No trained yield model results to compare.")

    greater_is_better = results[0]["greater_is_better"]
    best_result = sorted(
        results,
        key=lambda result: result["primary_metric_value"],
        reverse=greater_is_better,
    )[0]

    return {
        "task": TASK_NAME,
        "primary_metric": best_result["primary_metric"],
        "greater_is_better": greater_is_better,
        "best_model_name": best_result["model_name"],
        "best_algorithm": best_result["algorithm"],
        "best_model": best_result,
        "models": [
            {
                "model_name": result["model_name"],
                "algorithm": result["algorithm"],
                "primary_metric": result["primary_metric"],
                "primary_metric_value": result["primary_metric_value"],
                "metrics": result["metrics"],
                "artifact_dir": str(result["artifact_dir"]),
            }
            for result in results
        ],
        "skipped_models": skipped_models or [],
    }


def save_best_model(best_result: dict[str, Any]) -> Path:
    """Save a stable copy of the best yield model and its artifacts."""

    best_dir = ARTIFACT_DIR / "best_model"
    best_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(best_result["model_path"], best_dir / "model.pkl")
    shutil.copy2(best_result["preprocessing_path"], best_dir / "preprocessing.pkl")
    shutil.copy2(best_result["metadata_path"], best_dir / "metadata.json")
    shutil.copy2(best_result["metrics_path"], best_dir / "metrics.json")

    if best_result["feature_importance_path"] is not None:
        shutil.copy2(best_result["feature_importance_path"], best_dir / "feature_importance.csv")

    return best_dir


def save_comparison(comparison: dict[str, Any]) -> Path:
    """Save a JSON comparison without unserializable fitted model objects."""

    comparison_path = ARTIFACT_DIR / "model_comparison.json"
    comparison_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {key: value for key, value in comparison.items() if key != "best_model"}
    with comparison_path.open("w", encoding="utf-8") as file:
        json.dump(_make_json_safe(serializable), file, indent=4)
    return comparison_path


def select_primary_metric(problem_type: str, model_config: dict[str, Any]) -> str:
    """Resolve the metric used to select the best model."""

    configured_metric = model_config.get("primary_metric")
    if configured_metric:
        return configured_metric

    if problem_type == "classification":
        return "f1"

    return "rmse"


def _make_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


# =========================================================
# MENU & WORKFLOW DRIVER
# =========================================================


def train_using_custom_data(dry_run: bool = False, interactive: bool = True) -> Optional[dict[str, Any]]:
    """
    Prompt user to select a dataset file via file_prompter and run yield model training.
    """
    if dry_run:
        print("[DRY RUN] Would prompt for a custom dataset file and run yield model training.")
        return None

    try:
        input_file = choose_input_file(directory=PROCESSED_DATA_DIR)
    except KeyboardInterrupt:
        print("\nFile selection cancelled.")
        return None
    except (FileNotFoundError, FileExistsError) as error:
        print(f"\nError: {error}")
        return None

    print(f"\nSelected Input File: {input_file}")
    return train_all_models(dataset_path=input_file)


def train_using_default_data(dry_run: bool = False, interactive: bool = True) -> Optional[dict[str, Any]]:
    """
    Run yield model training using default dataset path.
    """
    if dry_run:
        print(f"[DRY RUN] Would train yield models using default dataset: {DATASET_PATH}")
        return None

    if not DATASET_PATH.exists():
        print(f"\nError: Default dataset file not found: {DATASET_PATH}")
        return None

    return train_all_models(dataset_path=DATASET_PATH)


def interactive_loop(dry_run: bool = False) -> None:
    PATHS.ensure_dirs()

    menu = MenuRunner(
        title="Yield Training Menu",
        items=[
            MenuItem(
                key="1",
                label="Train using custom file (using file_prompter)",
                action=train_using_custom_data,
            ),
            MenuItem(
                key="2",
                label="Train using default dataset",
                action=train_using_default_data,
            ),
            MenuItem(
                key="0",
                label="Exit",
                action=lambda dry_run: None,
            ),
        ],
        prompt_func=prompt_menu_choice,
        pause_func=pause_for_user,
        notes=[
            "Option 1 lets you pick a specific dataset file for training.",
            "Option 2 trains models using the default dataset file.",
        ],
    )

    menu.run(dry_run=dry_run)


def run_non_interactive(command: str, dry_run: bool = False) -> None:
    shortcuts: dict[str, Callable[[bool], None]] = {
        "custom": lambda dry_run: train_using_custom_data(dry_run=dry_run, interactive=False),
        "default": lambda dry_run: train_using_default_data(dry_run=dry_run, interactive=False),
    }

    action = shortcuts.get(command)

    if not action:
        print(f"Unknown command: {command}")
        print("")
        print("Available commands:")
        for key in shortcuts:
            print(f" - {key}")
        sys.exit(1)

    PATHS.ensure_dirs()
    action(dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive manager for Yield Model Training")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them where supported.",
    )

    parser.add_argument(
        "--command",
        choices=[
            "custom",
            "default",
        ],
        help="Run a workflow directly without opening the menu.",
    )

    args = parser.parse_args()

    if args.command:
        run_non_interactive(args.command, dry_run=args.dry_run)
    else:
        interactive_loop(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
