"""Reusable machine-learning utilities for Smart Farming AI tasks."""

from ai.core.ml.data_loader import load_dataset, validate_dataset
from ai.core.ml.evaluation import evaluate_model
from ai.core.ml.model_io import load_model, load_preprocessing_artifacts, save_model, save_preprocessing_artifacts
from ai.core.ml.prediction import predict, predict_with_confidence
from ai.core.ml.preprocessing import PreprocessingArtifacts, PreprocessingConfig, fit_preprocessor, preprocess_dataset, transform_features
from ai.core.ml.splitting import SplitConfig, split_dataset
from ai.core.ml.training import train_model

__all__ = [
    "PreprocessingArtifacts",
    "PreprocessingConfig",
    "SplitConfig",
    "evaluate_model",
    "fit_preprocessor",
    "load_dataset",
    "load_model",
    "load_preprocessing_artifacts",
    "predict",
    "predict_with_confidence",
    "preprocess_dataset",
    "save_model",
    "save_preprocessing_artifacts",
    "split_dataset",
    "train_model",
    "transform_features",
    "validate_dataset",
]
