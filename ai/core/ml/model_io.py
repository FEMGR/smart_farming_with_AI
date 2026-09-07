"""
Persistence helpers for trained models and preprocessing artifacts.

Primary use:
    PyTorch models (MLPs, CNNs, Vision Transformers)
    Random Forest
    XGBoost
    Scikit-learn pipelines
    Encoders
    Scalers
    Feature transformers

PyTorch models are persisted using torch serialization, while
traditional machine learning models and preprocessing artifacts use
joblib serialization.

This module handles final trained models intended for inference.
PyTorch training checkpoints are handled separately by
ai.core.ml.pytorch.checkpoint.
"""

from pathlib import Path
from typing import Any

import joblib

from ai.core.file_status import write_joblib_with_status


try:
    import torch
    from torch import nn
except ImportError:
    torch = None
    nn = None
    HAS_PYTORCH = False
else:
    HAS_PYTORCH = True


PYTORCH_EXTENSIONS = {".pt", ".pth"}


def ensure_model_dir(path: str | Path) -> Path:
    """Create and return a model or artifact directory."""

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _is_pytorch_model(model: Any) -> bool:
    """Return whether the object is a PyTorch model."""

    return HAS_PYTORCH and isinstance(model, nn.Module)


def save_model(
    model: Any,
    path: str | Path,
) -> Path:
    """
    Save a trained model for inference.

    PyTorch models are saved using PyTorch serialization.
    Traditional machine learning models are saved using joblib.
    """

    if _is_pytorch_model(model):
        return save_pytorch_model(model, path)

    model_path = Path(path)

    ensure_model_dir(model_path.parent)

    return write_joblib_with_status(
        model,
        model_path,
        description="trained model",
    )


def load_model(
    path: str | Path,
    model_architecture: Any | None = None,
    device: str | None = None,
) -> Any:
    """
    Load a trained model.

    PyTorch models require an optional model architecture when loading
    weights-only files. Traditional models are loaded with joblib.
    """

    model_path = Path(path)

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    if model_path.suffix.lower() in PYTORCH_EXTENSIONS:
        return load_pytorch_model(
            model_path,
            model_architecture=model_architecture,
            device=device,
        )

    return joblib.load(model_path)


def save_pytorch_model(
    model: Any,
    path: str | Path,
    save_weights_only: bool = True,
) -> Path:
    """
    Save a trained PyTorch model for inference.

    By default, only the model state dictionary is saved.
    """

    if not HAS_PYTORCH:
        raise ImportError("PyTorch is required to save PyTorch models.")

    model_path = Path(path)

    ensure_model_dir(model_path.parent)

    model_to_save = model.module if hasattr(model, "module") else model

    if save_weights_only:
        torch.save(
            model_to_save.state_dict(),
            model_path,
        )
    else:
        torch.save(
            model_to_save,
            model_path,
        )

    return model_path


def load_pytorch_model(
    path: str | Path,
    model_architecture: Any | None = None,
    device: str | None = None,
) -> Any:
    """
    Load a trained PyTorch model for inference.

    A model architecture must be provided when loading a weights-only
    state dictionary.
    """

    if not HAS_PYTORCH:
        raise ImportError("PyTorch is required to load PyTorch models.")

    model_path = Path(path)

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    map_location = device or "cpu"

    loaded_object = torch.load(
        model_path,
        map_location=map_location,
    )

    # Weights-only model
    if isinstance(loaded_object, dict):

        if model_architecture is None:
            raise ValueError("model_architecture is required when loading " "a PyTorch state dictionary.")

        model = model_architecture.to(map_location)

        model.load_state_dict(loaded_object)

        model.eval()

        return model

    # Full serialized model
    if isinstance(loaded_object, nn.Module):

        loaded_object = loaded_object.to(map_location)

        loaded_object.eval()

        return loaded_object

    raise ValueError(f"Unsupported PyTorch model format: {model_path}")


def save_artifact(
    artifact: Any,
    path: str | Path,
) -> Path:
    """
    Save a preprocessing or supporting artifact with joblib.
    """

    artifact_path = Path(path)

    ensure_model_dir(artifact_path.parent)

    return write_joblib_with_status(
        artifact,
        artifact_path,
        description="preprocessing/model artifact",
    )


def load_artifact(
    path: str | Path,
) -> Any:
    """
    Load a preprocessing or supporting artifact.
    """

    artifact_path = Path(path)

    if not artifact_path.exists():
        raise FileNotFoundError(f"Artifact not found: {artifact_path}")

    return joblib.load(artifact_path)


def save_preprocessing_artifacts(
    artifacts: Any,
    path: str | Path,
) -> Path:
    """
    Save preprocessing artifacts required for inference.
    """

    return save_artifact(artifacts, path)


def load_preprocessing_artifacts(
    path: str | Path,
) -> Any:
    """
    Load preprocessing artifacts required for inference.
    """

    return load_artifact(path)
