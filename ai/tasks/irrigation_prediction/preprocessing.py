"""
Purpose
-------
Shared preprocessing pipeline for irrigation prediction models.

Supported models
----------------
- Random Forest
- XGBoost
- Gradient Boosting
- Logistic Regression
- Future PyTorch models

Responsibilities
----------------
1. Load dataset
2. Detect target column
3. Determine ML task
4. Encode categorical variables
5. Handle missing values
6. Split train/test sets
7. Save preprocessing artifacts
"""

# ai/tasks/irrigation_prediction/preprocessing.py

from pathlib import Path
import joblib

import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ==========================================================
# Paths
# ==========================================================

TASK_FOLDER = Path(__file__).resolve().parent

MODEL_FOLDER = TASK_FOLDER / "saved_models"
MODEL_FOLDER.mkdir(parents=True, exist_ok=True)

IMPUTER_FILE = MODEL_FOLDER / "imputer.pkl"
ENCODER_FILE = MODEL_FOLDER / "label_encoders.pkl"

# ==========================================================
# Configuration
# ==========================================================

TARGET_CANDIDATES = [
    "watering_needed",
    "watering_amount_liters",
]

TEST_SIZE = 0.20
RANDOM_STATE = 42

# ==========================================================
# Detect Target
# ==========================================================


def detect_target(df: pd.DataFrame) -> str:

    for column in TARGET_CANDIDATES:
        if column in df.columns:
            return column

    raise ValueError(f"No target found.\nExpected one of {TARGET_CANDIDATES}")


# ==========================================================
# Determine ML Task
# ==========================================================


def detect_problem_type(
    df: pd.DataFrame,
    target: str,
) -> str:
    """
    Returns

    classification
    regression
    """

    if target == "watering_needed":
        return "classification"

    return "regression"


# ==========================================================
# Encode categorical variables
# ==========================================================


def encode_features(
    X: pd.DataFrame,
):
    """
    Encode all categorical columns.
    """

    encoders = {}

    categorical_columns = X.select_dtypes(include=["object", "category"]).columns

    X = X.copy()

    for column in categorical_columns:

        encoder = LabelEncoder()

        X[column] = encoder.fit_transform(X[column].astype(str))

        encoders[column] = encoder

    return X, encoders


# ==========================================================
# Encode target
# ==========================================================


def encode_target(
    y: pd.Series,
    problem_type: str,
    encoders: dict,
):
    """
    Encode only classification targets.
    """

    if problem_type == "classification":

        encoder = LabelEncoder()

        y = encoder.fit_transform(y.astype(str))

        encoders["target"] = encoder

    return y


# ==========================================================
# Missing values
# ==========================================================


def impute_missing_values(
    X: pd.DataFrame,
):
    """
    Replace missing values using median.
    """

    # Remove columns that are completely empty
    empty_columns = X.columns[X.isna().all()].tolist()

    if empty_columns:
        print("\nRemoving completely empty columns:")
        print(empty_columns)

        X = X.drop(columns=empty_columns)

    imputer = SimpleImputer(strategy="median")

    X = pd.DataFrame(
        imputer.fit_transform(X),
        columns=X.columns,
        index=X.index,
    )

    return X, imputer


# ==========================================================
# Save preprocessing artifacts
# ==========================================================


def save_preprocessing(
    imputer,
    encoders,
):

    joblib.dump(
        imputer,
        IMPUTER_FILE,
    )

    joblib.dump(
        encoders,
        ENCODER_FILE,
    )


# ==========================================================
# Main preprocessing
# ==========================================================


def preprocess_dataset(
    df: pd.DataFrame,
):
    """
    Complete preprocessing pipeline.
    """

    target = detect_target(df)

    problem_type = detect_problem_type(
        df,
        target,
    )

    X = df.drop(columns=[target])

    y = df[target]

    X, encoders = encode_features(X)

    y = encode_target(
        y,
        problem_type,
        encoders,
    )

    X, imputer = impute_missing_values(X)

    save_preprocessing(
        imputer,
        encoders,
    )

    split_args = dict(
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    if problem_type == "classification":

        split_args["stratify"] = y

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        **split_args,
    )

    return {
        "problem_type": problem_type,
        "target": target,
        "features": list(X.columns),
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "encoders": encoders,
        "imputer": imputer,
    }
