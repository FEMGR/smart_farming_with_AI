"""
Purpose
-------
Merge multiple cleaned DataFrames into one AI-ready dataset.

Pipeline

load_data.py
      ↓
clean_data.py
      ↓
normalize.py
      ↓
merge_data.py
      ↓
train_model.py
"""

import argparse
import sys
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
from ai.core.constants import (
    CANONICAL_DUPLICATE_COLUMNS,
    MERGE_DATA_OUTPUT_FILE as OUTPUT_FILE,
)
from ai.core.file_prompter import (
    PROCESSED_DATA_DIR,
    choose_input_file,
    generate_phase_output_filename,
    pause_for_user,
    prompt_menu_choice,
)
from ai.core.file_status import write_dataframe_csv_with_status
from ai.preprocessing.load_data import load_data_file
from plant_data_bank_scripts.scripts.project_paths import PATHS

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


RECOMMENDED_ENRICHMENT_COLUMNS = [
    "plant_name",
    "scientific_name",
    "country",
    "dataset_source",
    "dataset_origin",
]


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """
    Ask a yes/no question for interactive merge workflows.
    """

    suffix = " [Y/n]: " if default else " [y/N]: "

    while True:
        answer = input(prompt + suffix).strip().lower()

        if not answer:
            return default

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("Please answer yes or no.")


def select_dataset_from_mapping(datasets: dict[str, pd.DataFrame]) -> tuple[str, pd.DataFrame]:
    """
    Ask the user to choose one processed dataset from an in-memory mapping.
    """

    names = list(datasets)

    if not names:
        raise ValueError("No datasets are available.")

    print("\nAvailable datasets")
    for index, name in enumerate(names, start=1):
        print(f"{index}. {name} {datasets[name].shape}")

    while True:
        choice = input("Choose one dataset to continue without merging: ").strip()

        if choice.isdigit():
            selected_index = int(choice) - 1

            if 0 <= selected_index < len(names):
                name = names[selected_index]
                return name, datasets[name]

        print("Invalid selection.")


def prompt_column_value_pairs(df: pd.DataFrame) -> list[tuple[str, str]]:
    """
    Ask the user which constant-value columns should be added to a dataset.
    """

    missing_recommended = [column for column in RECOMMENDED_ENRICHMENT_COLUMNS if column not in df.columns]

    if missing_recommended:
        print("\nRecommended missing columns:")
        for column in missing_recommended:
            print(f" - {column}")

    if not ask_yes_no("Do you want to add information columns to this dataset?", default=True):
        return []

    additions: list[tuple[str, str]] = []

    while True:
        column = input("Column name to add (blank to finish): ").strip()

        if not column:
            break

        value = input(f"Value for every row in '{column}': ").strip()
        additions.append((column, value))

        if not ask_yes_no("Add another column?", default=False):
            break

    return additions


def add_constant_columns(
    df: pd.DataFrame,
    additions: list[tuple[str, str]],
    interactive: bool = True,
) -> pd.DataFrame:
    """
    Add or update dataset-level information columns with one value per row.
    """

    enriched = df.copy()

    for column, value in additions:
        if not column:
            continue

        if column in enriched.columns and interactive:
            missing_mask = enriched[column].isna() | (enriched[column].astype(str).str.strip() == "")

            print(f"\nColumn '{column}' already exists.")
            print("1. Fill only missing values")
            print("2. Overwrite all values")
            print("3. Skip this column")

            choice = input("Choose an option [1]: ").strip() or "1"

            if choice == "2":
                enriched[column] = value
            elif choice == "3":
                continue
            else:
                enriched.loc[missing_mask, column] = value
        elif column in enriched.columns:
            missing_mask = enriched[column].isna() | (enriched[column].astype(str).str.strip() == "")
            enriched.loc[missing_mask, column] = value
        else:
            enriched[column] = value

    return enriched


def enrich_dataset_interactively(df: pd.DataFrame) -> pd.DataFrame:
    additions = prompt_column_value_pairs(df)
    return add_constant_columns(df, additions, interactive=True)


def save_unmerged_dataset(df: pd.DataFrame, output_file: Path) -> None:
    """
    Save a standalone dataset that intentionally skipped merging.
    """

    write_dataframe_csv_with_status(
        df,
        output_file,
        description="standalone merge-stage dataset",
    )


def normalize_location_id(series: pd.Series) -> pd.Series:
    """
    Normalize location IDs for joins while preserving non-numeric IDs.
    """

    normalized = series.astype("string").str.strip()
    numeric_values = pd.to_numeric(normalized, errors="coerce")
    integer_like = numeric_values.notna() & (numeric_values % 1 == 0)

    normalized.loc[integer_like] = numeric_values.loc[integer_like].astype("Int64").astype("string")

    return normalized.replace("", pd.NA)


def parse_timestamp(series: pd.Series) -> pd.Series:
    try:
        return pd.to_datetime(series, errors="coerce", format="mixed")
    except TypeError:
        return pd.to_datetime(series, errors="coerce")


