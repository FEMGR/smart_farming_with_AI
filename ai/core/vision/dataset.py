"""
Generic PyTorch dataset for image classification tasks.

This dataset can be reused for:
- Plant identification
- Plant disease detection
- Pest detection
"""

# ai/core/vision/dataset.py

import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from PIL import Image
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import DataLoader, Dataset, Subset

from ai.core.vision.transforms import get_image_transforms

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tiff",
)


class VisionDataset(Dataset):
    """Generic dataset for image classification."""

    def __init__(
        self,
        root_dir: str,
        transform: Optional[Callable] = None,
    ):
        self.root_dir = root_dir
        self.transform = transform

        self.samples: List[Tuple[str, int]] = []
        self.classes: List[str] = []
        self.class_to_idx: Dict[str, int] = {}

        self._load_dataset()

    def _load_dataset(self) -> None:
        """Parses the directory tree to build file index and class mappings."""
        if not os.path.exists(self.root_dir):
            raise FileNotFoundError(f"Directory not found: {self.root_dir}")

        # Extract class names sorted alphabetically (ignoring hidden/system folders)
        self.classes = sorted([d for d in os.listdir(self.root_dir) if os.path.isdir(os.path.join(self.root_dir, d)) and not d.startswith(".")])

        if not self.classes:
            raise ValueError(f"No class directories found inside: {self.root_dir}")

        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}

        for target_class in self.classes:
            class_dir = os.path.join(self.root_dir, target_class)
            class_idx = self.class_to_idx[target_class]

            for root, _, fnames in sorted(os.walk(class_dir, followlinks=True)):
                for fname in sorted(fnames):
                    if fname.lower().endswith(IMAGE_EXTENSIONS):
                        path = os.path.join(root, fname)
                        self.samples.append((path, class_idx))

    @property
    def targets(self) -> List[int]:
        """Expose all sample targets to facilitate stratified splitting."""
        return [sample[1] for sample in self.samples]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int]:
        path, target = self.samples[index]

        with open(path, "rb") as f:
            img = Image.open(f).convert("RGB")

        if self.transform is not None:
            img = self.transform(img)

        return img, target


def create_dataloaders(
    data_dir: str,
    batch_size: int = 32,
    img_size: int = 224,
    num_workers: int = 0,  # Changed default to 0 for safe signal handling
    train_split: float = 0.8,
    seed: int = 42,
) -> Tuple[DataLoader, DataLoader, Dict[str, int]]:
    """
    Creates train and val DataLoaders with support for pre-split or dynamic dataset layouts.

    Defaulting num_workers to 0 (or lower) prevents background C++ PyTorch worker processes
    from blocking KeyboardInterrupt (Ctrl + C) signal handling during interactive training.
    """
    base_path = Path(data_dir)
    pin_memory = torch.cuda.is_available()

    # Check for pre-existing train/valid split structure
    train_subpath = base_path / "train"
    val_subpath = next((base_path / name for name in ("valid", "val", "validation") if (base_path / name).exists()), None)

    if train_subpath.exists() and val_subpath is not None:
        # --- Pre-split Dataset Mode ---
        train_dataset = VisionDataset(
            root_dir=str(train_subpath),
            transform=get_image_transforms(img_size=img_size, is_train=True),
        )
        val_dataset = VisionDataset(
            root_dir=str(val_subpath),
            transform=get_image_transforms(img_size=img_size, is_train=False),
        )

        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=pin_memory,
            persistent_workers=False if num_workers == 0 else True,
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            persistent_workers=False if num_workers == 0 else True,
        )

        return train_loader, val_loader, train_dataset.class_to_idx

    # --- Stratified Dynamic Split Mode ---
    base_dataset = VisionDataset(root_dir=data_dir)
    total_len = len(base_dataset)

    if total_len < 2:
        raise ValueError("Dataset must contain at least 2 images.")

    all_indices = list(range(total_len))
    targets = base_dataset.targets

    train_indices, val_indices = train_test_split(
        all_indices,
        test_size=1.0 - train_split,
        stratify=targets,
        random_state=seed,
        shuffle=True,
    )

    train_dataset = VisionDataset(
        root_dir=data_dir,
        transform=get_image_transforms(img_size=img_size, is_train=True),
    )
    val_dataset = VisionDataset(
        root_dir=data_dir,
        transform=get_image_transforms(img_size=img_size, is_train=False),
    )

    train_subset = Subset(train_dataset, train_indices)
    val_subset = Subset(val_dataset, val_indices)

    train_loader = DataLoader(
        train_subset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=False if num_workers == 0 else True,
    )
    val_loader = DataLoader(
        val_subset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=False if num_workers == 0 else True,
    )

    return train_loader, val_loader, base_dataset.class_to_idx
