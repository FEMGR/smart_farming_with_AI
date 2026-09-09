"""
This module imports your custom field augmentations from
.augmentation and standard PyTorch transforms, assembling them
into standardized training and evaluation pipelines.
"""

# ai/core/vision/transforms.py

import torch
from typing import Tuple
import torchvision.transforms.v2 as T
from .augmentation import RandomShadow, RandomFieldNoise, ImageColorJitter

# Standard ImageNet normalization parameters
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def if_tensor_given():
    """Helper lambda check to ensure PIL format prior to custom filter execution."""
    return T.Lambda(lambda x: x if isinstance(x, torch.Tensor) is False else T.ToPILImage()(x))


def simulate_augmentations(img_size: Tuple[int, int] = (224, 224), mean: list = IMAGENET_MEAN, std: list = IMAGENET_STD) -> T.Compose:
    # Simulates field variations like changing daylight, camera angles, and orientation.
    return T.Compose(
        [
            T.ToPILImage(),
            if_tensor_given(),  # Ensures PIL compatibility for custom filters
            T.Resize(img_size),
            # Geometric augmentations (plants/diseases/pests appear in any orientation)
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.5),
            T.RandomRotation(degrees=45),
            T.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.9, 1.1)),
            # Field-specific lighting and noise augmentations
            ImageColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
            RandomShadow(p=0.4),
            RandomFieldNoise(p=0.3),
            # Tensor conversion and normalization
            T.ToTensor(),
            T.Normalize(mean=mean, std=std),
        ]
    )


def prepare_for_transformation(img_size: Tuple[int, int] = (224, 224), mean: list = IMAGENET_MEAN, std: list = IMAGENET_STD) -> T.Compose:
    """
    prepare images for validation, testing, and production inference.
    """
    return T.Compose([T.Resize(img_size), T.ToTensor(), T.Normalize(mean=mean, std=std)])


def get_image_transforms(img_size: int = 224, is_train: bool = True) -> T.Compose:
    """
    Unified entry point called by vision/dataset.py.
    """
    size_tuple = (img_size, img_size)
    if is_train:
        return simulate_augmentations(img_size=size_tuple)
    return prepare_for_transformation(img_size=size_tuple)
