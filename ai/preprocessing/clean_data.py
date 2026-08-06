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

NON_IMPUTED_NUMERIC_COLUMNS = {
    "user_id",
    "plant_id",
    "species_id",
    "location_id",
    "group_id",
    "latitude",
    "longitude",
}


# =====================================================
# Cleaning Functions
# =====================================================


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    # Find any column that has been parsed into a Python list
    # list_cols = [col for col in df.columns if df[col].apply(lambda x: isinstance(x, list)).any()]
    # Find any column that has been parsed into a Python list (skipping datetime columns)
    list_cols = [col for col in df.columns if not pd.api.types.is_datetime64_any_dtype(df[col]) and df[col].apply(lambda x: isinstance(x, list)).any()]

    if list_cols:
        # Convert list columns to strings temporarily to allow deduplication
        df_copy = df.copy()
        for col in list_cols:
            df_copy[col] = df_copy[col].astype(str)

        # Get the indices of the unique rows
        unique_indices = df_copy.drop_duplicates().index

        # Return the original data (keeping actual lists intact) at those unique indices
        return df.loc[unique_indices]

    # If no lists are found, run normally

    return df.drop_duplicates()


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing numeric measurements using the mean.

    Identifier and coordinate fields are join keys. Filling those values would
    attach unrelated rows to the same plant/location during merging.
    """
    df = df.copy()
    numeric_columns = [column for column in df.select_dtypes(include="number").columns if column not in NON_IMPUTED_NUMERIC_COLUMNS]

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
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", format="mixed")
        except TypeError:
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


def clean_weather_data(df):

    df = remove_duplicates(df)

    df = coerce_numeric_columns(df)

    df = convert_timestamp_to_date(df)

    df = fill_missing_values(df)

    df = sort_by_timestamp(df)

    df = reset_index(df)

    return df


def clean_plant_data(df):

    df = remove_duplicates(df)

    df = convert_timestamp_to_date(df)

    df = fill_missing_values(df)

    df = reset_index(df)

    return df


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
    """

    df = remove_duplicates(df)
    df = coerce_numeric_columns(df)
    df = convert_timestamp_to_date(df)

    print("\nBefore validation")
    print(df.shape)

    if "temperature" in df.columns:
        print(df["temperature"].describe())

    df = remove_invalid_sensor_values(df)

    print("\nAfter validation")
    print(df.shape)

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

        print(f"\n===== Cleaning {name} =====")
        print("Initial:", df.shape)

        if name == "sensor":
            cleaned[name] = clean_dataframe(df)

        elif name in ("weather", "weather_json"):
            cleaned[name] = clean_weather_data(df)

        elif name == "plants":
            cleaned[name] = clean_plant_data(df)

        else:
            cleaned[name] = df.copy()

        print("Final:", cleaned[name].shape)

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
