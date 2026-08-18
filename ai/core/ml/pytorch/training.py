"""Training loop for PyTorch tabular models."""

from dataclasses import dataclass, field
from datetime import datetime
from time import perf_counter
from typing import Any, Literal

try:
    import torch
    from torch import nn
except ImportError as exc:  # pragma: no cover - exercised only without torch installed
    torch = None
    nn = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


ProblemType = Literal["classification", "regression"]


@dataclass(frozen=True)
class PyTorchTrainingConfig:
    epochs: int = 50
    batch_size: int = 128
    learning_rate: float = 0.001
    weight_decay: float = 0.0
    random_state: int = 42
    device: str | None = None


@dataclass
class PyTorchTrainingResult:
    model: Any
    training_rows: int
    started_at: str
    finished_at: str
    duration_seconds: float
    history: dict[str, list[float]] = field(default_factory=dict)


def ensure_torch_available() -> None:
    """Raise a clear error when PyTorch is not installed."""

    if _IMPORT_ERROR is not None:
        raise ImportError("PyTorch is required for MLP training. Install torch in the project environment.") from _IMPORT_ERROR


def resolve_device(device: str | None = None):
    """Resolve the requested training device."""

    ensure_torch_available()
    if device:
        return torch.device(device)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def train_pytorch_model(
    model,
    train_loader,
    problem_type: ProblemType,
    config: PyTorchTrainingConfig | None = None,
) -> PyTorchTrainingResult:
    """Train a PyTorch model with a standard supervised loop."""

    ensure_torch_available()
    training_config = config or PyTorchTrainingConfig()
    torch.manual_seed(training_config.random_state)

    device = resolve_device(training_config.device)
    model.to(device)
    model.train()

    if problem_type == "classification":
        criterion = nn.CrossEntropyLoss()
    elif problem_type == "regression":
        criterion = nn.MSELoss()
    else:
        raise ValueError(f"Unsupported problem type: {problem_type}")

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=training_config.learning_rate,
        weight_decay=training_config.weight_decay,
    )

    started_at = datetime.now().isoformat()
    start = perf_counter()
    history = {"loss": []}

    for _ in range(training_config.epochs):
        epoch_loss = 0.0
        sample_count = 0

        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()

            batch_size = len(X_batch)
            epoch_loss += float(loss.detach().cpu().item()) * batch_size
            sample_count += batch_size

        history["loss"].append(epoch_loss / sample_count if sample_count else 0.0)

    duration = perf_counter() - start
    finished_at = datetime.now().isoformat()
    model.to("cpu")
    model.eval()

    return PyTorchTrainingResult(
        model=model,
        training_rows=len(train_loader.dataset),
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration,
        history=history,
    )
