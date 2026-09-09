"""PyTorch MLP model builder for tabular prediction tasks."""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    import torch
    from torch import nn
except ImportError as exc:  # pragma: no cover - exercised only without torch installed
    torch = None
    nn = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

from ai.core.tabular.dataset import create_dataloaders
from ai.core.ml.pytorch.training import PyTorchTrainingConfig, train_pytorch_model

DEFAULT_CLASSIFIER_PARAMS: dict[str, Any] = {
    "hidden_layers": (64, 32),
    "dropout": 0.10,
    "epochs": 50,
    "batch_size": 128,
    "learning_rate": 0.001,
    "weight_decay": 0.0,
    "random_state": 42,
    "device": None,
}

DEFAULT_REGRESSOR_PARAMS: dict[str, Any] = {
    "hidden_layers": (64, 32),
    "dropout": 0.10,
    "epochs": 80,
    "batch_size": 128,
    "learning_rate": 0.001,
    "weight_decay": 0.0,
    "random_state": 42,
    "device": None,
}


def ensure_torch_available() -> None:
    """Raise a clear error when PyTorch is not installed."""

    if _IMPORT_ERROR is not None:
        raise ImportError("PyTorch is required to build PyTorch MLP models. Install torch in the project environment.") from _IMPORT_ERROR


if nn is not None:

    class MLP(nn.Module):
        """Feed-forward multilayer perceptron for tabular data."""

        def __init__(
            self,
            input_dim: int,
            output_dim: int,
            hidden_layers: tuple[int, ...] = (64, 32),
            dropout: float = 0.10,
        ) -> None:
            super().__init__()
            layers: list[nn.Module] = []
            previous_dim = input_dim

            for hidden_dim in hidden_layers:
                layers.append(nn.Linear(previous_dim, hidden_dim))
                layers.append(nn.ReLU())
                if dropout > 0:
                    layers.append(nn.Dropout(dropout))
                previous_dim = hidden_dim

            layers.append(nn.Linear(previous_dim, output_dim))
            self.network = nn.Sequential(*layers)

        def forward(self, X):
            return self.network(X)

else:

    class MLP:  # pragma: no cover - exercised only without torch installed
        """Placeholder class that raises a clear dependency error."""

        def __init__(self, *args, **kwargs) -> None:
            ensure_torch_available()


