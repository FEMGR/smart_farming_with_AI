"""
Purpose
-------
Run the complete preprocessing pipeline for every dataset.

Pipeline
--------
Load Data
    ↓
Schema Standardization
    ↓
Unit Standardization
    ↓
Data Cleaning
    ↓
Normalization
    ↓
Return processed DataFrames

This module acts as the main entry point for preprocessing.
Other scripts (merge_data.py, train_model.py, etc.) should
import this module instead of calling each preprocessing
step individually.
"""

# ai/prepocessing/preprocess_data.py

from load_data import load_all_data
from standardize_schema import standardize_schema
from standardize_units import standardize_units
from clean_data import clean_dataframe
from normalize import normalize_dataframe, normalize_sensor_data


def is_sensor_dataset(source_name):
    """
    Return True for raw files that contain sensor readings.
    """

    return source_name == "sensor" or source_name.startswith("sensor_readings")


# =====================================================
# Preprocess a single dataset
# =====================================================


def preprocess_dataframe(df, source_name):
    """
    Run the complete preprocessing pipeline on one DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw dataset.

    source_name : str
        Dataset name (sensor, weather, plants, etc.)

    Returns
    -------
    pandas.DataFrame
        Processed dataset.
    """

    print(f"\nPreprocessing: {source_name}")

    # Step 1
    df = standardize_schema(df, source_name)

    # Step 2
    df = standardize_units(df, source_name)

    # Step 3
    df = clean_dataframe(df)

    # Step 4
    df = normalize_dataframe(
        df,
        datetime_columns=["timestamp"],
        boolean_columns=["is_raining", "use_sensor"],
    )

    if is_sensor_dataset(source_name):
        df = normalize_sensor_data(df)

    return df


# =====================================================
# Preprocess every dataset
# =====================================================


def preprocess_all_data():
    """
    Load and preprocess every dataset.

    Returns
    -------
    dict
        Dictionary containing processed DataFrames.
    """

    datasets = load_all_data()

    processed = {}

    for source_name, df in datasets.items():
        processed[source_name] = preprocess_dataframe(df, source_name)

    return processed


# =====================================================
# Test
# =====================================================

if __name__ == "__main__":

    datasets = preprocess_all_data()

    for name, df in datasets.items():
        print("\n" + "=" * 60)
        print(name.upper())
        print("=" * 60)

        print(df.head())
