"""
Purpose
-------
Build task-specific training datasets from the master feature repository.

This script does not create new features. It only selects relevant columns from
featured_data.csv and writes one training CSV per model objective.
"""

# ai/preprocessing/feature_selection.py

import argparse
import sys
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
from ai.core.constants import (
    FEATURE_SEL_INPUT_FILE as INPUT_FILE,
    NON_MODEL_FEATURE_COLUMNS,
    TRAINING_DATASETS,
)
from ai.core.file_prompter import (
    PROCESSED_DATA_DIR,
    choose_input_file,
    generate_phase_output_filename,
    pause_for_user,
    prompt_menu_choice,
)
from ai.core.menu_runner import MenuItem, MenuRunner
from ai.core.file_status import write_dataframe_csv_with_status
from data_bank.scripts.project_paths import PATHS

# ==========================================================
# Project Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def selected_target_column(df: pd.DataFrame, target_candidates: list[str]) -> str | None:
    """
    Return the first available target candidate for a model.
    """

    for target in target_candidates:
        if target in df.columns:
            return target

    return None


def select_training_columns(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, list[str], str | None]:
    """
    Select model-specific feature columns and one available target column.
    """

    feature_columns = [column for column in config["features"] if column in df.columns and column not in NON_MODEL_FEATURE_COLUMNS]

    target_column = selected_target_column(df, config["target_candidates"])
    selected_columns = feature_columns.copy()

    if target_column is not None and target_column not in NON_MODEL_FEATURE_COLUMNS:
        selected_columns.append(target_column)

    missing_columns = [column for column in [*config["features"], *config["target_candidates"]] if column not in df.columns]

    return df.loc[:, selected_columns], missing_columns, target_column


def save_training_dataset(df: pd.DataFrame, output_file: Path) -> None:
    write_dataframe_csv_with_status(
        df,
        output_file,
        description="training dataset",
    )


def build_training_datasets(featured_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Build and save all configured training datasets.
    """

    training_datasets = {}

    for model_name, config in TRAINING_DATASETS.items():
        training_df, missing_columns, target_column = select_training_columns(featured_df, config)
        save_training_dataset(training_df, config["output_file"])
        training_datasets[model_name] = training_df

        print(f"\n{model_name}_training.csv")
        print(f"Saved to: {config['output_file']}")
        print(f"Shape: {training_df.shape}")

        if target_column is None:
            print(f"Target: missing. Expected one of {config['target_candidates']}")
        else:
            print(f"Target: {target_column}")

        if missing_columns:
            print(f"Missing optional columns: {missing_columns}")

    return training_datasets


def split_training_sets(
    featured_df: pd.DataFrame | None = None,
    input_file: Path = INPUT_FILE,
    selected_output_file: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Load the master feature repository and write task-specific training CSVs.
    """

    if featured_df is None:
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        featured_df = pd.read_csv(input_file)

    if selected_output_file is not None:
        write_dataframe_csv_with_status(
            featured_df,
            selected_output_file,
            description="selected feature repository",
        )

    return build_training_datasets(featured_df)


# =========================================================
# MENU & WORKFLOW DRIVER
# =========================================================


def feature_selection_custom_data(dry_run: bool = False, interactive: bool = True) -> Optional[dict[str, pd.DataFrame]]:
    """
    Prompt user to select a feature-engineered dataset file via file_prompter and build training datasets.
    """
    if dry_run:
        print("[DRY RUN] Would select a custom dataset file via file_prompter and run feature selection.")
        return None

    try:
        input_file = choose_input_file(directory=PROCESSED_DATA_DIR)
        output_file = generate_phase_output_filename(input_file=input_file, phase="feature_selection")
    except KeyboardInterrupt:
        print("\nFile selection cancelled.")
        return None
    except (FileNotFoundError, FileExistsError) as error:
        print(f"\nError: {error}")
        return None

    print(f"\nSelected Input File: {input_file}")
    print(f"Selected Output File: {output_file}")
    training_sets = split_training_sets(input_file=input_file, selected_output_file=output_file)

    print("\nCustom feature selection completed successfully!")
    return training_sets


def feature_selection_default_data(dry_run: bool = False, interactive: bool = True) -> Optional[dict[str, pd.DataFrame]]:
    """
    Run feature selection on default featured dataset file.
    """
    if dry_run:
        print(f"[DRY RUN] Would process default feature repository dataset: {INPUT_FILE}")
        return None

    if not INPUT_FILE.exists():
        print(f"\nError: Input file not found:\n{INPUT_FILE}")
        return None

    training_sets = split_training_sets(input_file=INPUT_FILE)

    print("\nDefault feature selection completed successfully!")
    return training_sets


def interactive_loop(dry_run: bool = False) -> None:
    PATHS.ensure_dirs()

    menu = MenuRunner(
        title="Feature Selection Menu",
        items=[
            MenuItem(
                key="1",
                label="Feature Selection on custom file (using file_prompter)",
                action=feature_selection_custom_data,
            ),
            MenuItem(
                key="2",
                label="Feature Selection on default merged data (original process)",
                action=feature_selection_default_data,
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
        "custom": lambda dry_run: feature_selection_custom_data(dry_run=dry_run, interactive=False),
        "default": lambda dry_run: feature_selection_default_data(dry_run=dry_run, interactive=False),
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


def main() -> Optional[dict[str, pd.DataFrame]]:
    parser = argparse.ArgumentParser(description="Interactive manager for Feature Selection")

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
        return None
    else:
        interactive_loop(dry_run=args.dry_run)
        return None


if __name__ == "__main__":
    main()
