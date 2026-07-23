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


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert known measurement columns to numeric values.
    """

    df = df.copy()

    numeric_columns = [
        "temperature",
        "humidity",
        "soil_moisture",
        "soil_ph",
        "light",
        "rainfall",
        "rain_probability",
        "wind_speed",
    ]

    for column in numeric_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def remove_invalid_sensor_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove impossible sensor values.

    These ranges are examples and should be adjusted
    for your sensors.
    """

    if "temperature" in df.columns:
        df = df[df["temperature"].isna() | ((df["temperature"] >= -30) & (df["temperature"] <= 60))]

    if "humidity" in df.columns:
        df = df[df["humidity"].isna() | ((df["humidity"] >= 0) & (df["humidity"] <= 100))]

    if "soil_moisture" in df.columns:
        df = df[df["soil_moisture"].isna() | ((df["soil_moisture"] >= 0) & (df["soil_moisture"] <= 100))]

    if "soil_ph" in df.columns:
        df = df[df["soil_ph"].isna() | ((df["soil_ph"] >= 0) & (df["soil_ph"] <= 14))]

    if "light" in df.columns:
        df = df[df["light"].isna() | (df["light"] >= 0)]

    return df


def convert_timestamp_to_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert columns into the correct data types.
    """

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])

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


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute the complete data cleaning pipeline.

    The order of these operations is important:
        1. Remove duplicate rows
        2. Convert measurement values
        3. Convert timestamps
        4. Remove invalid values
        5. Fill missing values
        6. Sort by timestamp
        7. Reset index
    """

    df = remove_duplicates(df)
    df = coerce_numeric_columns(df)
    df = convert_timestamp_to_date(df)
    df = remove_invalid_sensor_values(df)
    df = fill_missing_values(df)
    df = sort_by_timestamp(df)
    df = reset_index(df)

    return df


def clean_all_datasets(datasets):
    """
    Clean every DataFrame stored in the dataset dictionary.
    """

    cleaned = {}

    for name, df in datasets.items():
        cleaned[name] = clean_dataframe(df)

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

    df = clean_dataframe(df)

    print("Saving cleaned dataset...")

    save_clean_data(df)

    print("Data cleaning completed successfully.")


# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":
    main()
