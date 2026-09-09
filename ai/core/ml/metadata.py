"""Model metadata creation and JSON persistence."""

# ai/core/metadata.py

from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
import json
import math

import numpy as np

from ai.core.file_status import write_json_with_status


def create_model_metadata(
    task_name: str,
    algorithm: str,
    problem_type: str,
    target_column: str,
    feature_columns: list[str],
    training_rows: int,
    test_rows: int | None = None,
    validation_rows: int | None = None,
    model_params: dict[str, Any] | None = None,
    preprocessing_config: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    model_version: str | None = None,
    checkpoint_metric: str | None = "min_val_loss",
    selection_metric: str | None = "max_val_acc",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build standardized metadata for a trained model."""

    metadata = {
        "task": task_name,
        "algorithm": algorithm,
        "problem_type": problem_type,
        "target": target_column,
        "features": feature_columns,
        "training_rows": training_rows,
        "validation_rows": validation_rows,
        "testing_rows": test_rows,
        "created": datetime.now().isoformat(),
        "model_version": model_version,
        "model_selection": {
            "checkpoint_metric": checkpoint_metric,
            "selection_metric": selection_metric,
        },
        "model_params": model_params or {},
        "preprocessing_config": preprocessing_config or {},
        "metrics": metrics or {},
    }

    if extra:
        metadata.update(extra)

    return _make_json_safe(metadata)


def save_metadata(metadata: dict[str, Any], path: str | Path) -> Path:
    """Save model metadata as JSON."""

    metadata_path = Path(path)
    return write_json_with_status(
        _make_json_safe(metadata),
        metadata_path,
        description="model metadata",
        indent=4,
    )


def load_metadata(path: str | Path) -> dict[str, Any]:
    """Load model metadata from JSON."""

    metadata_path = Path(path)
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")

    with metadata_path.open(encoding="utf-8") as file:
        return json.load(file)


def _make_json_safe(value):
    if is_dataclass(value):
        return _make_json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _make_json_safe(value.tolist())
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        float_value = float(value)
        return float_value if math.isfinite(float_value) else None
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
