"""Common training helpers for scikit-learn-compatible models."""

# ai/core/ml/training.py

from dataclasses import dataclass, field
from datetime import datetime
from time import perf_counter
from typing import Any


@dataclass
class TrainingResult:
    model: Any
    training_rows: int
    started_at: str
    finished_at: str
    duration_seconds: float
    fit_params: dict[str, Any] = field(default_factory=dict)


def train_model(
    model,
    X_train,
    y_train,
    fit_params: dict[str, Any] | None = None,
) -> TrainingResult:
    """Fit a scikit-learn/XGBoost-style model and return training details."""

    params = fit_params or {}
    started_at = datetime.now().isoformat()
    start = perf_counter()

    model.fit(X_train, y_train, **params)

    duration = perf_counter() - start
    finished_at = datetime.now().isoformat()
    return TrainingResult(
        model=model,
        training_rows=len(X_train),
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration,
        fit_params=params,
    )


def get_model_params(model) -> dict[str, Any]:
    """Return model parameters when the estimator exposes get_params()."""

    if hasattr(model, "get_params"):
        return model.get_params()

    return {}
