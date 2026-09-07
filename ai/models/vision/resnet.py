"""
ResNet backbone wrapper for Transfer Learning in agricultural vision tasks.
"""

# ai/models/vision/resnet.py

from typing import Literal

import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet18_Weights, ResNet34_Weights, ResNet50_Weights

ResNetVariant = Literal["resnet18", "resnet34", "resnet50"]


def build_resnet(
    num_classes: int,
    variant: ResNetVariant = "resnet18",
    pretrained: bool = True,
    freeze_backbone: bool = False,
    dropout_rate: float = 0.2,
) -> nn.Module:
    """
    Build a ResNet model with a custom classification head.

    Args:
        num_classes (int): Number of target classes (e.g. 10 plant diseases).
        variant (str): Options: 'resnet18', 'resnet34', or 'resnet50'.
        pretrained (bool): Whether to load ImageNet pre-trained weights.
        freeze_backbone (bool): If True, freezes feature extractor parameters for fast fine-tuning.
        dropout_rate (float): Dropout probability before final linear layer.

    Returns:
        nn.Module: Configured ResNet PyTorch model.
    """
    if variant == "resnet18":
        weights = ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
    elif variant == "resnet34":
        weights = ResNet34_Weights.DEFAULT if pretrained else None
        model = models.resnet34(weights=weights)
    elif variant == "resnet50":
        weights = ResNet50_Weights.DEFAULT if pretrained else None
        model = models.resnet50(weights=weights)
    else:
        raise ValueError(f"Unsupported ResNet variant: {variant}")

    # Freeze convolutional feature extractor if requested
    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Replace the FC classification head
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(p=dropout_rate),
        nn.Linear(in_features, num_classes),
    )

    return model
