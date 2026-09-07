"""Train the disease ResNet18 vision model using the shared vision pipeline."""

# ai/tasks/disease_detection/train_resnet.py

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.tasks.disease_detection.train import train_selected_model  # noqa: E402


def train():
    """Compatibility entry point for the ResNet18-only training command."""
    return train_selected_model("resnet18")


if __name__ == "__main__":
    train()
