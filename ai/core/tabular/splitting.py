"""
Dataset splitting helpers.

Random train/test splits are the default. A time-aware split is available for
future tasks that must avoid mixing future observations into training data.
"""

from dataclasses import dataclass
from typing import Literal

import pandas as pd
from sklearn.model_selection import train_test_split

SplitStrategy = Literal["random", "time"]


@dataclass(frozen=True)
class SplitConfig:
    test_size: float = 0.20
    validation_size: float | None = None
    random_state: int = 42
    stratify: bool = True
    shuffle: bool = True
    strategy: SplitStrategy = "random"
    time_column: str | None = None


def split_dataset(
    X: pd.DataFrame,
    y: pd.Series,
    problem_type: str | None = None,
    config: SplitConfig | None = None,
) -> dict:
    """
    Split features and target into train/test or train/validation/test sets.
    """

    split_config = config or SplitConfig()
    _validate_split_inputs(X, y, split_config)

    if split_config.strategy == "time":
        return _time_split(X, y, split_config)

    return _random_split(X, y, problem_type, split_config)


def _validate_split_inputs(X: pd.DataFrame, y: pd.Series, config: SplitConfig) -> None:
    if len(X) != len(y):
        raise ValueError("X and y must contain the same number of rows.")

    if not 0 < config.test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")

    if config.validation_size is not None and not 0 < config.validation_size < 1:
        raise ValueError("validation_size must be between 0 and 1.")

    if config.strategy == "time" and not config.time_column:
        raise ValueError("time_column is required for time-aware splitting.")

    if config.strategy not in {"random", "time"}:
        raise ValueError(f"Unsupported split strategy: {config.strategy}")


def _random_split(
    X: pd.DataFrame,
    y: pd.Series,
    problem_type: str | None,
    config: SplitConfig,
) -> dict:
    stratify = _get_stratify_values(y, problem_type, config)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
        shuffle=config.shuffle,
        stratify=stratify,
    )

    result = {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
    }

    if config.validation_size is not None:
        validation_stratify = _get_stratify_values(y_train, problem_type, config)
        X_train, X_validation, y_train, y_validation = train_test_split(
            X_train,
            y_train,
            test_size=config.validation_size,
            random_state=config.random_state,
            shuffle=config.shuffle,
            stratify=validation_stratify,
        )
        result.update(
            {
                "X_train": X_train,
                "X_validation": X_validation,
                "X_val": X_validation,
                "y_train": y_train,
                "y_validation": y_validation,
                "y_val": y_validation,
            }
        )

    return result


def _time_split(X: pd.DataFrame, y: pd.Series, config: SplitConfig) -> dict:
    if config.time_column in X.columns:
        sort_values = X[config.time_column]
    elif getattr(y, "name", None) == config.time_column:
        sort_values = y
    else:
        raise ValueError(f"time_column not found in features or target: {config.time_column}")

    ordered_index = sort_values.sort_values().index
    X_ordered = X.loc[ordered_index]
    y_ordered = y.loc[ordered_index]

    test_start = int(len(X_ordered) * (1 - config.test_size))
    X_train = X_ordered.iloc[:test_start]
    X_test = X_ordered.iloc[test_start:]
    y_train = y_ordered.iloc[:test_start]
    y_test = y_ordered.iloc[test_start:]

    result = {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
    }

    if config.validation_size is not None:
        validation_start = int(len(X_train) * (1 - config.validation_size))
        result.update(
            {
                "X_train": X_train.iloc[:validation_start],
                "X_validation": X_train.iloc[validation_start:],
                "X_val": X_train.iloc[validation_start:],
                "y_train": y_train.iloc[:validation_start],
                "y_validation": y_train.iloc[validation_start:],
                "y_val": y_train.iloc[validation_start:],
            }
        )

    return result


def _get_stratify_values(
    y: pd.Series,
    problem_type: str | None,
    config: SplitConfig,
) -> pd.Series | None:
    if problem_type != "classification" or not config.stratify or not config.shuffle:
        return None

    class_counts = pd.Series(y).value_counts(dropna=False)
    if len(class_counts) < 2 or (class_counts < 2).any():
        return None

    return y
