"""Persistence helpers for models and preprocessing artifacts."""

from pathlib import Path
from typing import Any

import joblib


def ensure_model_dir(path: str | Path) -> Path:
    """Create and return a model/artifact directory."""

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_model(model, path: str | Path) -> Path:
    """Serialize a model with joblib."""

    model_path = Path(path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    return model_path


def load_model(path: str | Path):
    """Load a joblib-serialized model."""

    model_path = Path(path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    return joblib.load(model_path)


def save_artifact(artifact: Any, path: str | Path) -> Path:
    """Serialize an arbitrary preprocessing/model artifact with joblib."""

    artifact_path = Path(path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, artifact_path)
    return artifact_path


def load_artifact(path: str | Path) -> Any:
    """Load a joblib-serialized artifact."""

    artifact_path = Path(path)
    if not artifact_path.exists():
        raise FileNotFoundError(f"Artifact not found: {artifact_path}")
    return joblib.load(artifact_path)


def save_preprocessing_artifacts(artifacts: Any, path: str | Path) -> Path:
    """Save preprocessing artifacts required for inference."""

    return save_artifact(artifacts, path)


def load_preprocessing_artifacts(path: str | Path) -> Any:
    """Load preprocessing artifacts required for inference."""

    return load_artifact(path)
