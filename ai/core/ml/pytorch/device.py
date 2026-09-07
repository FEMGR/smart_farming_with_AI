"""
Purpose
-------
Provide centralized utilities for selecting and managing the PyTorch
computation device.

This module ensures PyTorch models and tensors consistently use the
best available device, such as CUDA (GPU) or CPU.
"""

# ai/core/ml/pytorch/device.py

try:
    import torch
except ImportError as exc:  # pragma: no cover
    torch = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def ensure_torch_available() -> None:
    """Raise a clear error when PyTorch is not installed."""

    if _IMPORT_ERROR is not None:
        raise ImportError("PyTorch is required for this operation. " "Install torch in the project environment.") from _IMPORT_ERROR


def resolve_device(requested_device: str | torch.device | None = None) -> torch.device:
    """
    Resolve the PyTorch computation device.

    Uses the requested device when provided. Otherwise, CUDA is used
    when available, with CPU as the fallback.
    """
    ensure_torch_available()

    # 1. If user passed an existing torch.device object, return it as-is
    if isinstance(requested_device, torch.device):
        return requested_device

    # 2. If user passed a string (e.g. "cuda", "cpu", "cuda:0"), convert it
    if requested_device is not None:
        return torch.device(requested_device)

    # 3. Default fallback logic
    default_device_str = "cuda" if torch.cuda.is_available() else "cpu"
    return torch.device(default_device_str)
