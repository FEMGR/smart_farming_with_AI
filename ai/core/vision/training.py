"""
Training engine specifically tailored for PyTorch Computer Vision models
with accuracy, loss, F1-score, and confusion matrix evaluation.
"""

# ai/core/vision/training.py

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Optional, Union

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from ai.core.ml.pytorch.checkpoint import load_checkpoint, save_checkpoint
from ai.core.ml.pytorch.device import ensure_torch_available, resolve_device


def compute_metrics_and_confusion_matrix(
    all_preds: torch.Tensor,
    all_targets: torch.Tensor,
    num_classes: int,
) -> tuple[float, list[list[int]]]:
    """
    Computes Macro F1-score and Confusion Matrix without requiring external libraries.
    """
    cm = torch.zeros((num_classes, num_classes), dtype=torch.int64)
    for t, p in zip(all_targets.view(-1), all_preds.view(-1)):
        cm[t.long(), p.long()] += 1

    f1_scores = []
    for c in range(num_classes):
        tp = float(cm[c, c])
        fp = float(cm[:, c].sum() - tp)
        fn = float(cm[c, :].sum() - tp)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0
        f1_scores.append(f1)

    macro_f1 = sum(f1_scores) / len(f1_scores) if len(f1_scores) > 0 else 0.0
    return round(macro_f1, 4), cm.tolist()


@dataclass(frozen=True)
class VisionTrainingConfig:
    epochs: int = 30
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    random_state: int = 42
    device: Optional[str] = None
    checkpoint_dir: Optional[Union[str, Path]] = "checkpoints"
    restore_best_by: str = "loss"  # Options: "loss", "acc", or "f1"


@dataclass
class VisionTrainingResult:
    model: nn.Module
    training_rows: int
    started_at: str
    finished_at: str
    duration_seconds: float
    best_checkpoint_val_loss: float
    best_checkpoint_val_acc: float
    best_checkpoint_val_f1: float
    best_loss_epoch: int = 0
    max_val_acc: float = 0.0
    best_acc_epoch: int = 0
    best_loss_model_path: Optional[Path] = None
    best_acc_model_path: Optional[Path] = None
    restored_from: Optional[Path] = None
    final_confusion_matrix: List[List[int]] = field(default_factory=list)
    history: Dict[str, List[float]] = field(default_factory=dict)


