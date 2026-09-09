"""
handles un-normalizing the ImageNet pixel distributions applied during
PyTorch preprocessing so images render in true-to-life color,
alongside their mapped class labels.
"""

# ai/core/vision/visualization.py

from typing import Dict, List, Optional, Union
import matplotlib.pyplot as plt
import numpy as np
import torch


def denormalize(tensor: torch.Tensor, mean: List[float] = [0.485, 0.456, 0.406], std: List[float] = [0.229, 0.224, 0.225]) -> np.ndarray:
    """
    Reverses ImageNet normalization applied during preprocessing.
    Converts a Tensor (C, H, W) to a NumPy array (H, W, C) scaled to [0, 1].
    """
    image = tensor.clone().cpu().numpy()

    # Reshape mean and std for vector broadcasting: (3, 1, 1)
    mean_arr = np.array(mean)[:, None, None]
    std_arr = np.array(std)[:, None, None]

    # Reverse normalization: img = (tensor * std) + mean
    image = (image * std_arr) + mean_arr

    # Clip values to valid [0, 1] range and convert to (H, W, C)
    image = np.clip(image, 0, 1)
    return np.transpose(image, (1, 2, 0))


def plot_batch(
    images: torch.Tensor,
    labels: torch.Tensor,
    class_map: Optional[Union[Dict[int, str], Dict[str, int]]] = None,
    max_images: int = 16,
    ncols: int = 4,
    title: str = "Agricultural Dataset Batch",
    figsize: Optional[tuple] = None,
) -> None:
    """
    Plots a grid of images from a PyTorch DataLoader batch with class names.

    Args:
        images (torch.Tensor): Batch of image tensors (B, C, H, W).
        labels (torch.Tensor): Batch of target class indices (B,).
        class_map (dict, optional): Mapping dict between class indices and names.
        max_images (int): Maximum number of images to display. Default: 16.
        ncols (int): Number of grid columns. Default: 4.
        title (str): Figure title.
        figsize (tuple, optional): Explicit figure dimensions (width, height).
    """
    # Inverse map if user passed {class_name: index} instead of {index: class_name}
    idx_to_class = {}
    if class_map:
        first_key = next(iter(class_map.keys()))
        if isinstance(first_key, str):
            idx_to_class = {v: k for k, v in class_map.items()}
        else:
            idx_to_class = class_map

    num_images = min(len(images), max_images)
    nrows = int(np.ceil(num_images / ncols))

    if figsize is None:
        figsize = (ncols * 3.5, nrows * 3.5)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    fig.suptitle(title, fontsize=16, fontweight="bold", y=0.98)

    # Standardize axes to a 1D array for simpler iteration
    if num_images == 1:
        axes_list = [axes]
    else:
        axes_list = axes.flatten() if hasattr(axes, "flatten") else axes

    for idx in range(len(axes_list)):
        ax = axes_list[idx]
        if idx < num_images:
            img_np = denormalize(images[idx])
            label_idx = int(labels[idx].item())

            # Retrieve string class name if available
            class_name = idx_to_class.get(label_idx, f"Class {label_idx}")

            ax.imshow(img_np)
            ax.set_title(class_name, fontsize=10, fontweight="medium")
            ax.axis("off")
        else:
            # Turn off unused subplot axes
            ax.axis("off")

    plt.tight_layout()
    plt.show()


def plot_predictions(
    images: torch.Tensor,
    preds: torch.Tensor,
    targets: torch.Tensor,
    class_map: Optional[Union[Dict[int, str], Dict[str, int]]] = None,
    max_images: int = 16,
    ncols: int = 4,
) -> None:
    """
    Plots predictions versus true targets. Correct predictions are highlighted in green,
    incorrect predictions in red.
    """
    idx_to_class = {}
    if class_map:
        first_key = next(iter(class_map.keys()))
        if isinstance(first_key, str):
            idx_to_class = {v: k for k, v in class_map.items()}
        else:
            idx_to_class = class_map

    num_images = min(len(images), max_images)
    nrows = int(np.ceil(num_images / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.5, nrows * 3.8))
    fig.suptitle("Model Predictions vs Ground Truth", fontsize=16, fontweight="bold", y=0.98)

    axes_list = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for idx in range(len(axes_list)):
        ax = axes_list[idx]
        if idx < num_images:
            img_np = denormalize(images[idx])
            pred_idx = int(preds[idx].item())
            target_idx = int(targets[idx].item())

            pred_name = idx_to_class.get(pred_idx, f"Class {pred_idx}")
            target_name = idx_to_class.get(target_idx, f"Class {target_idx}")

            is_correct = pred_idx == target_idx
            title_color = "green" if is_correct else "red"

            ax.imshow(img_np)

            if is_correct:
                ax.set_title(f"Pred: {pred_name}", color=title_color, fontsize=10, fontweight="bold")
            else:
                ax.set_title(f"Pred: {pred_name}\nTrue: {target_name}", color=title_color, fontsize=10, fontweight="bold")

            ax.axis("off")
        else:
            ax.axis("off")

    plt.tight_layout()
    plt.show()
