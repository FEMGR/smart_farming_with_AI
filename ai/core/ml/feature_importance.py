"""Feature-importance extraction and persistence."""

from pathlib import Path

import pandas as pd

from ai.core.file_status import write_dataframe_csv_with_status


def get_feature_importance(
    model,
    feature_names: list[str],
    importance_type: str = "gain",
) -> pd.DataFrame:
    """
    Extract feature importance for models that expose it.

    Supports common scikit-learn estimators and XGBoost sklearn wrappers.
    """

    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
        return _importance_frame(feature_names, values)

    if hasattr(model, "get_booster"):
        booster_scores = model.get_booster().get_score(importance_type=importance_type)
        values = [_score_for_feature(booster_scores, feature, index) for index, feature in enumerate(feature_names)]
        return _importance_frame(feature_names, values)

    raise ValueError("Model does not expose feature importance.")


def save_feature_importance(
    importance: pd.DataFrame,
    path: str | Path,
) -> Path:
    """Save feature importance as CSV."""

    output_path = Path(path)
    return write_dataframe_csv_with_status(
        importance,
        output_path,
        description="feature importance",
    )


def extract_and_save_feature_importance(
    model,
    feature_names: list[str],
    path: str | Path,
    importance_type: str = "gain",
) -> Path:
    """Extract feature importance and save it as CSV."""

    importance = get_feature_importance(model, feature_names, importance_type=importance_type)
    return save_feature_importance(importance, path)


def _importance_frame(feature_names: list[str], values) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": list(values),
        }
    )
    total = frame["importance"].sum()
    frame["importance_normalized"] = frame["importance"] / total if total else 0
    return frame.sort_values("importance", ascending=False).reset_index(drop=True)


def _score_for_feature(scores: dict, feature: str, index: int):
    return scores.get(feature, scores.get(f"f{index}", 0))
