"""
Purpose
-------
Clean raw sensor data before it is used for machine learning.

Input
-----
ai/datasets/raw/sensor_readings.csv

Output
------
ai/datasets/processed/cleaned_sensor_readings.csv

After cleaning, the dataset should have:
    ✓ No duplicate rows
    ✓ Missing values handled
    ✓ Invalid sensor values removed
    ✓ Consistent data types
    ✓ Standardized column names
    ✓ Timestamp converted to datetime
    ✓ Saved to the processed dataset folder
"""

# ai/prepocessing/clean_data.py
from pathlib import Path

import pandas as pd

from load_data import load_csv


# =====================================================
# Project Paths
# =====================================================

# clean_data.py
#      │
# preprocessing/
#      │
# ai/
AI_FOLDER = Path(__file__).resolve().parent.parent

# ai/datasets/processed/
OUTPUT_FOLDER = AI_FOLDER / "datasets" / "processed"

OUTPUT_FILE = OUTPUT_FOLDER / "cleaned_sensor_readings.csv"


# =====================================================
# Cleaning Functions
# =====================================================


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicated rows.

    Duplicate rows may occur if a sensor sends the same
    reading more than once.
    """

    return df.drop_duplicates()


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing numeric values using the median.

    Median is usually preferred over the mean because
    it is less affected by extreme outliers.
    """
    df = df.copy()
    numeric_columns = df.select_dtypes(include="number").columns

    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())

    return df


def remove_invalid_sensor_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove impossible sensor values.

    These ranges are examples and should be adjusted
    for your sensors.
    """

    if "temperature_c" in df.columns:
        df = df[(df["temperature_c"] >= -30) & (df["temperature_c"] <= 60)]

    if "humidity_pct" in df.columns:
        df = df[(df["humidity_pct"] >= 0) & (df["humidity_pct"] <= 100)]

    if "soil_moisture_pct" in df.columns:
        df = df[(df["soil_moisture_pct"] >= 0) & (df["soil_moisture_pct"] <= 100)]

    return df


def convert_timestamp_to_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert columns into the correct data types.
    """

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names.

    Makes future preprocessing easier because every
    dataset follows the same naming convention.
    """

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    return df


def sort_by_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort the dataset by timestamp.
    """

    if "timestamp" in df.columns:
        df = df.sort_values("timestamp")

    return df


def reset_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reset row numbers after rows have been removed.
    """

    return df.reset_index(drop=True)


def save_clean_data(df: pd.DataFrame) -> None:
    """
    Save the cleaned dataset.
    """

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Cleaned dataset saved to:\n{OUTPUT_FILE}")


def clean_all_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute the complete data cleaning pipeline.

    The order of these operations is important:
        1. Rename columns
        2. Remove duplicate rows
        3. Fill missing values
        4. Remove invalid sensor values
        5. Convert data types
        6. Sort by timestamp
        7. Reset the index

    Returns
    -------
    pd.DataFrame
        The cleaned DataFrame.
    """
    df = remove_duplicates(df)
    df = fill_missing_values(df)
    df = remove_invalid_sensor_values(df)
    df = convert_timestamp_to_date(df)
    df = rename_columns(df)
    df = sort_by_timestamp(df)
    df = reset_index(df)

    return df


def clean_all_datasets(datasets):
    """
    Clean every DataFrame stored in the dataset dictionary.
    """

    cleaned = {}

    for name, df in datasets.items():
        cleaned[name] = clean_all_data(df)

    return cleaned


# =====================================================
# Main Pipeline
# =====================================================


def main():
    """
    Load, clean, and save the sensor dataset.
    """

    print("Loading dataset...")

    df = load_csv("sensor_readings.csv")

    print("Cleaning dataset...")

    df = clean_all_data(df)

    print("Saving cleaned dataset...")

    save_clean_data(df)

    print("Data cleaning completed successfully.")


# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":
    main()
