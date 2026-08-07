"""Disease prediction task configuration."""

from pathlib import Path

TASK_NAME = "disease_prediction"
TASK_LABEL = "Disease Prediction"

TASK_FOLDER = Path(__file__).resolve().parent
AI_ROOT = TASK_FOLDER.parents[1]

DATASET_PATH = AI_ROOT / "datasets" / "processed" / "disease_training.csv"
ARTIFACT_DIR = AI_ROOT / "artifacts" / TASK_NAME

TARGET_COLUMN = "disease_name"
TARGET_CANDIDATES = (
    "disease_name",
    "disease_risk",
)

PROBLEM_TYPE = "classification"
TEST_SIZE = 0.20
RANDOM_STATE = 42

MODELS = {
    "xgboost": {
        "algorithm": "XGBoost",
        "primary_metric": "f1",
        "greater_is_better": True,
        "enabled": True,
        "params": {},
    },
    "pytorch_mlp": {
        "algorithm": "PyTorch MLP",
        "primary_metric": "f1",
        "greater_is_better": True,
        "enabled": False,
        "status": "prepared_for_later",
        "reason": "PyTorch-specific training loop is not implemented yet.",
        "params": {},
    },
}

MODEL_ORDER = (
    "xgboost",
    "pytorch_mlp",
)
