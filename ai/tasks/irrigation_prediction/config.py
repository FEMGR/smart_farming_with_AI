"""Irrigation prediction task configuration."""

from pathlib import Path

TASK_NAME = "irrigation_prediction"
TASK_LABEL = "Irrigation Prediction"

TASK_FOLDER = Path(__file__).resolve().parent
AI_ROOT = TASK_FOLDER.parents[1]

DATASET_PATH = AI_ROOT / "datasets" / "processed" / "irrigation_training.csv"
ARTIFACT_DIR = AI_ROOT / "artifacts" / TASK_NAME

TARGET_COLUMN = "watering_needed"
TARGET_CANDIDATES = (
    "watering_needed",
    "watering_amount_liters",
)

PROBLEM_TYPE = "classification"
TEST_SIZE = 0.20
RANDOM_STATE = 42

MODELS = {
    "random_forest": {
        "algorithm": "Random Forest",
        "primary_metric": "f1",
        "greater_is_better": True,
        "params": {},
    },
    "xgboost": {
        "algorithm": "XGBoost",
        "primary_metric": "f1",
        "greater_is_better": True,
        "params": {},
    },
}

MODEL_ORDER = (
    "random_forest",
    "xgboost",
)
