"""Train, evaluate, compare, and persist Computer Vision plant identification models."""

# ai/tasks/plant_identification/train.py

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Optional, Dict

from ai.core.file_prompter import (
    pause_for_user,
    prompt_menu_choice,
)
from ai.core.file_status import write_json_with_status
from ai.core.menu_runner import MenuItem, MenuRunner
from ai.core.vision.dataset import create_dataloaders
from ai.core.vision.training import VisionTrainingConfig, train_vision_model
from ai.models.vision import build_custom_cnn, build_resnet, build_vit

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Task Configurations
DEFAULT_DATA_DIR = PROJECT_ROOT / "ai" / "datasets" / "raw" / "image" / "PlantLeafImageDataset"
ARTIFACT_DIR = PROJECT_ROOT / "ai" / "artifacts" / "plant_identification"
TASK_NAME = "plant_identification"
TASK_LABEL = "Plant Species Identification Vision Pipeline"

# Registered vision models and default enablement
VISION_MODELS = {
    "resnet18": {
        "algorithm": "ResNet-18",
        "builder": lambda num_classes: build_resnet(num_classes=num_classes, variant="resnet18", pretrained=True),
        "enabled": True,
        "primary_metric": "val_acc",
        "greater_is_better": True,
    },
    "resnet50": {
        "algorithm": "ResNet-50",
        "builder": lambda num_classes: build_resnet(num_classes=num_classes, variant="resnet50", pretrained=True),
        "enabled": True,
        "primary_metric": "val_acc",
        "greater_is_better": True,
    },
    "custom_cnn": {
        "algorithm": "Custom PlantCNN",
        "builder": lambda num_classes: build_custom_cnn(num_classes=num_classes),
        "enabled": True,
        "primary_metric": "val_acc",
        "greater_is_better": True,
    },
    "vit_b_16": {
        "algorithm": "Vision Transformer (ViT-B/16)",
        "builder": lambda num_classes: build_vit(num_classes=num_classes, variant="vit_b_16", pretrained=True),
        "enabled": True,
        "primary_metric": "val_acc",
        "greater_is_better": True,
    },
}

MODEL_ORDER = ["resnet18", "resnet50", "custom_cnn", "vit_b_16"]


def prepare_vision_data(data_dir: Path = DEFAULT_DATA_DIR, batch_size: int = 32, img_size: int = 224) -> dict[str, Any]:
    """Load plant species image dataset directory structure into PyTorch DataLoaders."""

    # Check if user passed base folder or 'train' subfolder directly
    resolved_dir = data_dir
    if not (resolved_dir / "train").exists() and not (resolved_dir / "valid").exists():
        if resolved_dir.name == "train" and resolved_dir.parent.exists():
            resolved_dir = resolved_dir.parent  # Fall back to parent folder

    if not resolved_dir.exists():
        raise FileNotFoundError(
            f"Image dataset directory not found at: {resolved_dir}\n"
            f"Please ensure the Kaggle dataset is unzipped at:\n"
            f"  {PROJECT_ROOT}/ai/datasets/raw/image/PlantDiseaseDetectionDataset/"
        )

    print(f"\nLoading vision dataset from: {resolved_dir}")
    train_loader, val_loader, class_to_idx = create_dataloaders(
        data_dir=str(resolved_dir),
        batch_size=batch_size,
        img_size=img_size,
    )
    idx_to_class = {v: k for k, v in class_to_idx.items()}

    print(f"Classes Found ({len(class_to_idx)}): {list(class_to_idx.keys())}")
    print(f"Train Batches  : {len(train_loader)}")
    print(f"Val Batches    : {len(val_loader)}")

    return {
        "train_loader": train_loader,
        "val_loader": val_loader,
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class,
        "num_classes": len(class_to_idx),
        "data_dir": resolved_dir,
    }


