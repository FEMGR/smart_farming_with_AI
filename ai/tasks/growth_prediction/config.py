"""Growth prediction task configuration."""

from pathlib import Path

TASK_NAME = "growth_prediction"
TASK_LABEL = "Growth Prediction"

TASK_FOLDER = Path(__file__).resolve().parent
AI_ROOT = TASK_FOLDER.parents[1]

DATASET_PATH = AI_ROOT / "datasets" / "processed" / "growth_training.csv"
ARTIFACT_DIR = AI_ROOT / "artifacts" / TASK_NAME

TARGET_COLUMN = "future_height_cm"
TARGET_CANDIDATES = (
    "future_height_cm",
    "growth_rate",
)

PROBLEM_TYPE = "regression"
TEST_SIZE = 0.20
RANDOM_STATE = 42

MODELS = {
    "random_forest": {
        "algorithm": "Random Forest",
        "primary_metric": "rmse",
        "greater_is_better": False,
        "enabled": True,
        "params": {},
    },
    "pytorch_mlp": {
        "algorithm": "PyTorch MLP",
        "primary_metric": "rmse",
        "greater_is_better": False,
        "enabled": False,
        "status": "prepared_for_later",
        "reason": "PyTorch-specific training loop is not implemented yet.",
        "params": {},
    },
}

MODEL_ORDER = (
    "random_forest",
    "pytorch_mlp",
)
