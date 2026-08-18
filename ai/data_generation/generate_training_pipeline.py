"""
Generate mock raw data and run the existing preprocessing pipeline.

generate_training_data.py is intentionally limited to raw CSV generation.
This script orchestrates the downstream preprocessing steps:

1. Generate plants.csv, weather.csv, and sensor_readings.csv
2. Load, standardize, clean, and normalize raw datasets
3. Merge datasets into merged_data.csv
4. Engineer the master feature repository featured_data.csv
5. Split featured_data.csv into task-specific training datasets
"""

from __future__ import annotations

import sys

import pandas as pd
from feature_engineering import engineer_features, save_featured_dataset
from feature_selection import split_training_sets
from merge_data import merge_all_data, save_merged_data
from preprocess_data import preprocess_all_data

from ai.core.constants import (
    DATA_GENERATION_DIR,
    PREPROCESSING_DIR,
)
from generate_training_data import generate_all

if str(DATA_GENERATION_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_GENERATION_DIR))

if str(PREPROCESSING_DIR) not in sys.path:
    sys.path.insert(0, str(PREPROCESSING_DIR))


def require_dataset(datasets: dict[str, pd.DataFrame], name: str) -> pd.DataFrame:
    if name not in datasets:
        raise KeyError(f"Required dataset '{name}' was not loaded. Available datasets: {sorted(datasets)}")

    return datasets[name]


def main() -> dict[str, pd.DataFrame]:
    print("=" * 70)
    print("GENERATE MOCK TRAINING PIPELINE")
    print("=" * 70)

    print("\nStep 1: Generating raw mock CSV files...")
    generate_all()

    print("\nStep 2: Loading, standardizing, cleaning, and normalizing raw data...")
    datasets = preprocess_all_data()

    plants_df = require_dataset(datasets, "plants")
    weather_df = require_dataset(datasets, "weather")
    sensor_df = require_dataset(datasets, "sensor")

    print("\nStep 3: Merging processed datasets...")
    merged_df = merge_all_data(plants_df, weather_df, sensor_df)
    save_merged_data(merged_df)

    print("\nStep 4: Engineering master feature repository...")
    featured_df = engineer_features(merged_df)
    save_featured_dataset(featured_df)

    print("\nStep 5: Splitting model-specific training datasets...")
    training_datasets = split_training_sets(featured_df)

    print("\nTraining pipeline completed.")

    return {
        "merged": merged_df,
        "featured": featured_df,
        **training_datasets,
    }


if __name__ == "__main__":
    main()
