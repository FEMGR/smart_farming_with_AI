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

import json
import re

import pandas as pd

from ai.core.constants import (
    UNIT_CONVERSIONS as CONVERSIONS,
    UNIT_FOLDER,
)
from ai.core.file_status import write_json_with_status


# =====================================================
# Configuration
# =====================================================


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

    write_json_with_status(
        units,
        path,
        description="unit mapping",
        indent=4,
    )


def load_unit_mapping(source_name):

    path = UNIT_FOLDER / f"{source_name}.json"

    if path.exists():

        with open(path) as file:
            return json.load(file)

    return None


# =====================================================
# Expected Units Metadata & Display
# =====================================================

EXPECTED_UNITS_INFO = {
    "temperature": {
        "target": "C",
        "labels": {"C": "Celsius (°C)", "F": "Fahrenheit (°F)", "K": "Kelvin (K)"},
    },
    "rainfall": {
        "target": "mm",
        "labels": {"mm": "Millimeters (mm)", "cm": "Centimeters (cm)", "inch": "Inches (in)"},
    },
    "wind_speed": {
        "target": "m/s",
        "labels": {"m/s": "Meters/second (m/s)", "km/h": "Kilometers/hour (km/h)", "mph": "Miles/hour (mph)"},
    },
    "pressure": {
        "target": "hPa",
        "labels": {"hPa": "Hectopascals (hPa)", "Pa": "Pascals (Pa)", "atm": "Atmospheres (atm)"},
    },
    "distance": {
        "target": "m",
        "labels": {"m": "Meters (m)", "ft": "Feet (ft)"},
    },
    "soil_moisture": {
        "target": "%",
        "labels": {"%": "Percentage (%)"},
    },
}


def print_expected_units_banner() -> None:
    print("\n" + "=" * 60)
    print("SPECIFY MEASUREMENT UNITS")
    print("=================================================")
    print("Supported & Accepted Units for Standardized Conversion:")
    for col, info in EXPECTED_UNITS_INFO.items():
        options = list(CONVERSIONS.get(col, {}).keys())
        labels = info.get("labels", {})
        accepted_str = ", ".join([labels.get(u, u) for u in options])
        target_str = labels.get(info.get("target", ""), info.get("target", ""))
        print(f"  • {col:15} : Accepted [{accepted_str}] -> Target [{target_str}]")
    print("=================================================")


# =====================================================
# Ask user
# =====================================================


def ask_unit(column_name: str) -> str | None:
    if column_name not in CONVERSIONS:
        return None

    options = list(CONVERSIONS[column_name].keys())
    info = EXPECTED_UNITS_INFO.get(column_name, {})
    labels = info.get("labels", {})
    target = info.get("target", options[0] if options else "")

    accepted_labels_str = ", ".join([labels.get(u, u) for u in options])

    print("\n" + "-" * 50)
    print(f"Column        : {column_name}")
    print(f"Accepted units: {accepted_labels_str}")
    if target:
        print(f"Target unit   : {labels.get(target, target)}")
    print("-" * 50)

    for i, unit in enumerate(options, start=1):
        label = labels.get(unit, unit)
        print(f"  {i}. {label} [{unit}]")

    accepted_inputs = ", ".join([f"{i} or '{u}'" for i, u in enumerate(options, start=1)])

    while True:
        choice = input(f"\nSpecify current unit ({accepted_inputs}): ").strip()

        if choice.isdigit():
            selected_index = int(choice)
            if 1 <= selected_index <= len(options):
                return options[selected_index - 1]

        for unit in options:
            if choice.lower() == unit.lower():
                return unit

        print(f"Invalid choice. Please enter a valid number (1-{len(options)}) " f"or unit symbol ({', '.join(options)}).")


# =====================================================
# Interactive mapping
# =====================================================


def create_unit_mapping(df: pd.DataFrame) -> dict:
    units = {}

    print_expected_units_banner()

    for column in df.columns:
        if column in CONVERSIONS:
            inferred_unit = infer_unit(df, column)

            if inferred_unit is not None:
                info = EXPECTED_UNITS_INFO.get(column, {})
                labels = info.get("labels", {})
                target = info.get("target", "")
                print(f"\nColumn        : {column}")
                print(f"Detected unit : {labels.get(inferred_unit, inferred_unit)} [{inferred_unit}]")
                print(f"Accepted units: {', '.join([labels.get(u, u) for u in CONVERSIONS[column]])}")
                if target:
                    print(f"Target unit   : {labels.get(target, target)}")
                units[column] = inferred_unit
                continue

            units[column] = ask_unit(column)

    return units


def prompt_existing_unit_mapping(df: pd.DataFrame, units: dict, source_name: str) -> dict:
    print("\n" + "=" * 60)
    print(f"Existing Unit Mapping Found for '{source_name}'")
    print("=" * 60)

    for col, unit in units.items():
        info = EXPECTED_UNITS_INFO.get(col, {})
        labels = info.get("labels", {})
        unit_label = labels.get(unit, unit)
        target = info.get("target", "")
        target_label = labels.get(target, target)
        print(f"  • {col:15} : {unit_label} [{unit}] -> Target [{target_label}]")

    print("=" * 60)
    print("Options:")
    print(" [Y] Accept and use existing unit mapping")
    print(" [E] Edit unit mapping")
    print(" [C] Cancel")

    while True:
        choice = input("\nSelect an option [Y/e/c]: ").strip().lower()

        if choice in ("", "y", "yes"):
            print(f"\nUsing existing unit mapping for '{source_name}'.")
            return units

        elif choice in ("e", "edit"):
            units = {}
            print_expected_units_banner()
            for column in df.columns:
                if column in CONVERSIONS:
                    units[column] = ask_unit(column)
            save_unit_mapping(units, source_name)
            print(f"\nSaved updated unit mapping for '{source_name}'.")
            return units

        elif choice in ("c", "cancel"):
            raise KeyboardInterrupt("Unit standardization cancelled.")

        else:
            print("Invalid selection. Please choose Y, E, or C.")


# =====================================================
# Convert dataframe
# =====================================================


def convert_units(df: pd.DataFrame, units: dict) -> pd.DataFrame:
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


def standardize_units(df: pd.DataFrame, source_name: str, interactive: bool = True) -> pd.DataFrame:
    units = load_unit_mapping(source_name)

    if units is None:
        if interactive:
            units = create_unit_mapping(df)
            save_unit_mapping(units, source_name)
        else:
            units = {}
            for column in df.columns:
                if column in CONVERSIONS:
                    inferred = infer_unit(df, column)
                    units[column] = inferred if inferred else list(CONVERSIONS[column].keys())[0]
            save_unit_mapping(units, source_name)

    else:
        units, changed = reconcile_unit_mapping(df, units)

        if changed:
            save_unit_mapping(units, source_name)
        elif interactive:
            units = prompt_existing_unit_mapping(df, units, source_name)

    df = convert_units(df, units)

    return df
