"""
Purpose
-------
Run the complete preprocessing pipeline for every dataset or a single file.

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

# ai/preprocessing/preprocess_data.py
import pandas as pd
import argparse
import sys
from pathlib import Path
from typing import Callable, Optional

from ai.core.file_prompter import (
    RAW_DATA_DIR,
    choose_input_file,
    generate_phase_output_filename,
    pause_for_user,
    prompt_menu_choice,
)
from ai.core.menu_runner import MenuItem, MenuRunner
from ai.core.file_status import write_dataframe_csv_with_status
from ai.preprocessing.load_data import load_all_data, load_data_file, get_dataset_name
from data_bank.scripts.project_paths import PATHS
from ai.preprocessing.standardize_schema import standardize_schema
from ai.preprocessing.standardize_units import standardize_units
from ai.preprocessing.clean_data import clean_dataframe
from ai.preprocessing.normalize import normalize_dataframe, normalize_sensor_data

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def is_sensor_dataset(source_name: str) -> bool:
    """
    Return True for raw files that contain sensor readings.
    """
    return source_name == "sensor" or source_name.startswith("sensor_readings")


def infer_dataset_origin(source_name: str) -> str:
    """
    Keep external and local/application observations traceable.
    """

    external_markers = ("kaggle", "mendeley", "cropdata", "tomato irrigation")

    if any(marker in source_name.lower() for marker in external_markers):
        return "external"

    if source_name in {"sensor", "weather", "plants"}:
        return "local"

    return "unknown"


# =====================================================
# Preprocess a single dataset
# =====================================================


def preprocess_dataframe(df: pd.DataFrame, source_name: str, interactive: bool = True) -> pd.DataFrame:
    """
    Run the complete preprocessing pipeline on one DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw dataset.

    source_name : str
        Dataset name (sensor, weather, plants, etc.)

    interactive : bool
        Whether to prompt the user interactively during schema and unit standardization.

    Returns
    -------
    pandas.DataFrame
        Processed dataset.
    """

    print(f"\nPreprocessing: {source_name}")

    df = df.copy()
    df["dataset_source"] = source_name
    df["dataset_origin"] = infer_dataset_origin(source_name)

    # Step 1
    df = standardize_schema(df, source_name, interactive=interactive)

    # Step 2
    df = standardize_units(df, source_name, interactive=interactive)

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


# =========================================================
# MENU & WORKFLOW DRIVER
# =========================================================


def preprocess_custom_data(dry_run: bool = False, interactive: bool = True) -> Optional[pd.DataFrame]:
    """
    Prompt the user to select one file via file_prompter, preprocess it,
    and save the cleaned and normalized output file.
    """
    if dry_run:
        print("[DRY RUN] Would select a custom file via file_prompter and preprocess it.")
        return None

    try:
        input_file = choose_input_file(directory=RAW_DATA_DIR)
        output_file = generate_phase_output_filename(input_file=input_file, phase="preprocessed")
    except KeyboardInterrupt:
        print("\nFile selection cancelled.")
        return None
    except (FileNotFoundError, FileExistsError) as error:
        print(f"\nError: {error}")
        return None

    print(f"\nSelected Input File : {input_file}")
    print(f"Target Output File  : {output_file}")

    df = load_data_file(input_file)
    source_name = get_dataset_name(input_file, set())

    processed_df = preprocess_dataframe(df, source_name, interactive=interactive)

    write_dataframe_csv_with_status(
        processed_df,
        output_file,
        description="preprocessed dataset",
    )

    print("\nSingle file preprocessing completed successfully!")
    print(f"Processed dataset saved to:\n  {output_file}")

    return processed_df


def preprocess_all_data(dry_run: bool = False, interactive: bool = True) -> dict[str, pd.DataFrame]:
    """
    Load and preprocess every dataset in raw data folder (original process).

    Returns
    -------
    dict
        Dictionary containing processed DataFrames.
    """
    if dry_run:
        print("[DRY RUN] Would load and preprocess all raw datasets.")
        return {}

    datasets = load_all_data()

    processed = {}

    for source_name, df in datasets.items():
        processed[source_name] = preprocess_dataframe(df, source_name, interactive=interactive)

    return processed


def interactive_loop(dry_run: bool = False) -> None:
    PATHS.ensure_dirs()

    menu = MenuRunner(
        title="Preprocessing Menu",
        items=[
            MenuItem(
                key="1",
                label="Preprocessing on a custom file (using file_prompter)",
                action=preprocess_custom_data,
            ),
            MenuItem(
                key="2",
                label="Preprocessing on default datasets (original process)",
                action=preprocess_all_data,
            ),
            MenuItem(
                key="0",
                label="Exit",
                action=lambda dry_run: None,
            ),
        ],
        prompt_func=prompt_menu_choice,
        pause_func=pause_for_user,
        notes=[
            "Option 1 lets you pick a specific file via file_prompter.",
            "Option 2 runs feature engineering on default merged dataset.",
        ],
    )

    menu.run(dry_run=dry_run)


def run_non_interactive(command: str, dry_run: bool = False) -> None:
    shortcuts: dict[str, Callable[[bool], None]] = {
        "custom": lambda dry_run: preprocess_custom_data(dry_run=dry_run, interactive=False),
        "default": lambda dry_run: preprocess_all_data(dry_run=dry_run, interactive=False),
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
    parser = argparse.ArgumentParser(description="Interactive manager for Preprocessor")

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
