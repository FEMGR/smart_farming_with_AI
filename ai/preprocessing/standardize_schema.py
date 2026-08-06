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

# ai/prepocessing/standardize_schema.py

from pathlib import Path
import json
from rapidfuzz import fuzz
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
    "timestamp": ["timestamp", "datetime", "date_time", "date", "time", "recorded_at", "created_at"],
    "sensor_id": ["id", "sensor", "sensor_id", "device_id"],
    "group_id": ["group", "group_id", "bed_id", "zone_id"],
    "location_id": ["location", "location_id", "field_id"],
    "latitude": ["latitude", "lat"],
    "longitude": ["longitude", "lon", "lng"],
    "country": ["country"],
    "city": ["city", "town"],
    "temperature": ["temperature", "temp", "temp_c", "temperature_c", "air_temperature"],
    "humidity": ["humidity", "humidity_pct", "relative_humidity", "rh"],
    "rainfall": ["rain", "rainfall", "precipitation"],
    "rain_probability": ["rain_probability", "pop", "precip_probability"],
    "wind_speed": ["wind", "wind_speed"],
    "soil_moisture": ["soil_moisture", "soil_moisture_pct", "soil_water", "soil_water_pct", "moisture"],
    "soil_ph": ["ph", "soil_ph"],
    "light": ["light", "light_lux", "sunlight", "lux", "illumination"],
}

AUTO_ACCEPT = 95
REVIEW = 80


def detect_columns(df):

    mapping = {}
    confidence = {}

    for canonical, synonyms in CANONICAL_COLUMNS.items():

        best_score = 0
        best_column = None

        for column in df.columns:

            column_lower = column.lower()

            for synonym in synonyms:

                score = fuzz.ratio(column_lower, synonym.lower())

                if score > best_score:
                    best_score = score
                    best_column = column

        if best_score >= REVIEW:

            mapping[best_column] = canonical
            confidence[canonical] = best_score

    return mapping, confidence


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


def create_mapping(df):

    mapping, confidence = detect_columns(df)

    while True:

        print_summary(mapping, confidence)

        choice = confirm_mapping()

        if choice == "y":

            return mapping

        elif choice == "e":

            mapping, confidence = edit_mapping(df, mapping, confidence)
        else:

            raise KeyboardInterrupt("Mapping cancelled.")


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


def confirm_mapping():

    while True:

        choice = input("\nAccept mapping? " "[Y]es / [E]dit / [C]ancel : ").lower()

        if choice in ("y", "e", "c"):

            return choice


def edit_mapping(df, mapping, confidence):
    try:
        canonical_list = list(CANONICAL_COLUMNS.keys())

        print("\nFields")
        for i, field in enumerate(canonical_list, start=1):
            print(f"{i}. {field}")

        selection = int(input("\nField to modify: "))
        canonical = canonical_list[selection - 1]  # e.g., 'timestamp'

        # FIX: Safely remove old references to this canonical value
        # without destroying other correct columns
        for key in list(mapping.keys()):
            if mapping[key] == canonical:
                del mapping[key]

        print("\nColumns")
        print("0. None")
        for i, column in enumerate(df.columns, start=1):
            print(f"{i}. {str(column)}")

        selected = int(input("Column: "))

        if selected == 0:
            if canonical in confidence:
                del confidence[canonical]
        else:
            chosen_column = df.columns[selected - 1]

            # Key is the original CSV column name, Value is the canonical name
            mapping[chosen_column] = canonical
            confidence[canonical] = 100.0

    except Exception as e:
        print(f"\n[Warning] An error occurred during editing: {e}")

    return mapping, confidence


# -----------------------------------------------------
# Standardization
# -----------------------------------------------------


def standardize_schema(df: pd.DataFrame, api_name: str):

    mapping = load_mapping(api_name)

    if mapping is None:

        mapping = create_mapping(df)

        save_mapping(mapping, api_name)

    df = df.rename(columns=mapping)
    df.attrs["schema_mapping"] = mapping
    df.attrs["original_columns_by_canonical"] = {canonical: original for original, canonical in mapping.items()}

    return df


# -----------------------------------------------------
# SUMMARY
# -----------------------------------------------------


def print_summary(mapping, confidence):

    print("\n" + "=" * 60)
    print("Schema Detection Summary")
    print("=" * 60)

    detected = set(mapping.values())

    for canonical in CANONICAL_COLUMNS:

        if canonical in detected:

            original = next(key for key, value in mapping.items() if value == canonical)

            score = confidence[canonical]

            status = "✓"

            if score < AUTO_ACCEPT:
                status = "?"

            print(f"{status} {canonical:20}" f"{original:25}" f"{score}%")

        else:

            print(f"✗ {canonical:20}Not detected")

    print("=" * 60)
