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


SUPPORTED_FILE_LOADERS = {
    ".csv": load_csv,
    ".xlsx": load_excel,
    ".xls": load_excel,
    ".json": load_json,
    ".parquet": load_parquet,
}

DATASET_NAME_ALIASES = {
    "sensor_readings": "sensor",
}


def get_dataset_name(path: Path, existing_names: set[str]) -> str:
    """
    Build a stable dataset name from a raw data file.
    """

    base_name = DATASET_NAME_ALIASES.get(path.stem, path.stem)

    if base_name not in existing_names:
        return base_name

    dataset_name = f"{base_name}_{path.suffix.lstrip('.')}"
    counter = 2

    while dataset_name in existing_names:
        dataset_name = f"{base_name}_{path.suffix.lstrip('.')}_{counter}"
        counter += 1

    return dataset_name


def load_data_file(path: Path) -> pd.DataFrame:
    """
    Load one supported data file from ai/datasets/raw/.
    """

    loader = SUPPORTED_FILE_LOADERS[path.suffix.lower()]

    return loader(path.name)


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
    Load all supported datasets from ai/datasets/raw/.

    Returns
    -------
    dict
        Dictionary of pandas DataFrames.
    """

    datasets = {}

    for path in sorted(RAW_DATA_DIR.iterdir()):

        if not path.is_file():
            continue

        if path.name == "weather.json":
            continue

        if path.suffix.lower() not in SUPPORTED_FILE_LOADERS:
            continue

        dataset_name = get_dataset_name(path, set(datasets))
        datasets[dataset_name] = load_data_file(path)

    return datasets


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
