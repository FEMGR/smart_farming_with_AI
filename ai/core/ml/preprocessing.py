"""
Task-agnostic preprocessing for model training and inference.

The caller provides task-specific configuration such as the target column and
problem type. This module never hard-codes task targets.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

from ai.core.ml.splitting import SplitConfig, split_dataset


@dataclass(frozen=True)
class PreprocessingConfig:
    target_column: str | None = None
    target_candidates: tuple[str, ...] = ()
    problem_type: str | None = None
    categorical_columns: tuple[str, ...] | None = None
    numeric_columns: tuple[str, ...] | None = None
    encode_categorical: bool = True
    encode_target: bool = True
    impute_strategy: str = "median"
    fill_unknown_category_value: int = -1
    drop_empty_columns: bool = True
    classification_unique_threshold: int = 20


@dataclass
class PreprocessingArtifacts:
    target_column: str
    problem_type: str
    feature_columns: list[str]
    numeric_columns: list[str]
    categorical_columns: list[str]
    dropped_columns: list[str] = field(default_factory=list)
    category_mappings: dict[str, dict[str, int]] = field(default_factory=dict)
    target_encoder: LabelEncoder | None = None
    imputer: SimpleImputer | None = None
    config: dict[str, Any] = field(default_factory=dict)


def detect_target(
    df: pd.DataFrame,
    target_column: str | None = None,
    target_candidates: Iterable[str] | None = None,
) -> str:
    """Resolve the configured target column from a DataFrame."""

    if target_column:
        if target_column not in df.columns:
            raise ValueError(f"Target column not found: {target_column}")
        return target_column

    candidates = list(target_candidates or [])
    for column in candidates:
        if column in df.columns:
            return column

    raise ValueError("No target column configured or detected.")


def infer_problem_type(
    y: pd.Series,
    problem_type: str | None = None,
    classification_unique_threshold: int = 20,
) -> str:
    """
    Resolve the ML problem type.

    Explicit configuration wins. Inference is intentionally conservative and
    based only on target dtype/cardinality, not task-specific column names.
    """

    if problem_type:
        if problem_type not in {"classification", "regression"}:
            raise ValueError(f"Unsupported problem type: {problem_type}")
        return problem_type

    if pd.api.types.is_bool_dtype(y) or pd.api.types.is_object_dtype(y) or isinstance(y.dtype, pd.CategoricalDtype):
        return "classification"

    non_null = y.dropna()
    unique_count = non_null.nunique()
    if pd.api.types.is_integer_dtype(non_null) and unique_count <= classification_unique_threshold:
        return "classification"

    return "regression"


def separate_features_target(
    df: pd.DataFrame,
    config: PreprocessingConfig | None = None,
    target_column: str | None = None,
    target_candidates: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series, str, str]:
    """Separate X/y and resolve target/problem type."""

    preprocessing_config = config or PreprocessingConfig(
        target_column=target_column,
        target_candidates=tuple(target_candidates or ()),
    )
    resolved_target = detect_target(
        df,
        target_column=preprocessing_config.target_column,
        target_candidates=preprocessing_config.target_candidates,
    )
    y = df[resolved_target]
    problem_type = infer_problem_type(
        y,
        problem_type=preprocessing_config.problem_type,
        classification_unique_threshold=preprocessing_config.classification_unique_threshold,
    )
    X = df.drop(columns=[resolved_target])
    return X, y, resolved_target, problem_type


def fit_preprocessor(
    X: pd.DataFrame,
    y: pd.Series | None = None,
    config: PreprocessingConfig | None = None,
    target_column: str | None = None,
    problem_type: str | None = None,
) -> tuple[pd.DataFrame, pd.Series | None, PreprocessingArtifacts]:
    """Fit preprocessing transformations and apply them to training data."""

    preprocessing_config = config or PreprocessingConfig(
        target_column=target_column,
        problem_type=problem_type,
    )
    resolved_problem_type = (
        infer_problem_type(
            y,
            problem_type=preprocessing_config.problem_type or problem_type,
            classification_unique_threshold=preprocessing_config.classification_unique_threshold,
        )
        if y is not None
        else (preprocessing_config.problem_type or problem_type or "regression")
    )

    X_prepared, dropped_columns = _drop_empty_columns(X, preprocessing_config)
    categorical_columns = _resolve_categorical_columns(X_prepared, preprocessing_config)
    numeric_columns = _resolve_numeric_columns(X_prepared, preprocessing_config, categorical_columns)

    category_mappings: dict[str, dict[str, int]] = {}
    if preprocessing_config.encode_categorical:
        X_prepared, category_mappings = _fit_encode_categorical_columns(
            X_prepared,
            categorical_columns,
            unknown_value=preprocessing_config.fill_unknown_category_value,
        )

    X_prepared = _coerce_features_to_numeric(X_prepared)
    imputer = SimpleImputer(strategy=preprocessing_config.impute_strategy)
    X_transformed = pd.DataFrame(
        imputer.fit_transform(X_prepared),
        columns=X_prepared.columns,
        index=X_prepared.index,
    )

    target_encoder: LabelEncoder | None = None
    y_transformed = y
    if y is not None and resolved_problem_type == "classification" and preprocessing_config.encode_target:
        target_encoder = LabelEncoder()
        y_transformed = pd.Series(
            target_encoder.fit_transform(y.astype(str)),
            index=y.index,
            name=y.name,
        )

    artifacts = PreprocessingArtifacts(
        target_column=preprocessing_config.target_column or target_column or getattr(y, "name", "") or "",
        problem_type=resolved_problem_type,
        feature_columns=list(X_transformed.columns),
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        dropped_columns=dropped_columns,
        category_mappings=category_mappings,
        target_encoder=target_encoder,
        imputer=imputer,
        config=asdict(preprocessing_config),
    )
    return X_transformed, y_transformed, artifacts


def transform_features(
    X: pd.DataFrame,
    artifacts: PreprocessingArtifacts,
) -> pd.DataFrame:
    """Apply fitted feature preprocessing artifacts to new feature data."""

    X_prepared = X.copy()
    if artifacts.dropped_columns:
        X_prepared = X_prepared.drop(columns=[column for column in artifacts.dropped_columns if column in X_prepared.columns])

    for column in artifacts.feature_columns:
        if column not in X_prepared.columns:
            X_prepared[column] = pd.NA

    X_prepared = X_prepared[artifacts.feature_columns]

    for column, mapping in artifacts.category_mappings.items():
        if column in X_prepared.columns:
            unknown_value = int(artifacts.config.get("fill_unknown_category_value", -1))
            X_prepared[column] = X_prepared[column].astype(str).map(mapping).fillna(unknown_value)

    X_prepared = _coerce_features_to_numeric(X_prepared)

    if artifacts.imputer is None:
        raise ValueError("Preprocessing artifacts do not include a fitted imputer.")

    return pd.DataFrame(
        artifacts.imputer.transform(X_prepared),
        columns=artifacts.feature_columns,
        index=X.index,
    )


def transform_target(
    y: pd.Series,
    artifacts: PreprocessingArtifacts,
) -> pd.Series:
    """Apply the fitted target encoder when one exists."""

    if artifacts.target_encoder is None:
        return y

    return pd.Series(
        artifacts.target_encoder.transform(y.astype(str)),
        index=y.index,
        name=y.name,
    )


def inverse_transform_target(
    values,
    artifacts: PreprocessingArtifacts,
):
    """Convert encoded classification predictions back to original labels."""

    if artifacts.target_encoder is None:
        return values

    return artifacts.target_encoder.inverse_transform(values)


def preprocess_dataset(
    df: pd.DataFrame,
    config: PreprocessingConfig | None = None,
    split_config: SplitConfig | None = None,
    target_column: str | None = None,
    target_candidates: Iterable[str] | None = None,
    problem_type: str | None = None,
) -> dict:
    """
    Convenience end-to-end preprocessing helper for legacy task scripts.

    For new task scripts, prefer calling separate_features_target(),
    split_dataset(), fit_preprocessor(), and transform_features() explicitly.
    """

    preprocessing_config = config or PreprocessingConfig(
        target_column=target_column,
        target_candidates=tuple(target_candidates or ()),
        problem_type=problem_type,
    )
    X, y, resolved_target, resolved_problem_type = separate_features_target(df, preprocessing_config)
    splits = split_dataset(X, y, problem_type=resolved_problem_type, config=split_config)

    train_config = PreprocessingConfig(
        **{
            **asdict(preprocessing_config),
            "target_column": resolved_target,
            "problem_type": resolved_problem_type,
        }
    )
    X_train, y_train, artifacts = fit_preprocessor(
        splits["X_train"],
        splits["y_train"],
        config=train_config,
    )
    X_test = transform_features(splits["X_test"], artifacts)
    y_test = transform_target(splits["y_test"], artifacts)

    result = {
        **splits,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "problem_type": resolved_problem_type,
        "target": resolved_target,
        "features": artifacts.feature_columns,
        "preprocessing": artifacts,
        "artifacts": artifacts,
        "imputer": artifacts.imputer,
        "encoders": {
            "features": artifacts.category_mappings,
            "target": artifacts.target_encoder,
        },
    }

    if "X_validation" in splits:
        result["X_validation"] = transform_features(splits["X_validation"], artifacts)
        result["X_val"] = result["X_validation"]
        result["y_validation"] = transform_target(splits["y_validation"], artifacts)
        result["y_val"] = result["y_validation"]

    return result


def _drop_empty_columns(
    X: pd.DataFrame,
    config: PreprocessingConfig,
) -> tuple[pd.DataFrame, list[str]]:
    if not config.drop_empty_columns:
        return X.copy(), []

    empty_columns = X.columns[X.isna().all()].tolist()
    return X.drop(columns=empty_columns), empty_columns


def _resolve_categorical_columns(
    X: pd.DataFrame,
    config: PreprocessingConfig,
) -> list[str]:
    if config.categorical_columns is not None:
        return [column for column in config.categorical_columns if column in X.columns]

    return list(X.select_dtypes(include=["object", "category", "bool"]).columns)


def _resolve_numeric_columns(
    X: pd.DataFrame,
    config: PreprocessingConfig,
    categorical_columns: list[str],
) -> list[str]:
    if config.numeric_columns is not None:
        return [column for column in config.numeric_columns if column in X.columns]

    categorical = set(categorical_columns)
    return [column for column in X.columns if column not in categorical]


def _fit_encode_categorical_columns(
    X: pd.DataFrame,
    categorical_columns: list[str],
    unknown_value: int,
) -> tuple[pd.DataFrame, dict[str, dict[str, int]]]:
    X_encoded = X.copy()
    mappings: dict[str, dict[str, int]] = {}

    for column in categorical_columns:
        categories = sorted(X_encoded[column].astype(str).fillna("").unique().tolist())
        mapping = {category: index for index, category in enumerate(categories)}
        X_encoded[column] = X_encoded[column].astype(str).map(mapping).fillna(unknown_value)
        mappings[column] = mapping

    return X_encoded, mappings


def _coerce_features_to_numeric(X: pd.DataFrame) -> pd.DataFrame:
    X_numeric = X.copy()
    for column in X_numeric.columns:
        X_numeric[column] = pd.to_numeric(X_numeric[column], errors="coerce")
    return X_numeric
