"""
Baseline Random Forest model for irrigation prediction.

Input
-----
ai/datasets/processed/irrigation_training.csv

Output
------
saved_models/
    random_forest_irrigation.pkl
    label_encoders.pkl

evaluation/
    random_forest_metrics.json
"""

# ai/tasks/irrigation_prediction/train_random_forest.py

from pathlib import Path
import json
from datetime import datetime

import joblib
import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
)

from preprocessing import preprocess_dataset

# ==========================================================
# Paths
# ==========================================================

TASK_FOLDER = Path(__file__).resolve().parent

DATASET = TASK_FOLDER.parent.parent / "datasets" / "processed" / "irrigation_training.csv"

MODEL_FOLDER = TASK_FOLDER / "saved_models"
MODEL_FOLDER.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_FOLDER / "random_forest.pkl"
METADATA_FILE = MODEL_FOLDER / "metadata.json"

# ==========================================================
# Configuration
# ==========================================================

CLASSIFIER_PARAMS = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "random_state": 42,
    "n_jobs": -1,
    "class_weight": "balanced",
}

REGRESSOR_PARAMS = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "random_state": 42,
    "n_jobs": -1,
}

# ==========================================================
# Model Builder
# ==========================================================


def build_model(problem_type: str):

    if problem_type == "classification":

        return RandomForestClassifier(**CLASSIFIER_PARAMS)

    return RandomForestRegressor(**REGRESSOR_PARAMS)


# ==========================================================
# Metadata
# ==========================================================


def save_metadata(data: dict):

    metadata = {
        "algorithm": "Random Forest",
        "task": "irrigation_prediction",
        "problem_type": data["problem_type"],
        "target": data["target"],
        "features": data["features"],
        "training_rows": len(data["X_train"]),
        "testing_rows": len(data["X_test"]),
        "created": datetime.now().isoformat(),
    }

    with open(METADATA_FILE, "w") as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )


# ==========================================================
# Save Model
# ==========================================================


def save_model(model):

    joblib.dump(
        model,
        MODEL_FILE,
    )


# ==========================================================
# Train
# ==========================================================


def train():

    print("=" * 60)
    print("Random Forest Training")
    print("=" * 60)

    print("\nLoading dataset...")

    df = pd.read_csv(DATASET)

    print(f"Rows : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    print("\nPreprocessing...")

    data = preprocess_dataset(df)

    print(f"Problem Type : {data['problem_type']}")
    print(f"Target       : {data['target']}")

    print("\nBuilding model...")

    model = build_model(data["problem_type"])

    print("Training...")

    model.fit(
        data["X_train"],
        data["y_train"],
    )

    print("Training complete.")

    save_model(model)

    save_metadata(data)

    print("\nModel saved:")
    print(MODEL_FILE)

    print("\nMetadata saved:")
    print(METADATA_FILE)

    return {
        "model": model,
        **data,
    }


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    train()
