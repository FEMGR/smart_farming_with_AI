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

# ai/prepocessing/merge_data.py

import pandas as pd


# =====================================================
# Merge Functions
# =====================================================


def merge_sensor_weather(sensor_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge sensor readings with weather data
    using timestamp and location.
    """
    print("\nSensor columns:")
    print(sensor_df.columns)

    print("\nWeather columns:")
    print(weather_df.columns)

    return pd.merge(sensor_df, weather_df, on=["timestamp", "location_id"], how="left")


def merge_with_plants(data_df: pd.DataFrame, plants_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add plant information to the merged dataset.
    """

    return pd.merge(data_df, plants_df, on="plant_id", how="left")


def merge_all_data(sensor_df: pd.DataFrame, weather_df: pd.DataFrame, plants_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge every dataset required by the AI pipeline.
    """

    merged = merge_sensor_weather(sensor_df, weather_df)

    merged = merge_with_plants(merged, plants_df)

    return merged


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

    from load_data import load_all_data
    from clean_data import clean_all_datasets
    from normalize import normalize_all_data

    datasets = load_all_data()

    datasets = clean_all_datasets(datasets)

    datasets = normalize_all_data(datasets)

    merged_df = merge_all_data(datasets["sensor"], datasets["weather"], datasets["plants"])

    preview_dataset(merged_df)
