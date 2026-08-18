"""Gradient Boosting model builders.

This module only constructs model instances. Dataset loading, preprocessing,
training, evaluation, and persistence belong outside model builder modules.
"""

from typing import Any

from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor

from ai.core.constants import (
    DEFAULT_GB_CLASSIFIER_PARAMS as DEFAULT_CLASSIFIER_PARAMS,
    DEFAULT_GB_REGRESSOR_PARAMS as DEFAULT_REGRESSOR_PARAMS,
)


def build_classifier(params: dict[str, Any] | None = None) -> GradientBoostingClassifier:
    """Build a GradientBoostingClassifier."""

    return GradientBoostingClassifier(**_merge_params(DEFAULT_CLASSIFIER_PARAMS, params))


def build_regressor(params: dict[str, Any] | None = None) -> GradientBoostingRegressor:
    """Build a GradientBoostingRegressor."""

    return GradientBoostingRegressor(**_merge_params(DEFAULT_REGRESSOR_PARAMS, params))


def build_model(
    problem_type: str,
    params: dict[str, Any] | None = None,
) -> GradientBoostingClassifier | GradientBoostingRegressor:
    """Build a Gradient Boosting model for a classification or regression task."""

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
