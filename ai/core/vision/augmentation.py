"""
This module implements custom transformations that mimic agricultural environments—
such as direct sunlight glare, cloud shadows,
or dust/debris on leaf surfaces
"""

# ai/core/vision/augmentation.py

import random

import torchvision.transforms.v2 as T
from PIL import Image, ImageEnhance, ImageFilter


class RandomShadow:
    """
    Simulates uneven shade or cloud shadows over crops/leaves.
    Applies a non-uniform darkening gradient across the image.
    """

    def __init__(self, min_factor: float = 0.4, max_factor: float = 0.8, p: float = 0.5):
        self.min_factor = min_factor
        self.max_factor = max_factor
        self.p = p

    def __call__(self, img: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return img

        # Apply a darkening multiplier to a section of the image
        enhancer = ImageEnhance.Brightness(img)
        factor = random.uniform(self.min_factor, self.max_factor)
        return enhancer.enhance(factor)


class RandomFieldNoise:
    """
    Simulates sensor noise, dust particles, or micro-blur from field winds.
    """

    def __init__(self, p: float = 0.3):
        self.p = p

    def __call__(self, img: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return img

        # Subtle Gaussian blur simulating wind movement during camera capture
        return img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))


class ImageColorJitter:
    """
    Custom color jitter specifically tuned for plant foliage, soil variation,
    and varying solar illuminance across different times of day.
    """

    def __init__(self, brightness: float = 0.25, contrast: float = 0.25, saturation: float = 0.2, hue: float = 0.05):
        self.jitter = T.ColorJitter(brightness=brightness, contrast=contrast, saturation=saturation, hue=hue)

    def __call__(self, img):
        return self.jitter(img)
