"""Shared prediction and inference helpers."""

from typing import Any

import pandas as pd

from ai.core.ml.preprocessing import PreprocessingArtifacts, inverse_transform_target, transform_features


def prepare_input(
    records: pd.DataFrame | dict[str, Any] | list[dict[str, Any]],
    preprocessing_artifacts: PreprocessingArtifacts | None = None,
) -> pd.DataFrame:
    """Convert prediction input records into a DataFrame and preprocess them."""

    if isinstance(records, pd.DataFrame):
        df = records.copy()
    elif isinstance(records, dict):
        df = pd.DataFrame([records])
    else:
        df = pd.DataFrame(records)

    if preprocessing_artifacts is None:
        return df

    return transform_features(df, preprocessing_artifacts)


def predict(
    model,
    records: pd.DataFrame | dict[str, Any] | list[dict[str, Any]],
    preprocessing_artifacts: PreprocessingArtifacts | None = None,
    inverse_transform: bool = True,
):
    """Run model prediction with optional preprocessing and label decoding."""

    X = prepare_input(records, preprocessing_artifacts)
    predictions = model.predict(X)

    if inverse_transform and preprocessing_artifacts is not None:
        predictions = inverse_transform_target(predictions, preprocessing_artifacts)

    return predictions


def predict_with_confidence(
    model,
    records: pd.DataFrame | dict[str, Any] | list[dict[str, Any]],
    preprocessing_artifacts: PreprocessingArtifacts | None = None,
    inverse_transform: bool = True,
) -> dict[str, Any]:
    """Return predictions plus probabilities or decision scores when available."""

    X = prepare_input(records, preprocessing_artifacts)
    predictions = model.predict(X)
    output_predictions = predictions

    if inverse_transform and preprocessing_artifacts is not None:
        output_predictions = inverse_transform_target(predictions, preprocessing_artifacts)

    result: dict[str, Any] = {"predictions": _to_list(output_predictions)}

    if hasattr(model, "predict_proba"):
        result["probabilities"] = _to_list(model.predict_proba(X))
    elif hasattr(model, "decision_function"):
        result["scores"] = _to_list(model.decision_function(X))

    return result


def _to_list(values):
    if hasattr(values, "tolist"):
        return values.tolist()
    return values
