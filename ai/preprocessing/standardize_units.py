"""

Purpose
-------
Convert all measurement units into the project's canonical units.

Canonical Units
---------------
Temperature      -> Celsius (°C)
Rainfall         -> millimeters (mm)
Wind Speed       -> meters/second (m/s)
Pressure         -> hectoPascal (hPa)
Distance         -> meters (m)
Soil Moisture    -> Percent (%)

This script should run AFTER schema standardization
and BEFORE clean_data.py.
"""

# ai/prepocessing/standardize_units.py

from pathlib import Path
import json
import re

import pandas as pd


# =====================================================
# Configuration
# =====================================================

AI_FOLDER = Path(__file__).resolve().parent.parent

CONFIG_FOLDER = AI_FOLDER / "config"

UNIT_FOLDER = CONFIG_FOLDER / "unit_mappings"

UNIT_FOLDER.mkdir(parents=True, exist_ok=True)


# =====================================================
# Unit conversion functions
# =====================================================


def fahrenheit_to_celsius(series):
    return (series - 32) * 5 / 9


def kelvin_to_celsius(series):
    return series - 273.15


def inch_to_mm(series):
    return series * 25.4


def cm_to_mm(series):
    return series * 10


def mph_to_ms(series):
    return series * 0.44704


def kmh_to_ms(series):
    return series / 3.6


def pa_to_hpa(series):
    return series / 100


def atm_to_hpa(series):
    return series * 1013.25


def feet_to_meter(series):
    return series * 0.3048


# =====================================================
# Conversion table
# =====================================================

CONVERSIONS = {
    "temperature": {
        "C": lambda x: x,
        "F": fahrenheit_to_celsius,
        "K": kelvin_to_celsius,
    },
    "rainfall": {
        "mm": lambda x: x,
        "cm": cm_to_mm,
        "inch": inch_to_mm,
    },
    "wind_speed": {
        "m/s": lambda x: x,
        "km/h": kmh_to_ms,
        "mph": mph_to_ms,
    },
    "pressure": {
        "hPa": lambda x: x,
        "Pa": pa_to_hpa,
        "atm": atm_to_hpa,
    },
    "distance": {
        "m": lambda x: x,
        "ft": feet_to_meter,
    },
    "soil_moisture": {
        "%": lambda x: x,
    },
}


def normalize_column_name(column_name):
    return re.sub(r"[^a-z0-9]+", "_", column_name.lower()).strip("_")


def infer_unit_from_column_name(column_name, source_column_name=None):
    """
    Infer obvious units from source column names like temp_c or rainfall_mm.
    """

    names = [column_name]

    if source_column_name:
        names.append(source_column_name)

    normalized_names = [normalize_column_name(name) for name in names]

    if column_name == "temperature":

        for name in normalized_names:

            if name.endswith("_c") or "celsius" in name:
                return "C"

            if name.endswith("_f") or "fahrenheit" in name:
                return "F"

            if name.endswith("_k") or "kelvin" in name:
                return "K"

    if column_name == "rainfall":

        for name in normalized_names:

            if name.endswith("_mm"):
                return "mm"

            if name.endswith("_cm"):
                return "cm"

            if "inch" in name:
                return "inch"

    if column_name == "wind_speed":

        for name in normalized_names:

            if name.endswith("_ms") or name.endswith("_m_s"):
                return "m/s"

            if name.endswith("_kmh") or name.endswith("_km_h"):
                return "km/h"

            if name.endswith("_mph"):
                return "mph"

    if column_name == "soil_moisture":

        for name in normalized_names:

            if name.endswith("_pct") or "percent" in name:
                return "%"

    return None


def infer_unit(df, column_name):
    source_columns = df.attrs.get("original_columns_by_canonical", {})

    return infer_unit_from_column_name(
        column_name,
        source_columns.get(column_name),
    )


def reconcile_unit_mapping(df, units):
    """
    Add or correct unit mappings when the source column name contains a unit.
    """

    units = dict(units)
    changed = False

    for column in df.columns:

        if column not in CONVERSIONS:
            continue

        inferred_unit = infer_unit(df, column)

        if inferred_unit is None:
            continue

        if units.get(column) != inferred_unit:
            units[column] = inferred_unit
            changed = True

    return units, changed


# =====================================================
# Save / load mapping
# =====================================================


def save_unit_mapping(units, source_name):

    path = UNIT_FOLDER / f"{source_name}.json"

    with open(path, "w") as file:
        json.dump(units, file, indent=4)


def load_unit_mapping(source_name):

    path = UNIT_FOLDER / f"{source_name}.json"

    if path.exists():

        with open(path) as file:
            return json.load(file)

    return None


# =====================================================
# Ask user
# =====================================================


def ask_unit(column_name):

    if column_name not in CONVERSIONS:
        return None

    print(f"\nColumn : {column_name}")

    options = list(CONVERSIONS[column_name].keys())

    for i, unit in enumerate(options, start=1):

        print(f"{i}. {unit}")

    while True:

        choice = input("Current unit : ").strip()

        if choice.isdigit():

            selected_index = int(choice)

            if 1 <= selected_index <= len(options):

                return options[selected_index - 1]

        for unit in options:

            if choice.lower() == unit.lower():

                return unit

        print("Invalid choice.")


# =====================================================
# Interactive mapping
# =====================================================


def create_unit_mapping(df):

    units = {}

    print("\nSpecify the units of each measurement.\n")

    for column in df.columns:

        if column in CONVERSIONS:

            inferred_unit = infer_unit(df, column)

            if inferred_unit is not None:
                print(f"\nColumn : {column}")
                print(f"Detected unit : {inferred_unit}")
                units[column] = inferred_unit
                continue

            units[column] = ask_unit(column)

    return units


# =====================================================
# Convert dataframe
# =====================================================


def convert_units(df, units):

    for column, unit in units.items():

        if column not in df.columns:
            continue

        conversion = CONVERSIONS[column].get(unit)

        if conversion is None:
            continue

        values = pd.to_numeric(df[column], errors="coerce")
        df[column] = conversion(values)

    return df


# =====================================================
# Main function
# =====================================================


def standardize_units(df, source_name):

    units = load_unit_mapping(source_name)

    if units is None:

        units = create_unit_mapping(df)

        save_unit_mapping(units, source_name)

    else:

        units, changed = reconcile_unit_mapping(df, units)

        if changed:
            save_unit_mapping(units, source_name)

    df = convert_units(df, units)

    return df