def fill_from_first_available(df: pd.DataFrame, target: str, candidates: list[str]) -> pd.DataFrame:
    available_columns = [column for column in candidates if column in df.columns]

    if not available_columns:
        return df

    if target in df.columns:
        available_columns = [target, *available_columns]

    df[target] = df[available_columns].bfill(axis=1).iloc[:, 0]

    columns_to_drop = [column for column in candidates if column in df.columns]
    return df.drop(columns=columns_to_drop)


def resolve_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse pandas merge suffix columns into canonical columns.
    """

    df = df.copy()

    for canonical_column, duplicate_columns in CANONICAL_DUPLICATE_COLUMNS.items():
        df = fill_from_first_available(df, canonical_column, duplicate_columns)

    return df


def plant_with_weather(plants_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    plants_df = plants_df.copy()
    weather_df = weather_df.copy()
    plants_df["latitude"] = pd.to_numeric(plants_df["latitude"], errors="coerce")
    plants_df["longitude"] = pd.to_numeric(plants_df["longitude"], errors="coerce")
    weather_df["latitude"] = pd.to_numeric(weather_df["latitude"], errors="coerce")
    weather_df["longitude"] = pd.to_numeric(weather_df["longitude"], errors="coerce")

    plants_df["lat_round"] = plants_df["latitude"].round(4)
    plants_df["lon_round"] = plants_df["longitude"].round(4)

    weather_df["lat_round"] = weather_df["latitude"].round(4)
    weather_df["lon_round"] = weather_df["longitude"].round(4)

    plants_df = plants_df.dropna(subset=["lat_round", "lon_round"])
    weather_df = weather_df.dropna(subset=["lat_round", "lon_round"])

    return pd.merge(
        plants_df,
        weather_df,
        on=["lat_round", "lon_round"],
        how="inner",
    )


def merge_with_sensor(data_df: pd.DataFrame, sensor_df: pd.DataFrame) -> pd.DataFrame:
    data_df = data_df.copy()
    sensor_df = sensor_df.copy()
    data_df["location_id"] = normalize_location_id(data_df["location_id"])
    sensor_df["location_id"] = normalize_location_id(sensor_df["location_id"])
    sensor_df["timestamp"] = parse_timestamp(sensor_df["timestamp"])
    data_df["timestamp"] = parse_timestamp(data_df["timestamp"])
    data_df = data_df.dropna(subset=["timestamp", "location_id"])
    sensor_df = sensor_df.dropna(subset=["timestamp", "location_id"])
    return pd.merge(data_df, sensor_df, on=["timestamp", "location_id"], how="inner")


def merge_all_data(plants_df: pd.DataFrame, weather_df: pd.DataFrame, sensor_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge every dataset required by the AI pipeline.
    """

    merged = plant_with_weather(plants_df, weather_df)

    merged = merge_with_sensor(merged, sensor_df)

    merged = resolve_duplicate_columns(merged)

    return merged


def save_merged_data(df: pd.DataFrame, output_file: Path = OUTPUT_FILE) -> None:
    """
    Save the merged dataset.
    """

    write_dataframe_csv_with_status(
        df,
        output_file,
        description="merged dataset",
    )


# =====================================================
# Pipeline Workflows
# =====================================================


def merge_custom_data(dry_run: bool = False, interactive: bool = True) -> Optional[pd.DataFrame]:
    """
    Prompt user to merge custom preprocessed files or keep one dataset standalone.
    """
    if dry_run:
        print("[DRY RUN] Would ask whether to merge custom files or enrich one standalone dataset.")
        return None

    should_merge = True

    if interactive:
        should_merge = ask_yes_no("Do you want to merge multiple datasets?", default=True)

    if not should_merge:
        try:
            print("\n--- Select Dataset File ---")
            input_file = choose_input_file(directory=PROCESSED_DATA_DIR)
            output_file = generate_phase_output_filename(input_file=input_file, phase="merged")
        except KeyboardInterrupt:
            print("\nFile selection cancelled.")
            return None
        except (FileNotFoundError, FileExistsError) as error:
            print(f"\nError: {error}")
            return None

        print(f"\nSelected Dataset File: {input_file}")
        print(f"Target Output File   : {output_file}")

        dataset_df = load_data_file(input_file)
        dataset_df = enrich_dataset_interactively(dataset_df)
        save_unmerged_dataset(dataset_df, output_file=output_file)
        preview_dataset(dataset_df, title="Standalone Dataset")

        print("\nStandalone dataset preparation completed successfully!")
        return dataset_df

    try:
        print("\n--- Select Plants Dataset File ---")
        plants_file = choose_input_file(directory=PROCESSED_DATA_DIR)

        print("\n--- Select Weather Dataset File ---")
        weather_file = choose_input_file(directory=PROCESSED_DATA_DIR)

        print("\n--- Select Sensor Dataset File ---")
        sensor_file = choose_input_file(directory=PROCESSED_DATA_DIR)

        output_file = generate_phase_output_filename(input_file=plants_file, phase="merged")
    except KeyboardInterrupt:
        print("\nFile selection cancelled.")
        return None
    except (FileNotFoundError, FileExistsError) as error:
        print(f"\nError: {error}")
        return None

    print(f"\nSelected Plants File  : {plants_file}")
    print(f"Selected Weather File : {weather_file}")
    print(f"Selected Sensor File  : {sensor_file}")
    print(f"Target Output File    : {output_file}")

    plants_df = load_data_file(plants_file)
    weather_df = load_data_file(weather_file)
    sensor_df = load_data_file(sensor_file)

    merged_df = merge_all_data(plants_df, weather_df, sensor_df)
    save_merged_data(merged_df, output_file=output_file)
    preview_dataset(merged_df, title="Merged Dataset")

    print("\nCustom dataset merging completed successfully!")
    return merged_df


