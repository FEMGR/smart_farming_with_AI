"""
Vision Prediction Layer for trained Smart Farming Computer Vision models.

This module loads PyTorch vision model checkpoints (.pth) alongside class maps
and metadata artifacts, preprocesses input images (PIL, path, or bytes), and
generates disease and pest predictions with confidence breakdown scores.
"""

# ai/inference/vision_prediction.py

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Union

import torch
from PIL import Image

from ai.core.constants import ARTIFACTS_DIR  # noqa: E402
from ai.core.ml.pytorch.device import resolve_device  # noqa: E402
from ai.core.vision.transforms import get_image_transforms  # noqa: E402
from ai.models.vision import build_custom_cnn, build_resnet, build_vit  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SUPPORTED_VISION_TASKS = (
    "disease_detection",
    "pest_detection",
)

VISION_TASK_ALIASES = {
    "disease_vision": "disease_detection",
    "pest_vision": "pest_detection",
    "disease": "disease_detection",
    "pest": "pest_detection",
}


@dataclass
class VisionPredictionResult:
    task: str
    prediction: str
    class_index: int
    confidence: float
    confidence_percentage: str
    breakdown: list[dict[str, Any]]
    artifact_dir: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VisionPredictionLayer:
    """Load PyTorch vision artifacts and generate image-based classification predictions."""

    def __init__(self, artifacts_dir: str | Path = ARTIFACTS_DIR) -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.device = resolve_device()
        self._loaded_engines: dict[str, dict[str, Any]] = {}

    def predict_image(
        self,
        task: str,
        image_input: Union[str, Path, Image.Image],
        artifact_dir: str | Path | None = None,
        top_k: int = 3,
    ) -> VisionPredictionResult:
        """
        Run inference on a single image file or PIL Image object.

        Args:
            task: Task name or alias (e.g., 'disease_detection', 'pest_detection')
            image_input: Path to image file or PIL Image object
            artifact_dir: Optional override path to artifact directory
            top_k: Number of candidate classes to return in breakdown

        Returns:
            VisionPredictionResult dataclass instance
        """
        task_name = normalize_vision_task_name(task)
        resolved_artifact_dir = Path(artifact_dir) if artifact_dir else self.artifacts_dir / task_name / "best_model"

        engine = self._get_or_load_engine(resolved_artifact_dir)
        image = self._preprocess_input_image(image_input)

        # Apply evaluation transform and add batch dimension [1, C, H, W]
        tensor = engine["transform"](image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = engine["model"](tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]

        top_probs, top_indices = torch.topk(probabilities, k=min(top_k, len(engine["idx_to_class"])))

        predicted_idx = top_indices[0].item()
        confidence = top_probs[0].item()
        predicted_label = engine["idx_to_class"].get(predicted_idx, f"Class_{predicted_idx}")

        breakdown = [
            {
                "class_index": idx,
                "label": engine["idx_to_class"].get(idx, f"Class_{idx}"),
                "confidence": round(prob, 4),
            }
            for prob, idx in zip(top_probs.tolist(), top_indices.tolist())
        ]

        return VisionPredictionResult(
            task=task_name,
            prediction=predicted_label,
            class_index=predicted_idx,
            confidence=round(confidence, 4),
            confidence_percentage=f"{confidence * 100:.2f}%",
            breakdown=breakdown,
            artifact_dir=str(resolved_artifact_dir),
        )

    def _get_or_load_engine(self, artifact_dir: Path) -> dict[str, Any]:
        """Cache and manage loaded models in memory."""
        cache_key = str(artifact_dir)
        if cache_key in self._loaded_engines:
            return self._loaded_engines[cache_key]

        if not artifact_dir.exists():
            raise FileNotFoundError(f"Vision artifact directory not found: {artifact_dir}")

        # Locate Checkpoint File
        model_path = artifact_dir / "model.pth"
        if not model_path.exists():
            model_path = artifact_dir / "best_vision_model.pth"

        if not model_path.exists():
            raise FileNotFoundError(f"No PyTorch vision weights (.pth) found in: {artifact_dir}")

        # Load Metadata and Class Mapping
        metadata_path = artifact_dir / "metadata.json"
        class_map_path = artifact_dir / "class_map.json"

        idx_to_class: dict[int, str] = {}
        img_size = 224
        model_name = "resnet18"

        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                num_classes = meta.get("num_classes")
                model_name = meta.get("model_name", "resnet18")
                img_size = meta.get("img_size", 224)

                if "idx_to_class" in meta:
                    idx_to_class = {int(k): v for k, v in meta["idx_to_class"].items()}

        elif class_map_path.exists():
            with open(class_map_path, "r", encoding="utf-8") as f:
                cmap = json.load(f)
                idx_to_class = {int(k): v for k, v in cmap["idx_to_class"].items()}
                num_classes = len(idx_to_class)
        else:
            raise FileNotFoundError(f"No metadata.json or class_map.json found in: {artifact_dir}")

        # Re-build Model Architecture
        model = build_vision_architecture(model_name, num_classes)

        # Load Weights
        checkpoint = torch.load(model_path, map_location=self.device)
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            model.load_state_dict(checkpoint["state_dict"])
        else:
            model.load_state_dict(checkpoint)

        model.to(self.device)
        model.eval()

        engine = {
            "model": model,
            "idx_to_class": idx_to_class,
            "transform": get_image_transforms(img_size=img_size),
        }
        self._loaded_engines[cache_key] = engine
        return engine

    def _preprocess_input_image(self, image_input: Union[str, Path, Image.Image]) -> Image.Image:
        """Ensure input is converted into RGB PIL Image format."""
        if isinstance(image_input, (str, Path)):
            path = Path(image_input)
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {path}")
            return Image.open(path).convert("RGB")
        elif isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")


# =========================================================
# HELPER FUNCTIONS & CONVENIENCE APIS
# =========================================================


def predict_vision_task(
    task: str,
    image_input: Union[str, Path, Image.Image],
    artifact_dir: str | Path | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    """Convenience function for single image prediction."""
    return (
        VisionPredictionLayer()
        .predict_image(
            task=task,
            image_input=image_input,
            artifact_dir=artifact_dir,
            top_k=top_k,
        )
        .to_dict()
    )


def build_vision_architecture(model_name: str, num_classes: int) -> torch.nn.Module:
    """Instantiate correct vision model architecture matching model_name."""
    name = model_name.lower()
    if "resnet50" in name:
        return build_resnet(num_classes=num_classes, variant="resnet50", pretrained=False)
    elif "resnet" in name:
        return build_resnet(num_classes=num_classes, variant="resnet18", pretrained=False)
    elif "vit" in name:
        return build_vit(num_classes=num_classes, variant="vit_b_16", pretrained=False)
    elif "custom_cnn" in name or "cnn" in name:
        return build_custom_cnn(num_classes=num_classes)
    else:
        return build_resnet(num_classes=num_classes, variant="resnet18", pretrained=False)


def normalize_vision_task_name(task: str) -> str:
    """Normalize aliases for vision tasks."""
    task_name = VISION_TASK_ALIASES.get(task, task)
    if task_name not in SUPPORTED_VISION_TASKS:
        raise ValueError(f"Unsupported vision task: '{task}'. Supported vision tasks: {SUPPORTED_VISION_TASKS}")
    return task_name
