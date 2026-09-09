"""
Vision Transformer (ViT) architecture wrapper for high-accuracy plant classification.
"""

# ai/models/vision/vit.py

from typing import Literal

import torch.nn as nn
import torchvision.models as models
from torchvision.models import ViT_B_16_Weights, ViT_B_32_Weights

ViTVariant = Literal["vit_b_16", "vit_b_32"]


def build_vit(
    num_classes: int,
    variant: ViTVariant = "vit_b_16",
    pretrained: bool = True,
    freeze_backbone: bool = False,
    dropout_rate: float = 0.2,
) -> nn.Module:
    """
    Build a Vision Transformer (ViT) model for fine-grained classification.

    Args:
        num_classes (int): Number of target classes.
        variant (str): 'vit_b_16' (16x16 patch) or 'vit_b_32' (32x32 patch).
        pretrained (bool): Load ImageNet pre-trained weights.
        freeze_backbone (bool): If True, freezes transformer encoder layers.
        dropout_rate (float): Dropout rate in classification head.

    Returns:
        nn.Module: Configured Vision Transformer PyTorch model.
    """
    if variant == "vit_b_16":
        weights = ViT_B_16_Weights.DEFAULT if pretrained else None
        model = models.vit_b_16(weights=weights)
    elif variant == "vit_b_32":
        weights = ViT_B_32_Weights.DEFAULT if pretrained else None
        model = models.vit_b_32(weights=weights)
    else:
        raise ValueError(f"Unsupported ViT variant: {variant}")

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Replace classification head ('heads.head' in torchvision ViT)
    in_features = model.heads.head.in_features
    model.heads.head = nn.Sequential(
        nn.Dropout(p=dropout_rate),
        nn.Linear(in_features, num_classes),
    )

    return model
