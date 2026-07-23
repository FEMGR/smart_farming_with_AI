"""
Purpose
-------
Load data from various sources and convert it into pandas DataFrames.

This is the first step of the AI preprocessing pipeline.

                load_data.py
                     │
      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼
 load_csv()    load_database()   load_api()
      │              │              │
      └──────────────┼──────────────┘
                     ▼
               pandas DataFrame
                     ▼
             clean_data.py
                     ▼
             normalize.py
                     ▼
             merge_data.py
                     ▼
             train_model.py
"""

# ai/prepocessing/load.py

from pathlib import Path

import pandas as pd
import requests
from sqlalchemy import create_engine

# -----------------------------------------------------
# Locate the AI dataset folder
# -----------------------------------------------------

# load_data.py
#     │
# preprocessing/
#     │
# ai/
AI_FOLDER = Path(__file__).resolve().parent.parent

# ai/datasets/raw/
RAW_DATA_DIR = AI_FOLDER / "datasets" / "raw"


# =====================================================
# Helper Functions
# =====================================================


def build_path(filename: str) -> Path:
    """
    Build the full path to a file stored in ai/datasets/raw/.
    """

    return RAW_DATA_DIR / filename


# =====================================================
# File Loaders
# =====================================================


def load_csv(filename: str) -> pd.DataFrame:
    """
    Load a CSV file.
    """

    return pd.read_csv(build_path(filename))


def load_excel(filename: str) -> pd.DataFrame:
    """
    Load an Excel file.
    """

    return pd.read_excel(build_path(filename))


def load_json(filename: str) -> pd.DataFrame:
    """
    Load a JSON file.
    """

    return pd.read_json(build_path(filename))


def load_parquet(filename: str) -> pd.DataFrame:
    """
    Load a Parquet file.
    """

    return pd.read_parquet(build_path(filename))


# =====================================================
# Database Loader
# =====================================================


def load_database(connection_string: str, query: str) -> pd.DataFrame:
    """
    Execute an SQL query and return the result as a DataFrame.
    """

    engine = create_engine(connection_string)

    return pd.read_sql(query, engine)


# =====================================================
# API Loader
# =====================================================


def load_api(url: str) -> pd.DataFrame:
    """
    Download JSON data from a REST API.
    """

    response = requests.get(url)

    # Raise an exception if the request failed.
    response.raise_for_status()

    data = response.json()

    return pd.DataFrame(data)


# =====================================================
# Sensor Loader (Placeholder)
# =====================================================


def load_sensor():
    """
    Placeholder for future sensor integration.

    Future examples:
        - Serial (Arduino)
        - MQTT
        - Raspberry Pi GPIO
        - ESP32
    """

    raise NotImplementedError("Sensor loading has not been implemented yet.")


# =====================================================
# Project Loader
# =====================================================


def load_all_data() -> dict:
    """
    Load all datasets required by the AI pipeline.

    Returns
    -------
    dict
        Dictionary of pandas DataFrames.
    """

    return {
        "sensor": load_csv("sensor_readings.csv"),
        "weather": load_csv("weather.csv"),
        "plants": load_csv("plants.csv"),
    }


# =====================================================
# Preview Utility
# =====================================================


def preview_dataframe(df: pd.DataFrame, name: str) -> None:
    """
    Display a quick summary of a DataFrame.
    """

    print("\n" + "=" * 60)
    print(name.upper())
    print("=" * 60)

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())


# =====================================================
# Test
# =====================================================

if __name__ == "__main__":

    datasets = load_all_data()

    for name, dataframe in datasets.items():
        preview_dataframe(dataframe, name)

"""
sensor_df.isnull().sum()	How many missing values per column?	
sensor_df[sensor_df.isnull().any(axis=1)]	Which rows have missing values?	
sensor_df.isnull()	Which cells are missing?
sensor_df[sensor_df.isnull().any(axis=1)].index	Which row numbers are affected?	
iterrows() example	Which column is missing in each row?	
np.where()	Exact row/column coordinates of every missing value
"""
