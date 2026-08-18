"""
Purpose
-------
Merge multiple cleaned DataFrames into one AI-ready dataset.

Pipeline

load_data.py
      ↓
clean_data.py
      ↓
normalize.py
      ↓
merge_data.py
      ↓
train_model.py
"""

import sys
from pathlib import Path

import pandas as pd

# clean_data.py
#      │
# preprocessing/
#      │
# ai/
from ai.core.constants import (
    CANONICAL_DUPLICATE_COLUMNS,
    MERGE_DATA_OUTPUT_FILE as OUTPUT_FILE,
    MERGE_DATA_OUTPUT_FOLDER as OUTPUT_FOLDER,
)

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def normalize_location_id(series: pd.Series) -> pd.Series:
    """
    Normalize location IDs for joins while preserving non-numeric IDs.
    """

    normalized = series.astype("string").str.strip()
    numeric_values = pd.to_numeric(normalized, errors="coerce")
    integer_like = numeric_values.notna() & (numeric_values % 1 == 0)

    normalized.loc[integer_like] = numeric_values.loc[integer_like].astype("Int64").astype("string")

    return normalized.replace("", pd.NA)


def parse_timestamp(series: pd.Series) -> pd.Series:
    try:
        return pd.to_datetime(series, errors="coerce", format="mixed")
    except TypeError:
        return pd.to_datetime(series, errors="coerce")


def fill_from_first_available(df: pd.DataFrame, target: str, candidates: list[str]) -> pd.DataFrame:
    available_columns = [column for column in candidates if column in df.columns]

    if not available_columns:
        return df

    if target in df.columns:
        available_columns = [target, *available_columns]

    df[target] = df[available_columns].bfill(axis=1).iloc[:, 0]

    columns_to_drop = [column for column in candidates if column in df.columns]
    return df.drop(columns=columns_to_drop)


def resolve_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse pandas merge suffix columns into canonical columns.
    """

    df = df.copy()

    for canonical_column, duplicate_columns in CANONICAL_DUPLICATE_COLUMNS.items():
        df = fill_from_first_available(df, canonical_column, duplicate_columns)

    return df


def plant_with_weather(plants_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    plants_df = plants_df.copy()
    weather_df = weather_df.copy()
    plants_df["latitude"] = pd.to_numeric(plants_df["latitude"], errors="coerce")
    plants_df["longitude"] = pd.to_numeric(plants_df["longitude"], errors="coerce")
    weather_df["latitude"] = pd.to_numeric(weather_df["latitude"], errors="coerce")
    weather_df["longitude"] = pd.to_numeric(weather_df["longitude"], errors="coerce")

    plants_df["lat_round"] = plants_df["latitude"].round(4)
    plants_df["lon_round"] = plants_df["longitude"].round(4)

    weather_df["lat_round"] = weather_df["latitude"].round(4)
    weather_df["lon_round"] = weather_df["longitude"].round(4)

    plants_df = plants_df.dropna(subset=["lat_round", "lon_round"])
    weather_df = weather_df.dropna(subset=["lat_round", "lon_round"])

    return pd.merge(
        plants_df,
        weather_df,
        on=["lat_round", "lon_round"],
        how="inner",
    )


def merge_with_sensor(data_df: pd.DataFrame, sensor_df: pd.DataFrame) -> pd.DataFrame:
    data_df = data_df.copy()
    sensor_df = sensor_df.copy()
    data_df["location_id"] = normalize_location_id(data_df["location_id"])
    sensor_df["location_id"] = normalize_location_id(sensor_df["location_id"])
    sensor_df["timestamp"] = parse_timestamp(sensor_df["timestamp"])
    data_df["timestamp"] = parse_timestamp(data_df["timestamp"])
    data_df = data_df.dropna(subset=["timestamp", "location_id"])
    sensor_df = sensor_df.dropna(subset=["timestamp", "location_id"])
    return pd.merge(data_df, sensor_df, on=["timestamp", "location_id"], how="inner")


def merge_all_data(plants_df: pd.DataFrame, weather_df: pd.DataFrame, sensor_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge every dataset required by the AI pipeline.
    """

    merged = plant_with_weather(plants_df, weather_df)

    merged = merge_with_sensor(merged, sensor_df)

    merged = resolve_duplicate_columns(merged)

    return merged


def save_merged_data(df: pd.DataFrame) -> None:
    """
    Save the merged dataset.
    """

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Merged dataset saved to:\n{OUTPUT_FILE}")


# =====================================================
# Utility
# =====================================================


def preview_dataset(df: pd.DataFrame) -> None:
    """
    Display a summary of the merged dataset.
    """

    print("\nMerged Dataset")
    print("-" * 50)

    print(df.head())

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nMissing Values:")
    print(df.isnull().sum())


# =====================================================
# Test
# =====================================================

if __name__ == "__main__":

    from ai.preprocessing.preprocess_data import preprocess_all_data

    datasets = preprocess_all_data()

    print("\nShapes before merge")
    print("Plants :", datasets["plants"].shape)
    print("Weather:", datasets["weather"].shape)
    print("Sensor :", datasets["sensor"].shape)

    merged_df = merge_all_data(datasets["plants"], datasets["weather"], datasets["sensor"])

    print("Saving cleaned dataset...")

    save_merged_data(merged_df)

    preview_dataset(merged_df)
