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

import json

import pandas as pd
from rapidfuzz import fuzz

from ai.core.constants import (
    AUTO_ACCEPT_THRESHOLD as AUTO_ACCEPT,
    CANONICAL_COLUMNS,
    MAPPING_DIR,
    REVIEW_THRESHOLD as REVIEW,
)
from ai.core.file_status import write_json_with_status

# -----------------------------------------------------
# Mapping folder
# -----------------------------------------------------


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


def augment_mapping(
    existing_mapping: dict,
    detected_mapping: dict,
    detected_confidence: dict,
) -> tuple[dict, dict, bool]:
    """
    Add newly detected mappings without overriding saved user choices.
    """

    mapping = existing_mapping.copy()
    confidence = {canonical: 100.0 for canonical in mapping.values()}
    changed = False
    mapped_columns = set(mapping)
    mapped_canonicals = set(mapping.values())

    for source_column, canonical in detected_mapping.items():
        if source_column in mapped_columns or canonical in mapped_canonicals:
            continue

        mapping[source_column] = canonical
        confidence[canonical] = detected_confidence.get(canonical, 100.0)
        mapped_columns.add(source_column)
        mapped_canonicals.add(canonical)
        changed = True

    return mapping, confidence, changed


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

    write_json_with_status(
        mapping,
        path,
        description="schema mapping",
        indent=4,
    )


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
# Prompt Previous Mapping
# -----------------------------------------------------


def prompt_existing_mapping(df: pd.DataFrame, mapping: dict, api_name: str) -> dict:
    """
    Prompt the user to review, edit, or re-detect an existing saved schema mapping.
    """
    confidence = {canonical: 100.0 for canonical in mapping.values()}

    print("\n" + "=" * 60)
    print(f"Existing Schema Mapping Found for '{api_name}'")
    print("=" * 60)

    while True:
        print_summary(mapping, confidence)

        print("\nOptions for existing mapping:")
        print(" [Y] Accept and use existing mapping")
        print(" [E] Edit mapping")
        print(" [R] Re-detect columns from scratch")
        print(" [C] Cancel")

        choice = input("\nSelect an option [Y/e/r/c]: ").strip().lower()

        if choice in ("", "y", "yes"):
            print(f"\nUsing schema mapping for '{api_name}'.")
            return mapping

        elif choice in ("e", "edit"):
            mapping, confidence = edit_mapping(df, mapping, confidence)
            save_mapping(mapping, api_name)
            print(f"\nSaved updated schema mapping for '{api_name}'.")

        elif choice in ("r", "redetect", "re-detect"):
            mapping = create_mapping(df)
            save_mapping(mapping, api_name)
            return mapping

        elif choice in ("c", "cancel"):
            raise KeyboardInterrupt("Schema standardization cancelled.")

        else:
            print("Invalid selection. Please choose Y, E, R, or C.")


# -----------------------------------------------------
# Standardization
# -----------------------------------------------------


def standardize_schema(df: pd.DataFrame, api_name: str, interactive: bool = True):
    """
    Standardize schema by mapping dataset columns to canonical names.
    Prompts the user to review or edit existing mappings if present in interactive mode.
    """
    mapping = load_mapping(api_name)
    detected_mapping, detected_confidence = detect_columns(df)

    if mapping is None:
        if interactive:
            mapping = create_mapping(df)
            save_mapping(mapping, api_name)
        else:
            mapping = detected_mapping
    else:
        mapping, confidence, changed = augment_mapping(
            mapping,
            detected_mapping,
            detected_confidence,
        )

        if changed:
            save_mapping(mapping, api_name)

        if interactive:
            mapping = prompt_existing_mapping(df, mapping, api_name)

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

            score = confidence.get(canonical, 100.0)

            status = "✓"

            if score < AUTO_ACCEPT:
                status = "?"

            print(f"{status} {canonical:20}" f"{original:25}" f"{score}%")

        else:

            print(f"✗ {canonical:20}Not detected")

    print("=" * 60)
