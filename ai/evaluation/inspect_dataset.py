"""


Purpose
-------
Inspect an ML training dataset before model evaluation.

Checks:
- Dataset shape
- Missing values
- Duplicate rows
- Target class distribution
- Unique values per categorical feature
- Numerical statistics
- Feature correlations
"""

# ai/evaluation/inspect_dataset.py

import argparse
import sys
from pathlib import Path
from typing import Callable

import pandas as pd

from data_bank.scripts.project_paths import PATHS
from ai.core.file_prompter import (
    PROCESSED_DATA_DIR,
    choose_input_file,
    pause_for_user,
    prompt_menu_choice,
)
from ai.core.menu_runner import MenuItem, MenuRunner


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# ==========================================================
# Paths
# ==========================================================

AI_FOLDER = Path(__file__).resolve().parent.parent

DEFAULT_DATA_FILE = AI_FOLDER / "datasets" / "processed" / "cropdata_updated.csv"


# ==========================================================
# Inspection Functions
# ==========================================================


def inspect_basic_info(df: pd.DataFrame) -> None:
    """Display basic dataset information."""

    print("\n" + "=" * 60)
    print("1. DATASET OVERVIEW")
    print("=" * 60)

    print(f"\nRows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)


def inspect_missing_values(df: pd.DataFrame) -> None:
    """Check missing values."""

    print("\n" + "=" * 60)
    print("2. MISSING VALUES")
    print("=" * 60)

    missing = df.isnull().sum()

    print(missing[missing > 0])

    if missing.sum() == 0:
        print("No missing values found.")


def inspect_duplicates(df: pd.DataFrame) -> None:
    """Check duplicate rows."""

    print("\n" + "=" * 60)
    print("3. DUPLICATE ROWS")
    print("=" * 60)

    duplicates = df.duplicated().sum()

    print(f"Duplicate rows: {duplicates}")

    if duplicates > 0:
        print("\nExample duplicates:")
        print(df[df.duplicated(keep=False)].head(10))


def inspect_target_distribution(df: pd.DataFrame, target: str = "watering_needed") -> None:
    """Check target class distribution."""

    print("\n" + "=" * 60)
    print("4. TARGET CLASS DISTRIBUTION")
    print("=" * 60)

    if target not in df.columns:
        print(f"Target column '{target}' not found.")
        return

    counts = df[target].value_counts()

    percentages = df[target].value_counts(normalize=True).mul(100).round(2)

    result = pd.DataFrame({"count": counts, "percentage": percentages})

    print(result)


def inspect_categorical_features(df: pd.DataFrame) -> None:
    """Inspect categorical feature diversity."""

    print("\n" + "=" * 60)
    print("5. CATEGORICAL FEATURE DIVERSITY")
    print("=" * 60)

    categorical_columns = df.select_dtypes(include=["object", "category"]).columns

    for column in categorical_columns:

        print(f"\n{column}")

        print(f"Unique values: {df[column].nunique()}")

        print("Top values:")

        print(df[column].value_counts().head(10))


def inspect_numerical_features(df: pd.DataFrame) -> None:
    """Inspect numerical feature statistics."""

    print("\n" + "=" * 60)
    print("6. NUMERICAL FEATURE STATISTICS")
    print("=" * 60)

    numerical_columns = df.select_dtypes(include=["number"]).columns

    print(df[numerical_columns].describe().T)


def inspect_correlations(df: pd.DataFrame) -> None:
    """Inspect correlations between numerical variables."""

    print("\n" + "=" * 60)
    print("7. NUMERICAL CORRELATIONS")
    print("=" * 60)

    numerical_df = df.select_dtypes(include=["number"])

    correlation = numerical_df.corr()

    print(correlation.round(3))


# ==========================================================
# Core Inspection Pipeline
# ==========================================================


def run_dataset_inspection(dataset_path: Path) -> None:
    """Load dataset from path and run all inspection functions."""

    if not dataset_path.exists():
        print(f"\nError: Dataset not found: {dataset_path}")
        return

    df = pd.read_csv(dataset_path)

    print("\nDATASET INSPECTION")
    print(f"File: {dataset_path}")

    inspect_basic_info(df)
    inspect_missing_values(df)
    inspect_duplicates(df)
    inspect_target_distribution(df)
    inspect_categorical_features(df)
    inspect_numerical_features(df)
    inspect_correlations(df)


# ==========================================================
# MENU & WORKFLOW DRIVER
# ==========================================================


def inspect_custom_dataset(dry_run: bool = False, interactive: bool = True) -> None:
    """Prompt user to choose a dataset via file_prompter and run inspection."""
    if dry_run:
        print("[DRY RUN] Would prompt for custom dataset file and run inspection.")
        return

    try:
        input_file = choose_input_file(directory=PROCESSED_DATA_DIR)
    except KeyboardInterrupt:
        print("\nFile selection cancelled.")
        return
    except (FileNotFoundError, FileExistsError) as error:
        print(f"\nError: {error}")
        return

    run_dataset_inspection(input_file)


def inspect_default_dataset(dry_run: bool = False, interactive: bool = True) -> None:
    """Run dataset inspection on default data file."""
    if dry_run:
        print(f"[DRY RUN] Would inspect default dataset file: {DEFAULT_DATA_FILE}")
        return

    run_dataset_inspection(DEFAULT_DATA_FILE)


def interactive_loop(dry_run: bool = False) -> None:
    PATHS.ensure_dirs()

    menu = MenuRunner(
        title="Dataset Inspection Menu",
        items=[
            MenuItem(
                key="1",
                label="Inspect custom dataset file (using file_prompter)",
                action=inspect_custom_dataset,
            ),
            MenuItem(
                key="2",
                label="Inspect default dataset file",
                action=inspect_default_dataset,
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
            "Option 1 lets you choose a specific dataset file to inspect.",
            "Option 2 inspects the default processed dataset file.",
        ],
    )

    menu.run(dry_run=dry_run)


def run_non_interactive(command: str, dry_run: bool = False) -> None:
    shortcuts: dict[str, Callable[[bool], None]] = {
        "custom": lambda dry_run: inspect_custom_dataset(dry_run=dry_run, interactive=False),
        "default": lambda dry_run: inspect_default_dataset(dry_run=dry_run, interactive=False),
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
    parser = argparse.ArgumentParser(description="Interactive manager for Dataset Inspection")

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