def train_vision_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: Optional[DataLoader] = None,
    config: Optional[VisionTrainingConfig] = None,
    num_classes: Optional[int] = None,
) -> VisionTrainingResult:
    """
    Train a vision model with validation, F1-score, Confusion Matrix generation,
    dual-checkpointing, best-weight restoration, and pause/resume capabilities.
    """
    ensure_torch_available()
    cfg = config or VisionTrainingConfig()
    torch.manual_seed(cfg.random_state)

    device = resolve_device(cfg.device)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.epochs)

    # Infer num_classes if not explicitly passed
    if num_classes is None:
        if hasattr(model, "fc") and hasattr(model.fc, "out_features"):
            num_classes = model.fc.out_features
        elif hasattr(model, "heads") and hasattr(model.heads, "head"):
            num_classes = model.heads.head.out_features
        elif hasattr(model, "classifier"):
            num_classes = model.classifier.out_features if hasattr(model.classifier, "out_features") else model.classifier[-1].out_features
        else:
            num_classes = 10  # Fallback default if unresolvable

    started_at = datetime.now().isoformat()
    start_time = perf_counter()

    history: Dict[str, List[float]] = {
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "val_f1": [],
    }

    checkpoint_dir = Path(cfg.checkpoint_dir) if cfg.checkpoint_dir else None
    last_confusion_matrix: List[List[int]] = []

    start_epoch = 1
    resume_checkpoint_path = checkpoint_dir / "training_checkpoint.pth" if checkpoint_dir else None

    # Initialize fallback tracking states
    history = {
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "val_f1": [],
    }
    best_checkpoint_val_loss = float("inf")
    best_checkpoint_val_acc = 0.0
    best_checkpoint_val_f1 = 0.0
    best_loss_epoch = 0
    max_val_acc = 0.0
    best_acc_epoch = 0

    # ------------------- 0. RESUME CHECKPOINT LOADING -------------------
    if resume_checkpoint_path and resume_checkpoint_path.exists():
        # Load raw metadata/checkpoint dictionary without applying state_dict yet
        checkpoint_data = torch.load(resume_checkpoint_path, map_location=device)

        # Check if final linear layer shape matches current num_classes
        saved_out_features = checkpoint_data["model_state_dict"]["fc.1.weight"].shape[0]

        if saved_out_features != num_classes:
            print(
                f"[WARNING] Class count mismatch! Checkpoint expects {saved_out_features} classes, "
                f"but current dataset has {num_classes} classes. Starting fresh training..."
            )
            # Skip resuming or remove obsolete checkpoint
            loaded_data = None
        else:
            # Use central checkpoint loader
            loaded_data = load_checkpoint(
                model=model,
                path=resume_checkpoint_path,
                optimizer=optimizer,
                scheduler=scheduler if scheduler else None,
                device=device,
            )

        # Restore epoch and custom evaluation metrics from saved metadata
        start_epoch = 1  # Default starting epoch for fresh training

        if loaded_data:
            start_epoch = loaded_data.get("epoch", 0) + 1
            metrics = loaded_data.get("metrics", {})

            history = metrics.get("history", history)
            best_checkpoint_val_loss = metrics.get("best_checkpoint_val_loss", float("inf"))
            best_checkpoint_val_acc = metrics.get("best_checkpoint_val_acc", 0.0)
            best_checkpoint_val_f1 = metrics.get("best_checkpoint_val_f1", 0.0)
            best_loss_epoch = metrics.get("best_loss_epoch", 0)
            max_val_acc = metrics.get("max_val_acc", 0.0)
            best_acc_epoch = metrics.get("best_acc_epoch", 0)
            last_confusion_matrix = metrics.get("last_confusion_matrix", [])

            print(f"[RESUMED] Successfully restored states! Resuming training from Epoch {start_epoch}/{cfg.epochs}...\n")
        else:
            print(f"[TRAINING] Starting fresh training from Epoch 1/{cfg.epochs}...")

    try:
        for epoch in range(start_epoch, cfg.epochs + 1):
            # ------------------- 1. TRAINING PHASE -------------------
            model.train()
            train_loss, train_correct, train_samples = 0.0, 0, 0

            train_pbar = tqdm(
                train_loader,
                desc=f"Epoch {epoch}/{cfg.epochs} [Train]",
                unit="batch",
                leave=True,
            )

            for X_batch, y_batch in train_pbar:
                batch_size = X_batch.size(0)
                if batch_size == 0:
                    continue

                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device).long()
                if y_batch.dim() > 1:
                    y_batch = y_batch.squeeze(-1)

                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()

                batch_loss = float(loss.item())
                train_loss += batch_loss * batch_size
                preds = torch.argmax(outputs, dim=1)
                train_correct += int((preds == y_batch).sum().item())
                train_samples += batch_size

                train_pbar.set_postfix(
                    {
                        "loss": f"{batch_loss:.4f}",
                        "acc": f"{(train_correct / train_samples):.4f}" if train_samples > 0 else "0.0000",
                    }
                )

            epoch_train_loss = train_loss / train_samples if train_samples > 0 else 0.0
            epoch_train_acc = train_correct / train_samples if train_samples > 0 else 0.0
            history["train_loss"].append(epoch_train_loss)
            history["train_acc"].append(epoch_train_acc)

            # Step scheduler after training epoch
            if scheduler:
                scheduler.step()

            # ------------------- 2. VALIDATION PHASE -------------------
            epoch_val_loss, epoch_val_acc, epoch_val_f1 = 0.0, 0.0, 0.0

            if val_loader is not None:
                model.eval()
                val_loss, val_correct, val_samples = 0.0, 0, 0
                all_preds: List[int] = []
                all_targets: List[int] = []

                val_pbar = tqdm(
                    val_loader,
                    desc=f"Epoch {epoch}/{cfg.epochs} [Val]  ",
                    unit="batch",
                    leave=False,
                )

                with torch.no_grad():
                    for X_batch, y_batch in val_pbar:
                        batch_size = X_batch.size(0)
                        if batch_size == 0:
                            continue

                        X_batch = X_batch.to(device)
                        y_batch = y_batch.to(device).long()
                        if y_batch.dim() > 1:
                            y_batch = y_batch.squeeze(-1)

                        outputs = model(X_batch)
                        loss = criterion(outputs, y_batch)

                        batch_loss = float(loss.item())
                        val_loss += batch_loss * batch_size
                        preds = torch.argmax(outputs, dim=1)
                        val_correct += int((preds == y_batch).sum().item())
                        val_samples += batch_size

                        all_preds.extend(preds.cpu().tolist())
                        all_targets.extend(y_batch.cpu().tolist())

                        val_pbar.set_postfix(
                            {
                                "loss": f"{batch_loss:.4f}",
                                "acc": f"{(val_correct / val_samples):.4f}" if val_samples > 0 else "0.0000",
                            }
                        )

                epoch_val_loss = val_loss / val_samples if val_samples > 0 else 0.0
                epoch_val_acc = val_correct / val_samples if val_samples > 0 else 0.0

                # Calculate confusion matrix & macro F1
                if all_targets:
                    confusion = [[0] * num_classes for _ in range(num_classes)]
                    for t, p in zip(all_targets, all_preds):
                        if 0 <= t < num_classes and 0 <= p < num_classes:
                            confusion[t][p] += 1
                    last_confusion_matrix = confusion

                    # Calculate macro F1-score
                    f1_scores = []
                    for c in range(num_classes):
                        tp = confusion[c][c]
                        fp = sum(confusion[r][c] for r in range(num_classes) if r != c)
                        fn = sum(confusion[c][col] for col in range(num_classes) if col != c)
                        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
                        f1_scores.append(f1)
                    epoch_val_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

            history["val_loss"].append(epoch_val_loss)
            history["val_acc"].append(epoch_val_acc)
            history["val_f1"].append(epoch_val_f1)

            # ------------------- CHECKPOINTING BEST WEIGHTS & RESUME STATE -------------------
            if checkpoint_dir:
                # 1. Update tracking metrics first so state stays consistent
                if epoch_val_loss < best_checkpoint_val_loss:
                    best_checkpoint_val_loss = epoch_val_loss
                    best_checkpoint_val_acc = epoch_val_acc
                    best_checkpoint_val_f1 = epoch_val_f1
                    best_loss_epoch = epoch

                if epoch_val_acc > max_val_acc:
                    max_val_acc = epoch_val_acc
                    best_acc_epoch = epoch

                # 2. Package up-to-date state metadata
                checkpoint_metrics = {
                    "history": history,
                    "best_checkpoint_val_loss": best_checkpoint_val_loss,
                    "best_checkpoint_val_acc": best_checkpoint_val_acc,
                    "best_checkpoint_val_f1": best_checkpoint_val_f1,
                    "best_loss_epoch": best_loss_epoch,
                    "max_val_acc": max_val_acc,
                    "best_acc_epoch": best_acc_epoch,
                    "last_confusion_matrix": last_confusion_matrix,
                }

                # 3. Save best weights if updated during this epoch
                if best_loss_epoch == epoch:
                    save_checkpoint(
                        model=model,
                        optimizer=optimizer,
                        epoch=epoch,
                        path=checkpoint_dir / "best_loss_model.pth",
                        metrics=checkpoint_metrics,
                        scheduler=scheduler,
                    )

                if best_acc_epoch == epoch:
                    save_checkpoint(
                        model=model,
                        optimizer=optimizer,
                        epoch=epoch,
                        path=checkpoint_dir / "best_acc_model.pth",
                        metrics=checkpoint_metrics,
                        scheduler=scheduler,
                    )

                # 4. FULL EPOCH COMPLETED: Save state for seamless resume
                if resume_checkpoint_path:
                    save_checkpoint(
                        model=model,
                        optimizer=optimizer,
                        epoch=epoch,  # Full epoch finished -> saved as N (resumes at N + 1)
                        path=resume_checkpoint_path,
                        metrics=checkpoint_metrics,
                        scheduler=scheduler,
                    )

            print(
                f"Epoch {epoch:02d}/{cfg.epochs:02d} Summary | "
                f"Train Loss: {epoch_train_loss:.4f} - Train Acc: {epoch_train_acc:.4f} | "
                f"Val Loss: {epoch_val_loss:.4f} - Val Acc: {epoch_val_acc:.4f} - Val F1: {epoch_val_f1:.4f}",
                flush=True,
            )

    except KeyboardInterrupt:
        current_epoch = locals().get("epoch", 1)
        print(f"\n[PAUSED] Training session interrupted at Epoch {current_epoch}.")
        if resume_checkpoint_path:
            checkpoint_metrics = {
                "history": history,
                "best_checkpoint_val_loss": best_checkpoint_val_loss,
                "best_checkpoint_val_acc": best_checkpoint_val_acc,
                "best_checkpoint_val_f1": best_checkpoint_val_f1,
                "best_loss_epoch": best_loss_epoch,
                "max_val_acc": max_val_acc,
                "best_acc_epoch": best_acc_epoch,
                "last_confusion_matrix": last_confusion_matrix,
            }
            completed_epoch = max(0, current_epoch - 1)

            save_checkpoint(
                model=model,
                optimizer=optimizer,
                epoch=completed_epoch,
                path=resume_checkpoint_path,
                metrics=checkpoint_metrics,
                scheduler=scheduler,
            )

            print(f"[PAUSED] Progress saved to {resume_checkpoint_path}. Re-run anytime to resume.")

        raise

    # ------------------- RELOAD BEST CHECKPOINT -------------------
    restored_from = None

    best_loss_model_path = checkpoint_dir / "best_loss_model.pth" if checkpoint_dir else None
    best_acc_model_path = checkpoint_dir / "best_acc_model.pth" if checkpoint_dir else None

    restore_criterion = getattr(cfg, "restore_best_by", "loss")
    target_checkpoint = best_acc_model_path if restore_criterion == "acc" else best_loss_model_path

    if target_checkpoint and target_checkpoint.exists():
        print(f"\n[EVALUATION] Restoring best weights from: {target_checkpoint}")
        load_checkpoint(
            model=model,
            path=target_checkpoint,
            device=device,
        )
        restored_from = target_checkpoint
    else:
        print("\n[EVALUATION] No checkpoint restored. Proceeding with current model weights.")

    duration = perf_counter() - start_time
    finished_at = datetime.now().isoformat()

    # Note: Moves model to CPU to free VRAM
    model.to("cpu")
    model.eval()

    total_training_rows = len(train_loader.dataset) if hasattr(train_loader, "dataset") and train_loader.dataset is not None else 0

    return VisionTrainingResult(
        model=model,
        training_rows=total_training_rows,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration,
        best_checkpoint_val_loss=best_checkpoint_val_loss,
        best_checkpoint_val_acc=best_checkpoint_val_acc,
        best_checkpoint_val_f1=best_checkpoint_val_f1,
        best_loss_epoch=best_loss_epoch,
        max_val_acc=max_val_acc,
        best_acc_epoch=best_acc_epoch,
        best_loss_model_path=best_loss_model_path,
        best_acc_model_path=best_acc_model_path,
        restored_from=restored_from,
        final_confusion_matrix=last_confusion_matrix,
        history=history,
    )
