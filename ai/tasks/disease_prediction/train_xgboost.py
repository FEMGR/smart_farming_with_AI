"""Train the disease XGBoost model using the shared ML pipeline."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.tasks.disease_prediction.train import train_selected_model  # noqa: E402


def train():
    """Compatibility entry point for the XGBoost-only training command."""

    return train_selected_model("xgboost")


if __name__ == "__main__":
    train()
