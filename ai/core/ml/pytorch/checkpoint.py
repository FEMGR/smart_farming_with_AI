"""
Purpose
-------
Provide centralized utilities for saving and loading PyTorch training
checkpoints.

A checkpoint stores the model state and optionally the optimizer,
training progress, and evaluation metrics so training can be resumed
or the best model state can be restored.

Primary use:
    MLP
    CNN
    ResNet
    Vision Transformer

Saves:
    - model_state_dict
    - optimizer_state_dict
    - scheduler_state_dict (optional)
    - epoch
    - metrics
"""

# ai/core/ml/pytorch/checkpoint.py

from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torch.optim import Optimizer


def save_checkpoint(
    model: nn.Module,
    optimizer: Optimizer | None,
    epoch: int,
    path: str | Path,
    metrics: dict[str, Any] | None = None,
    scheduler: Any | None = None,
) -> None:
    """
    Save the current PyTorch training state.

    The checkpoint includes the model state, optional optimizer state,
    current epoch, optional evaluation metrics, and optional scheduler
    state.
    """

    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Unwrap DataParallel or DistributedDataParallel models.
    model_to_save = model.module if hasattr(model, "module") else model

    checkpoint_data: dict[str, Any] = {
        "epoch": epoch,
        "model_state_dict": model_to_save.state_dict(),
        "optimizer_state_dict": (optimizer.state_dict() if optimizer is not None else None),
        "metrics": metrics or {},
    }

    if scheduler is not None:
        checkpoint_data["scheduler_state_dict"] = scheduler.state_dict()

    torch.save(
        checkpoint_data,
        checkpoint_path,
    )


def load_checkpoint(
    model: nn.Module,
    path: str | Path,
    optimizer: Optimizer | None = None,
    device: str | torch.device | None = None,
    scheduler: Any | None = None,
) -> dict[str, Any]:
    """
    Load a PyTorch training checkpoint.

    Restores the model and optional optimizer and scheduler states.

    Returns
    -------
    dict
        Saved training metadata, including epoch and metrics.
    """

    checkpoint_path = Path(path)

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    if device is None:
        device = next(model.parameters()).device

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,  # If loading complex custom objects/schedulers
    )

    # Unwrap DataParallel or DistributedDataParallel models.
    model_to_load = model.module if hasattr(model, "module") else model

    model_to_load.load_state_dict(checkpoint["model_state_dict"])

    if optimizer is not None and checkpoint.get("optimizer_state_dict") is not None:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

    if scheduler is not None and checkpoint.get("scheduler_state_dict") is not None:
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

    return {
        "epoch": checkpoint.get("epoch", 0),
        "metrics": checkpoint.get("metrics", {}),
    }
