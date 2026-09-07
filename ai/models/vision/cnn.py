"""
Custom Convolutional Neural Network (CNN) architecture for agricultural vision tasks.
"""

# ai/models/vision/cnn.py

import torch
import torch.nn as nn


class PlantCNN(nn.Module):
    """
    Custom 4-stage ConvNet designed for agricultural leaf/crop image classification.

    Includes Batch Normalization and Dropout for regularization against overfitting
    on small to medium field datasets.
    """

    def __init__(
        self,
        num_classes: int = 10,
        in_channels: int = 3,
        dropout_rate: float = 0.3,
    ) -> None:
        super().__init__()

        # Conv Block 1: Input (3, 224, 224) -> Output (32, 112, 112)
        self.block1 = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # Conv Block 2: Output (64, 56, 56)
        self.block2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # Conv Block 3: Output (128, 28, 28)
        self.block3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # Conv Block 4: Output (256, 14, 14)
        self.block4 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # Global Average Pooling -> (256, 1, 1)
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

        # Classification Head
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        x = self.global_pool(x)
        return self.classifier(x)


def build_custom_cnn(num_classes: int, in_channels: int = 3, dropout_rate: float = 0.3) -> PlantCNN:
    """Factory helper for PlantCNN."""
    return PlantCNN(num_classes=num_classes, in_channels=in_channels, dropout_rate=dropout_rate)
