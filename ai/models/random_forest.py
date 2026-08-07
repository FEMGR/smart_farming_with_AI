"""Random Forest model builders.

This module only constructs model instances. Dataset loading, preprocessing,
training, evaluation, and persistence belong to the shared ML core and task
orchestration layers.
"""

from typing import Any

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

DEFAULT_CLASSIFIER_PARAMS: dict[str, Any] = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "random_state": 42,
    "n_jobs": -1,
    "class_weight": "balanced",
}

DEFAULT_REGRESSOR_PARAMS: dict[str, Any] = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "random_state": 42,
    "n_jobs": -1,
}


def build_classifier(params: dict[str, Any] | None = None) -> RandomForestClassifier:
    """Build a RandomForestClassifier."""

    return RandomForestClassifier(**_merge_params(DEFAULT_CLASSIFIER_PARAMS, params))


def build_regressor(params: dict[str, Any] | None = None) -> RandomForestRegressor:
    """Build a RandomForestRegressor."""

    return RandomForestRegressor(**_merge_params(DEFAULT_REGRESSOR_PARAMS, params))


def build_model(
    problem_type: str,
    params: dict[str, Any] | None = None,
) -> RandomForestClassifier | RandomForestRegressor:
    """Build a Random Forest model for a classification or regression task."""

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
