"""
Purpose
-------
Standardize data loaded from external APIs or third-party datasets.

Unlike internal sensor or database data, external data often uses
different column names. This script allows the user to map those
columns into the project's canonical schema.

The mapping is saved so the same API does not need to be configured
again.
"""

# ai/prepocessing/standardize_api.py

from pathlib import Path
import json

import pandas as pd

# -----------------------------------------------------
# Mapping folder
# -----------------------------------------------------

AI_FOLDER = Path(__file__).resolve().parent.parent

MAPPING_DIR = AI_FOLDER / "config" / "schema_mappings"
MAPPING_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------
# Canonical columns
# -----------------------------------------------------

CANONICAL_COLUMNS = {
    # Merge keys
    "timestamp": "Timestamp",
    "group_id": "Group ID",
    "location_id": "Location ID",
    # Geography
    "latitude": "Latitude",
    "longitude": "Longitude",
    "country": "Country",
    "city": "City",
    # Weather
    "temperature": "Temperature",
    "humidity": "Humidity",
    "rainfall": "Rainfall",
    "rain_probability": "Rain Probability",
    "wind_speed": "Wind Speed",
    # Soil
    "soil_moisture": "Soil Moisture",
    "soil_ph": "Soil pH",
}


# -----------------------------------------------------
# Helper
# -----------------------------------------------------


def choose_column(df: pd.DataFrame, display_name: str):
    """
    Ask the user which column represents a canonical field.
    """

    print(f"\nSelect the column for {display_name}")

    print("0. None")

    for i, column in enumerate(df.columns, start=1):
        print(f"{i}. {column}")

    while True:

        choice = input("Choice: ")

        if choice.isdigit():

            choice = int(choice)

            if choice == 0:
                return None

            if 1 <= choice <= len(df.columns):
                return df.columns[choice - 1]

        print("Invalid selection.")


# -----------------------------------------------------
# Interactive mapper
# -----------------------------------------------------


def create_mapping(df: pd.DataFrame):

    mapping = {}

    print("\nDetected columns:\n")

    for column in df.columns:
        print(f"- {column}")

    print("\nMap only the columns that exist.\n")

    for canonical_name, display_name in CANONICAL_COLUMNS.items():

        selected = choose_column(df, display_name)

        if selected is not None:
            mapping[selected] = canonical_name

    return mapping


# -----------------------------------------------------
# Save mapping
# -----------------------------------------------------


def save_mapping(mapping: dict, api_name: str):

    path = MAPPING_DIR / f"{api_name}.json"

    with open(path, "w") as file:
        json.dump(mapping, file, indent=4)


def load_mapping(api_name: str):

    path = MAPPING_DIR / f"{api_name}.json"

    if path.exists():

        with open(path) as file:
            return json.load(file)

    return None


# -----------------------------------------------------
# Standardization
# -----------------------------------------------------


def standardize_api_dataframe(df: pd.DataFrame, api_name: str):

    mapping = load_mapping(api_name)

    if mapping is None:

        mapping = create_mapping(df)

        save_mapping(mapping, api_name)

    df = df.rename(columns=mapping)

    return df