def train_and_evaluate_model(
    model_name: str,
    data: dict[str, Any],
    epochs: int = 20,
    learning_rate: float = 1e-3,
) -> dict[str, Any]:
    """Train, evaluate, and serialize artifacts with lifecycle status tracking."""
    if model_name not in VISION_MODELS:
        raise ValueError(f"Unknown vision model: {model_name}")

    model_config = VISION_MODELS[model_name]
    algorithm = model_config["algorithm"]
    artifact_dir = ARTIFACT_DIR / model_name
    artifact_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = artifact_dir / "metadata.json"

    # 1. Write initial "in_progress" status metadata
    initial_metadata = {
        "status": "in_progress",
        "task_name": TASK_NAME,
        "algorithm": algorithm,
        "model_name": model_name,
        "num_classes": data["num_classes"],
        "dataset_path": str(data["data_dir"]),
        "training": {
            "epochs_planned": epochs,
            "learning_rate": learning_rate,
            "batch_size": data["train_loader"].batch_size,
        },
    }
    write_json_with_status(
        initial_metadata,
        metadata_path,
        description=f"{algorithm} metadata [in_progress]",
        indent=4,
    )

    print("\n" + "-" * 60)
    print(f"Training {algorithm}")
    print("-" * 60)

    # 2. Instantiate and run training loop with exception tracking
    model = model_config["builder"](num_classes=data["num_classes"])
    config = VisionTrainingConfig(
        epochs=epochs,
        learning_rate=learning_rate,
        checkpoint_dir=artifact_dir,
    )

    try:
        training_result = train_vision_model(
            model=model,
            train_loader=data["train_loader"],
            val_loader=data["val_loader"],
            config=config,
        )
    except Exception as error:
        # Mark metadata as failed if training crashes or is interrupted
        initial_metadata["status"] = "failed"
        initial_metadata["error"] = str(error)
        write_json_with_status(
            initial_metadata,
            metadata_path,
            description=f"{algorithm} metadata [failed]",
            indent=4,
        )
        raise error

    # 3. Compile Evaluation Metrics
    metrics = {
        "val_loss": round(training_result.best_checkpoint_val_loss, 4),
        "val_acc": round(training_result.best_checkpoint_val_acc, 4),
        "val_f1": round(training_result.best_checkpoint_val_f1, 4),
        "max_val_acc": round(training_result.max_val_acc, 4),
        "best_epoch": training_result.best_loss_epoch,
        "epochs_trained": epochs,
    }

    primary_metric = model_config.get("primary_metric", "val_acc")
    primary_metric_value = metrics[primary_metric]

    # 4. Save Metrics JSON using status helper
    metrics_path = write_json_with_status(
        metrics,
        artifact_dir / "metrics.json",
        description=f"{algorithm} metrics",
        indent=4,
    )

    # 5. Save Class Map Artifact using status helper
    class_map_path = write_json_with_status(
        {
            "class_to_idx": data["class_to_idx"],
            "idx_to_class": data["idx_to_class"],
        },
        artifact_dir / "class_map.json",
        description=f"{algorithm} class map",
        indent=4,
    )

    # 6. Mark Metadata status as "completed"
    final_metadata = {
        "status": "completed",
        "task_name": TASK_NAME,
        "algorithm": algorithm,
        "model_name": model_name,
        "num_classes": data["num_classes"],
        "dataset_path": str(data["data_dir"]),
        "primary_metric": primary_metric,
        "primary_metric_value": metrics[primary_metric],
        "metrics": metrics,
        "evaluation": {
            "confusion_matrix": training_result.final_confusion_matrix,
        },
        "training": {
            "duration_seconds": round(training_result.duration_seconds, 2),
            "learning_rate": learning_rate,
            "batch_size": data["train_loader"].batch_size,
        },
    }

    write_json_with_status(
        final_metadata,
        metadata_path,
        description=f"{algorithm} metadata [completed]",
        indent=4,
    )

    model_path = training_result.best_model_path or (artifact_dir / "best_vision_model.pth")

    return {
        "model_name": model_name,
        "algorithm": algorithm,
        "model": training_result.model,
        "artifact_dir": artifact_dir,
        "model_path": model_path,
        "class_map_path": class_map_path,
        "metrics_path": metrics_path,
        "metadata_path": metadata_path,
        "metrics": metrics,
        "primary_metric": primary_metric,
        "primary_metric_value": primary_metric_value,
        "greater_is_better": model_config.get("greater_is_better", True),
    }


def train_selected_model(model_name: str, data_dir: Path = DEFAULT_DATA_DIR) -> Optional[Dict[str, Any]]:
    """Train and evaluate a single configured vision model with pause/resume support."""
    model_config = VISION_MODELS.get(model_name)
    if model_config is None:
        raise ValueError(f"Unknown vision model: {model_name}")
    if not model_config.get("enabled", True):
        raise ValueError(f"Vision model is not enabled yet: {model_name}")

    # 1. CHECK FOR PAUSED CHECKPOINT BEFORE DATASET LOADING
    artifact_dir = Path("artifacts/plant_identification") / model_name
    checkpoint_file = artifact_dir / "training_checkpoint.pth"

    if checkpoint_file.exists():
        print("\n" + "=" * 60)
        print(f" ⏸️ PAUSED SESSION DETECTED FOR [{model_name.upper()}]")
        print(f" Checkpoint: {checkpoint_file}")
        print("=" * 60)
        print(" [1] Resume previous training session")
        print(" [2] Start fresh (overwrite existing checkpoint)")
        print(" [3] Delete checkpoint and return to main menu")
        print("=" * 60)

        choice = input("Select an option (1-3) [default: 1]: ").strip()

        if choice == "2":
            print(f"\n[INFO] Overwriting checkpoint. Starting fresh training for {model_name}...")
            checkpoint_file.unlink(missing_ok=True)
        elif choice == "3":
            print("\n[INFO] Checkpoint removed. Returning to main menu...")
            checkpoint_file.unlink(missing_ok=True)
            return None
        else:
            print(f"\n[INFO] Resuming training session for {model_name}...")

    # 2. PREPARE DATASET
    data = prepare_vision_data(data_dir=data_dir)

    # 3. RUN TRAINING LOOP (CATCH CTRL+C GRACEFULLY)
    try:
        return train_and_evaluate_model(model_name, data)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print(f" ⏸️ [PAUSED] Training session for [{model_name}] saved.")
        print(f" Returning to menu. Re-select [{model_name}] anytime to resume.")
        print("=" * 60 + "\n")
        return None


