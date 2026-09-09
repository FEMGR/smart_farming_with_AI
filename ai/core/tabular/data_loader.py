"""
Dataset loading utilities for ML tasks.

This module keeps file loading and basic dataset checks out of task-specific
training scripts.
"""

# ai/core/ml/tabular/data_loader.py

from pathlib import Path
from typing import Iterable

import pandas as pd


def load_dataset(
    path: str | Path,
    required_columns: Iterable[str] | None = None,
    allow_empty: bool = False,
    **read_csv_kwargs,
) -> pd.DataFrame:
    """
    Load a CSV dataset and validate its basic shape.

    Parameters
    ----------
    path:
        CSV file path.
    required_columns:
        Optional columns that must be present in the loaded DataFrame.
    allow_empty:
        Whether an empty CSV is acceptable.
    read_csv_kwargs:
        Extra keyword arguments forwarded to pandas.read_csv.
    """

    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    if not dataset_path.is_file():
        raise ValueError(f"Dataset path is not a file: {dataset_path}")

    df = pd.read_csv(dataset_path, **read_csv_kwargs)
    return validate_dataset(df, required_columns=required_columns, allow_empty=allow_empty)


def validate_dataset(
    df: pd.DataFrame,
    required_columns: Iterable[str] | None = None,
    allow_empty: bool = False,
) -> pd.DataFrame:
    """Validate a loaded training dataset and return it unchanged."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")

    if df.empty and not allow_empty:
        raise ValueError("Dataset is empty.")

    if len(df.columns) == 0:
        raise ValueError("Dataset has no columns.")

    required = list(required_columns or [])
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    return df


def load_csv(*args, **kwargs) -> pd.DataFrame:
    """Backward-compatible alias for load_dataset."""

    return load_dataset(*args, **kwargs)
