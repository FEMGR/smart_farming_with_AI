"""XGBoost model builders.

This module only constructs model instances. It remains task-agnostic and does
not load datasets, preprocess features, train, evaluate, or save artifacts.
"""

from typing import Any

try:
    from xgboost import XGBClassifier, XGBRegressor
except ImportError as exc:  # pragma: no cover - exercised only without xgboost installed
    XGBClassifier = None
    XGBRegressor = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


DEFAULT_CLASSIFIER_PARAMS: dict[str, Any] = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "n_jobs": -1,
}

DEFAULT_REGRESSOR_PARAMS: dict[str, Any] = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "objective": "reg:squarederror",
    "n_jobs": -1,
}


def build_classifier(params: dict[str, Any] | None = None):
    """Build an XGBClassifier."""

    _ensure_xgboost_installed()
    return XGBClassifier(**_merge_params(DEFAULT_CLASSIFIER_PARAMS, params))


def build_regressor(params: dict[str, Any] | None = None):
    """Build an XGBRegressor."""

    _ensure_xgboost_installed()
    return XGBRegressor(**_merge_params(DEFAULT_REGRESSOR_PARAMS, params))


def build_model(
    problem_type: str,
    params: dict[str, Any] | None = None,
):
    """Build an XGBoost model for a classification or regression task."""

    if problem_type == "classification":
        return build_classifier(params)

    if problem_type == "regression":
        return build_regressor(params)

    raise ValueError(f"Unsupported problem type: {problem_type}")


def _ensure_xgboost_installed() -> None:
    if _IMPORT_ERROR is not None:
        raise ImportError("xgboost is required to build XGBoost models.") from _IMPORT_ERROR


def _merge_params(
    defaults: dict[str, Any],
    overrides: dict[str, Any] | None,
) -> dict[str, Any]:
    return {**defaults, **(overrides or {})}
