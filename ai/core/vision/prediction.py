"""
Image-specific prediction and inference helpers.

Primary use:
    Plant Identification
    Disease Detection
    Pest Detection
"""

# ai/core/vision/prediction.py

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from PIL import Image
import torch
import torch.nn as nn

from ai.core.vision.transforms import get_image_transforms
from ai.core.ml.pytorch.device import resolve_device


def load_image(image_input: Union[str, Path, Image.Image]) -> Image.Image:
    """Load and ensure an image is in RGB format."""
    if isinstance(image_input, (str, Path)):
        path = Path(image_input)
        if not path.exists():
            raise FileNotFoundError(f"Image not found at path: {path}")
        with open(path, "rb") as f:
            return Image.open(f).convert("RGB")
    elif isinstance(image_input, Image.Image):
        return image_input.convert("RGB")
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")


def predict_image(
    model: nn.Module,
    image_input: Union[str, Path, Image.Image],
    transform: Optional[Any] = None,
    class_map: Optional[Union[Dict[int, str], Dict[str, int]]] = None,
    device: Optional[Union[str, torch.device]] = None,
    img_size: int = 224,
) -> Dict[str, Any]:
    """
    Run prediction on a single image input.

    Args:
        model (nn.Module): Trained PyTorch vision model.
        image_input (str | Path | PIL.Image): File path or PIL Image instance.
        transform (callable, optional): Torchvision transform pipeline.
                                         Defaults to evaluation transform if None.
        class_map (dict, optional): Mapping dict between class index and label string.
        device (str | torch.device, optional): Target device for evaluation.
        img_size (int): Target image resolution if default transform is built.

    Returns:
        dict: Summary containing predicted class index, label name, confidence,
              and all class probabilities.
    """
    target_device = resolve_device(device)
    model = model.to(target_device)
    model.eval()

    # Normalize class_map to {int_index: str_label}
    idx_to_class = {}
    if class_map:
        first_key = next(iter(class_map.keys()))
        if isinstance(first_key, str):
            idx_to_class = {v: k for k, v in class_map.items()}
        else:
            idx_to_class = class_map

    # Load and preprocess image
    image = load_image(image_input)
    if transform is None:
        transform = get_image_transforms(img_size=img_size)

    # Convert to Tensor and add batch dimension (1, C, H, W)
    tensor_input = transform(image).unsqueeze(0).to(target_device)

    with torch.no_grad():
        outputs = model(tensor_input)
        probabilities = torch.softmax(outputs, dim=1).squeeze(0)
        confidence, pred_idx_tensor = torch.max(probabilities, dim=0)

    pred_idx = int(pred_idx_tensor.item())
    pred_confidence = float(confidence.item())
    pred_label = idx_to_class.get(pred_idx, f"Class {pred_idx}")

    return {
        "class_id": pred_idx,
        "label": pred_label,
        "confidence": round(pred_confidence, 4),
        "probabilities": {idx_to_class.get(i, f"Class {i}"): round(float(prob.item()), 4) for i, prob in enumerate(probabilities)},
    }


def predict_image_batch(
    model: nn.Module,
    images: List[Union[str, Path, Image.Image]],
    transform: Optional[Any] = None,
    class_map: Optional[Union[Dict[int, str], Dict[str, int]]] = None,
    device: Optional[Union[str, torch.device]] = None,
    img_size: int = 224,
) -> List[Dict[str, Any]]:
    """
    Run batch inference on a list of images.
    """
    target_device = resolve_device(device)
    model = model.to(target_device)
    model.eval()

    if transform is None:
        transform = get_image_transforms(img_size=img_size)

    # Process all images into a single batch tensor
    tensors = [transform(load_image(img)) for img in images]
    batch_tensor = torch.stack(tensors).to(target_device)

    # Normalize class map
    idx_to_class = {}
    if class_map:
        first_key = next(iter(class_map.keys()))
        if isinstance(first_key, str):
            idx_to_class = {v: k for k, v in class_map.items()}
        else:
            idx_to_class = class_map

    with torch.no_grad():
        outputs = model(batch_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidences, pred_indices = torch.max(probabilities, dim=1)

    results = []
    for i in range(len(images)):
        p_idx = int(pred_indices[i].item())
        conf = float(confidences[i].item())
        p_label = idx_to_class.get(p_idx, f"Class {p_idx}")

        results.append(
            {
                "class_id": p_idx,
                "label": p_label,
                "confidence": round(conf, 4),
                "probabilities": {idx_to_class.get(j, f"Class {j}"): round(float(prob.item()), 4) for j, prob in enumerate(probabilities[i])},
            }
        )

    return results