def merge_default_data(dry_run: bool = False, interactive: bool = True) -> Optional[pd.DataFrame]:
    """
    Load preprocessed raw datasets and either merge them or keep one standalone.
    """
    if dry_run:
        print("[DRY RUN] Would preprocess all raw datasets and ask whether to merge or enrich one standalone dataset.")
        return None

    from ai.preprocessing.preprocess_data import preprocess_all_data

    datasets = preprocess_all_data(interactive=interactive)

    print("\nShapes before merge")
    print("Plants :", datasets["plants"].shape if "plants" in datasets else "N/A")
    print("Weather:", datasets["weather"].shape if "weather" in datasets else "N/A")
    print("Sensor :", datasets["sensor"].shape if "sensor" in datasets else "N/A")

    should_merge = True

    if interactive:
        should_merge = ask_yes_no("Do you want to merge these datasets?", default=True)

    if not should_merge:
        try:
            dataset_name, dataset_df = select_dataset_from_mapping(datasets)
        except ValueError as error:
            print(f"\nError: {error}")
            return None

        print(f"\nSelected standalone dataset: {dataset_name}")
        dataset_df = enrich_dataset_interactively(dataset_df)
        save_unmerged_dataset(dataset_df, output_file=OUTPUT_FILE)
        preview_dataset(dataset_df, title="Standalone Dataset")

        print("\nDefault standalone dataset preparation completed successfully!")
        return dataset_df

    merged_df = merge_all_data(datasets["plants"], datasets["weather"], datasets["sensor"])
    print("Saving cleaned merged dataset...")
    save_merged_data(merged_df, output_file=OUTPUT_FILE)
    preview_dataset(merged_df, title="Merged Dataset")

    print("\nDefault data merging completed successfully!")
    return merged_df


# =====================================================
# Utility
# =====================================================


def preview_dataset(df: pd.DataFrame, title: str = "Dataset") -> None:
    """
    Display a summary of a prepared dataset.
    """

    print(f"\n{title}")
    print("-" * 50)

    print(df.head())

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nMissing Values:")
    print(df.isnull().sum())


# =========================================================
# MENU
# =========================================================

MENU: dict[str, tuple[str, Callable[[bool], None]]] = {
    "1": ("Merge custom files (using file_prompter)", merge_custom_data),
    "2": ("Merge all preprocessed data (original process)", merge_default_data),
    "0": ("Exit", lambda dry_run: None),
}


def print_menu(dry_run: bool) -> None:
    print("")
    print("=================================================")
    print("Merge Data Menu")
    print("=================================================")

    for key, (label, _) in MENU.items():
        print(f"{key}. {label}")

    print("")
    print("Note: Option 1 lets you pick specific dataset files via file_prompter.")
    print("      Option 2 runs default preprocessed data merging across all datasets.")
    print("=================================================")


def pause() -> None:
    pause_for_user()


def interactive_loop(dry_run: bool = False) -> None:
    PATHS.ensure_dirs()

    while True:
        print_menu(dry_run)
        choice = prompt_menu_choice()

        if choice is None:
            return

        if choice == "0":
            print("Goodbye.")
            return

        menu_item = MENU.get(choice)

        if not menu_item:
            print("Invalid option.")
            if not pause_for_user():
                return
            continue

        label, action = menu_item

        print("")
        print(f"Selected: {label}")

        action(dry_run)

        if not pause_for_user():
            return


def run_non_interactive(command: str, dry_run: bool = False) -> None:
    shortcuts: dict[str, Callable[[bool], None]] = {
        "custom": lambda dry_run: merge_custom_data(dry_run=dry_run, interactive=False),
        "default": lambda dry_run: merge_default_data(dry_run=dry_run, interactive=False),
    }

    action = shortcuts.get(command)

    if not action:
        print(f"Unknown command: {command}")
        print("")
        print("Available commands:")
        for key in shortcuts:
            print(f" - {key}")
        sys.exit(1)

    PATHS.ensure_dirs()
    action(dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive manager for Data Merger")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them where supported.",
    )

    parser.add_argument(
        "--command",
        choices=[
            "custom",
            "default",
        ],
        help="Run a workflow directly without opening the menu.",
    )

    args = parser.parse_args()

    if args.command:
        run_non_interactive(args.command, dry_run=args.dry_run)
    else:
        interactive_loop(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