class PyTorchMLPEstimator:
    """Small sklearn-style wrapper around the PyTorch MLP."""

    def __init__(
        self,
        problem_type: str,
        hidden_layers: tuple[int, ...] = (64, 32),
        dropout: float = 0.10,
        epochs: int = 50,
        batch_size: int = 128,
        learning_rate: float = 0.001,
        weight_decay: float = 0.0,
        random_state: int = 42,
        device: str | None = None,
    ) -> None:
        self.problem_type = problem_type
        self.hidden_layers = tuple(hidden_layers)
        self.dropout = dropout
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.random_state = random_state
        self.device = device
        self.model_ = None
        self.classes_ = None
        self.feature_mean_ = None
        self.feature_scale_ = None
        self.target_mean_ = None
        self.target_scale_ = None
        self.training_history_ = None
        self.training_result_ = None

    def fit(self, X, y):
        """Fit the MLP model."""

        ensure_torch_available()
        if self.problem_type not in {"classification", "regression"}:
            raise ValueError(f"Unsupported problem type: {self.problem_type}")

        X_array = np.asarray(X, dtype=np.float32)
        y_array = np.asarray(y)
        X_scaled = self._fit_transform_features(X_array)

        if self.problem_type == "classification":
            self.classes_ = np.unique(y_array)
            class_to_index = {label: index for index, label in enumerate(self.classes_)}
            y_train = np.asarray([class_to_index[label] for label in y_array], dtype=np.int64)
            output_dim = len(self.classes_)
        else:
            y_numeric = y_array.astype(np.float32)
            self.target_mean_ = float(np.mean(y_numeric))
            self.target_scale_ = float(np.std(y_numeric))
            if self.target_scale_ == 0:
                self.target_scale_ = 1.0
            y_train = ((y_numeric - self.target_mean_) / self.target_scale_).astype(np.float32)
            output_dim = 1

        torch.manual_seed(self.random_state)
        self.model_ = MLP(
            input_dim=X_scaled.shape[1],
            output_dim=output_dim,
            hidden_layers=self.hidden_layers,
            dropout=self.dropout,
        )
        training_config = PyTorchTrainingConfig(
            epochs=self.epochs,
            batch_size=self.batch_size,
            learning_rate=self.learning_rate,
            weight_decay=self.weight_decay,
            random_state=self.random_state,
            device=self.device,
        )
        train_loader = create_dataloaders(
            X_scaled,
            y_train,
            self.problem_type,
            batch_size=self.batch_size,
            shuffle=True,
        )
        self.training_result_ = train_pytorch_model(
            self.model_,
            train_loader,
            self.problem_type,
            config=training_config,
        )
        self.training_history_ = self.training_result_.history
        return self

    def predict(self, X):
        """Predict labels or regression values."""

        ensure_torch_available()
        self._ensure_fitted()
        outputs = self._predict_outputs(X)

        if self.problem_type == "classification":
            class_indices = np.argmax(outputs, axis=1)
            return self.classes_[class_indices]

        values = outputs.reshape(-1)
        return values * self.target_scale_ + self.target_mean_

    def predict_proba(self, X):
        """Return class probabilities for classification tasks."""

        ensure_torch_available()
        self._ensure_fitted()
        if self.problem_type != "classification":
            raise AttributeError("predict_proba is only available for classification tasks.")

        outputs = self._predict_outputs(X)
        probabilities = torch.softmax(torch.as_tensor(outputs), dim=1)
        return probabilities.numpy()

    def get_params(self, deep: bool = True) -> dict[str, Any]:
        """Return estimator configuration parameters."""

        return {
            "problem_type": self.problem_type,
            "hidden_layers": self.hidden_layers,
            "dropout": self.dropout,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "weight_decay": self.weight_decay,
            "random_state": self.random_state,
            "device": self.device,
        }

    def set_params(self, **params):
        """Set estimator configuration parameters."""

        for key, value in params.items():
            setattr(self, key, value)
        return self

    def _fit_transform_features(self, X_array: np.ndarray) -> np.ndarray:
        self.feature_mean_ = X_array.mean(axis=0)
        self.feature_scale_ = X_array.std(axis=0)
        self.feature_scale_[self.feature_scale_ == 0] = 1.0
        return ((X_array - self.feature_mean_) / self.feature_scale_).astype(np.float32)

    def _transform_features(self, X) -> np.ndarray:
        X_array = np.asarray(X, dtype=np.float32)
        return ((X_array - self.feature_mean_) / self.feature_scale_).astype(np.float32)

    def _predict_outputs(self, X) -> np.ndarray:
        X_scaled = self._transform_features(X)
        self.model_.eval()
        with torch.no_grad():
            tensor = torch.as_tensor(X_scaled, dtype=torch.float32)
            return self.model_(tensor).detach().cpu().numpy()

    def _ensure_fitted(self) -> None:
        if self.model_ is None:
            raise ValueError("PyTorchMLPEstimator has not been fitted.")


def build_classifier(params: dict[str, Any] | None = None) -> PyTorchMLPEstimator:
    """Build a PyTorch MLP classifier."""

    return PyTorchMLPEstimator("classification", **_merge_params(DEFAULT_CLASSIFIER_PARAMS, params))


def build_regressor(params: dict[str, Any] | None = None) -> PyTorchMLPEstimator:
    """Build a PyTorch MLP regressor."""

    return PyTorchMLPEstimator("regression", **_merge_params(DEFAULT_REGRESSOR_PARAMS, params))


def build_model(
    problem_type: str,
    params: dict[str, Any] | None = None,
) -> PyTorchMLPEstimator:
    """Build a PyTorch MLP model for a classification or regression task."""

    if problem_type == "classification":
        return build_classifier(params)

    if problem_type == "regression":
        return build_regressor(params)

    raise ValueError(f"Unsupported problem type: {problem_type}")


def _merge_params(
    defaults: dict[str, Any],
    overrides: dict[str, Any] | None,
) -> dict[str, Any]:
    return {**defaults, **(overrides or {})}
