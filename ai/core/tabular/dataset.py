"""Dataset handling for PyTorch tabular models."""

# ai/core/tabular/dataset.py

from typing import Literal
import numpy as np
from ai.core.ml.pytorch.device import ensure_torch_available

try:
    import torch
    from torch.utils.data import DataLoader, Dataset
except ImportError as exc:  # pragma: no cover - exercised only without torch installed
    torch = None
    DataLoader = None
    Dataset = object
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


ProblemType = Literal["classification", "regression"]


class TabularDataset(Dataset):
    """PyTorch Dataset for numeric tabular features and targets."""

    def __init__(
        self,
        X,
        y,
        problem_type: ProblemType,
    ) -> None:
        ensure_torch_available()
        self.X = torch.as_tensor(np.asarray(X, dtype=np.float32), dtype=torch.float32)

        if problem_type == "classification":
            self.y = torch.as_tensor(np.asarray(y, dtype=np.int64), dtype=torch.long)
        elif problem_type == "regression":
            self.y = torch.as_tensor(np.asarray(y, dtype=np.float32).reshape(-1, 1), dtype=torch.float32)
        else:
            raise ValueError(f"Unsupported problem type: {problem_type}")

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, index: int):
        return self.X[index], self.y[index]


def create_dataloaders(
    X,
    y,
    problem_type: ProblemType,
    batch_size: int,
    shuffle: bool = True,
) -> DataLoader:
    """Create a PyTorch DataLoader for tabular data."""

    ensure_torch_available()
    dataset = TabularDataset(X, y, problem_type)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
