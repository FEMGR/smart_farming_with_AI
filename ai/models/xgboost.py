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


from ai.core.constants import (
    DEFAULT_XGB_CLASSIFIER_PARAMS as DEFAULT_CLASSIFIER_PARAMS,
    DEFAULT_XGB_REGRESSOR_PARAMS as DEFAULT_REGRESSOR_PARAMS,
)


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