def train_all_models(data_dir: Path = DEFAULT_DATA_DIR) -> dict[str, Any]:
    """Train configured vision models, compare performance, and persist the best model."""
    print("=" * 60)
    print(f"{TASK_LABEL} Training Pipeline")
    print("=" * 60)

    data = prepare_vision_data(data_dir=data_dir)
    results = []
    skipped_models = []

    for model_name in MODEL_ORDER:
        model_config = VISION_MODELS.get(model_name, {})
        if not model_config.get("enabled", True):
            skipped_models.append(skip_model(model_name, model_config))
            continue

        results.append(train_and_evaluate_model(model_name=model_name, data=data))

    comparison = compare_models(results, skipped_models)
    best_result = comparison["best_model"]
    best_artifact_dir = save_best_model(best_result)
    comparison["best_artifact_dir"] = str(best_artifact_dir)
    save_comparison(comparison)

    print("\n" + "=" * 60)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 60)
    for result in results:
        metric = result["primary_metric"]
        print(f"- {result['algorithm']}: {metric}={result['primary_metric_value']:.4f}")
    for skipped_model in skipped_models:
        print(f"- {skipped_model['algorithm']}: skipped ({skipped_model['reason']})")

    print("\nBEST VISION MODEL:")
    print(f"-> {best_result['algorithm']} ({best_result['primary_metric']}={best_result['primary_metric_value']:.4f})")
    print(f"-> Artifacts: {best_artifact_dir}")

    return {
        "data": data,
        "results": results,
        "skipped_models": skipped_models,
        "comparison": comparison,
        "best_model": best_result,
    }


def skip_model(model_name: str, model_config: dict[str, Any]) -> dict[str, Any]:
    """Record a model that is configured but skipped during pipeline execution."""
    return {
        "model_name": model_name,
        "algorithm": model_config.get("algorithm", model_name),
        "status": model_config.get("status", "skipped"),
        "reason": model_config.get("reason", "Model disabled in configuration."),
    }


def compare_models(
    results: list[dict[str, Any]],
    skipped_models: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compare evaluation metrics across all trained vision models."""
    if not results:
        raise ValueError("No trained vision model results to compare.")

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
    """Persist a copy of the winning model and its class map into best_model/."""
    best_dir = ARTIFACT_DIR / "best_model"
    best_dir.mkdir(parents=True, exist_ok=True)

    if Path(best_result["model_path"]).exists():
        shutil.copy2(best_result["model_path"], best_dir / "model.pth")
    shutil.copy2(best_result["class_map_path"], best_dir / "class_map.json")
    shutil.copy2(best_result["metadata_path"], best_dir / "metadata.json")
    shutil.copy2(best_result["metrics_path"], best_dir / "metrics.json")

    return best_dir


def save_comparison(comparison: dict[str, Any]) -> Path:
    """Save model comparison JSON excluding un-serializable PyTorch model objects."""
    comparison_path = ARTIFACT_DIR / "model_comparison.json"
    comparison_path.parent.mkdir(parents=True, exist_ok=True)

    serializable = {key: value for key, value in comparison.items() if key != "best_model"}
    with comparison_path.open("w", encoding="utf-8") as file:
        json.dump(_make_json_safe(serializable), file, indent=4)
    return comparison_path


def _make_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


# =========================================================
# MENU & WORKFLOW DRIVER
# =========================================================


def interactive_loop(dry_run: bool = False) -> None:
    menu = MenuRunner(
        title="Plant Identification Vision Training Menu",
        items=[
            MenuItem(
                key="1",
                label="Train & Compare All Vision Models (ResNet, ViT, Custom CNN)",
                action=lambda dry_run: train_all_models(data_dir=DEFAULT_DATA_DIR) if not dry_run else None,
            ),
            MenuItem(
                key="2",
                label="Train Selected Model (ResNet-18)",
                action=lambda dry_run: train_selected_model("resnet18", data_dir=DEFAULT_DATA_DIR) if not dry_run else None,
            ),
            MenuItem(
                key="0",
                label="Exit",
                action=lambda dry_run: None,
            ),
        ],
        prompt_func=prompt_menu_choice,
        pause_func=pause_for_user,
    )
    menu.run(dry_run=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manager for Plant Identification Vision Models")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing.")
    parser.add_argument("--model", choices=list(VISION_MODELS.keys()) + ["all"], default=None)

    args = parser.parse_args()

    if args.model == "all":
        train_all_models(data_dir=DEFAULT_DATA_DIR)
    elif args.model:
        train_selected_model(model_name=args.model, data_dir=DEFAULT_DATA_DIR)
    else:
        interactive_loop(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
