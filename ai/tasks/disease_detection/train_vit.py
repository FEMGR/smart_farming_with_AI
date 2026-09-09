"""Train the disease Vision Transformer (ViT) model using the vision training task."""

# ai/tasks/disease_detection/train_vit.py

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.tasks.disease_detection.train import train_selected_model  # noqa: E402


def train():
    """Compatibility entry point for the ViT-only training command."""
    return train_selected_model(model_name="vit_b_16")


if __name__ == "__main__":
    train()
