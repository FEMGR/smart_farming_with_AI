"""

Purpose
-------
Provide reusable interactive functions for selecting input files
and choosing output filenames for the AI preprocessing pipeline.

Typical workflow
----------------
datasets/raw/
    |
    +-- plants.csv
    +-- sensor_readings.csv
    +-- weather.csv
    +-- weather.json
          |
          v
    choose_input_file()
          |
          v
    preprocessing
          |
          v
    choose_output_file()
          |
          v
datasets/processed/
    |
    +-- processed_file.csv


This module does NOT:
    - load the data
    - clean the data
    - normalize the data
    - standardize the data
    - perform feature engineering

It only handles file selection and output-file naming.
"""

# ai/core/file_prompter.py

import re
from datetime import datetime
from pathlib import Path

# ==========================================================
# Project Paths
# ==========================================================

# file_prompter.py
#       |
#       +-- preprocessing/
#               |
#               +-- ai/
#
# Therefore:
# Path(__file__).resolve().parent.parent
# gives the ai/ directory.

AI_FOLDER = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = AI_FOLDER / "datasets" / "raw" / "external"
PROCESSED_DATA_DIR = AI_FOLDER / "datasets" / "processed"


# ==========================================================
# Supported File Types
# ==========================================================

SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
    ".parquet",
}

FILENAME_PHASES = {
    "cleaned",
    "merged",
    "featured",
    "selected",
    "standardized",
    "normalized",
    "preprocessed",
}


# ==========================================================
# Directory Helpers
# ==========================================================


def ensure_data_directories() -> None:
    """
    Make sure the raw and processed dataset directories exist.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# Find Available Input Files
# ==========================================================


def get_input_files(
    directory: Path = RAW_DATA_DIR,
    recursive: bool = False,
) -> list[Path]:
    """
    Return supported data files from the input directory.

    Parameters
    ----------
    directory : Path
        Directory containing raw/input datasets.

    Returns
    -------
    list[Path]
        Sorted list of supported files.
    """

    if not directory.exists():
        return []

    paths = directory.rglob("*") if recursive else directory.iterdir()

    files = [file for file in paths if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS]

    return sorted(files, key=lambda path: path.name.lower())


# ==========================================================
# Display Files
# ==========================================================


def display_files(
    files: list[Path],
    base_directory: Path | None = None,
) -> None:
    """
    Display files as a numbered list.
    """

    for index, file in enumerate(files, start=1):
        display_name = file.name

        if base_directory is not None:
            try:
                display_name = str(file.relative_to(base_directory))
            except ValueError:
                display_name = str(file)

        print(f"{index}. {display_name}")


# ==========================================================
# Choose One Or Multiple Files
# ==========================================================


def choose_file_selection_mode() -> str:
    """
    Ask whether the user wants one file or multiple files.

    Returns
    -------
    str
        Either "single" or "multiple".
    """

    print("\nHow many files do you want to use for training?")
    print("1. One file")
    print("2. Multiple files")
    print("0. Cancel")

    while True:

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            raise KeyboardInterrupt("File selection cancelled.")

        if choice == "1":
            return "single"

        if choice == "2":
            return "multiple"

        print("Please choose 0, 1, or 2.")


def parse_file_selection(
    selection: str,
    file_count: int,
) -> list[int]:
    """
    Parse a comma-separated file selection into zero-based indexes.

    Supports:
        1,3,5
        1-4
        all
    """

    selection = selection.strip().lower()

    if selection == "all":
        return list(range(file_count))

    selected_indexes: list[int] = []

    for part in selection.split(","):

        part = part.strip()

        if not part:
            continue

        if "-" in part:
            start_text, end_text = part.split("-", 1)

            if not start_text.isdigit() or not end_text.isdigit():
                raise ValueError("Ranges must use numbers, for example 1-3.")

            start = int(start_text)
            end = int(end_text)

            if start > end:
                raise ValueError("Range start must be less than or equal to range end.")

            selected_indexes.extend(range(start - 1, end))
            continue

        if not part.isdigit():
            raise ValueError("Selections must be numbers, ranges, or 'all'.")

        selected_indexes.append(int(part) - 1)

    if not selected_indexes:
        raise ValueError("No files were selected.")

    invalid_indexes = [index for index in selected_indexes if index < 0 or index >= file_count]

    if invalid_indexes:
        raise ValueError(f"Please choose files between 1 and {file_count}.")

    # Preserve user order while removing duplicates.
    deduped_indexes = list(dict.fromkeys(selected_indexes))

    return deduped_indexes


def choose_input_files(
    directory: Path = RAW_DATA_DIR,
    recursive: bool = False,
    ask_selection_mode: bool = True,
) -> list[Path]:
    """
    Interactively ask the user to select one or multiple input datasets.

    Parameters
    ----------
    directory : Path
        Directory containing input datasets.

    recursive : bool
        Whether files in child directories should also be shown.

    ask_selection_mode : bool
        Whether to ask the user to choose between one and multiple files.

    Returns
    -------
    list[Path]
        Full paths to the selected files.
    """

    ensure_data_directories()

    files = get_input_files(
        directory=directory,
        recursive=recursive,
    )

    if not files:
        raise FileNotFoundError(f"No supported data files were found in:\n{directory}")

    mode = "multiple"

    if ask_selection_mode:
        mode = choose_file_selection_mode()

    print("\n" + "=" * 60)
    print("AVAILABLE INPUT FILES")
    print("=" * 60)

    print("\nDirectory:")
    print(directory)

    print("\nFiles:")
    display_files(
        files,
        base_directory=directory if recursive else None,
    )

    print("\n0. Cancel")

    if mode == "single":

        while True:

            choice = input("\nSelect file: ").strip()

            if not choice.isdigit():
                print("Please enter a number.")
                continue

            choice = int(choice)

            if choice == 0:
                raise KeyboardInterrupt("File selection cancelled.")

            if 1 <= choice <= len(files):
                selected_file = files[choice - 1]

                print("\nSelected:")
                print(f"  {selected_file.name}")

                return [selected_file]

            print(f"Invalid selection. " f"Please choose 0-{len(files)}.")

    while True:

        choice = input("\nSelect files " "(comma-separated, ranges like 1-3, or 'all'): ").strip()

        if choice == "0":
            raise KeyboardInterrupt("File selection cancelled.")

        try:
            selected_indexes = parse_file_selection(
                choice,
                file_count=len(files),
            )
        except ValueError as error:
            print(error)
            continue

        selected_files = [files[index] for index in selected_indexes]

        print("\nSelected:")
        for selected_file in selected_files:
            print(f"  {selected_file.name}")

        return selected_files


# ==========================================================
# Choose Input File
# ==========================================================


def choose_input_file(
    directory: Path = RAW_DATA_DIR,
) -> Path:
    """
    Interactively ask the user to select an input dataset.

    Parameters
    ----------
    directory : Path
        Directory containing input datasets.

    Returns
    -------
    Path
        Full path to the selected file.

    Raises
    ------
    FileNotFoundError
        If no supported files are available.
    """

    selected_files = choose_input_files(
        directory=directory,
        ask_selection_mode=False,
    )

    return selected_files[0]


# ==========================================================
# Validate Output Filename
# ==========================================================


def validate_output_filename(filename: str) -> bool:
    """
    Validate a user-provided output filename.

    Parameters
    ----------
    filename : str
        Filename entered by the user.

    Returns
    -------
    bool
        True if the filename is valid.
    """

    filename = filename.strip()

    if not filename:
        return False

    # Prevent directory traversal.
    path = Path(filename)

    if path.name != filename:
        return False

    # Prevent names such as "." or ".."
    if filename in {".", ".."}:
        return False

    return True


# ==========================================================
# Add File Extension
# ==========================================================


def ensure_extension(
    filename: str,
    default_extension: str = ".csv",
) -> str:
    """
    Add a default extension if the user did not provide one.

    Examples
    --------
    sensor_clean
        -> sensor_clean.csv

    sensor_clean.csv
        -> sensor_clean.csv

    Parameters
    ----------
    filename : str
        Desired output filename.

    default_extension : str
        Extension to add when none is supplied.

    Returns
    -------
    str
        Filename with an extension.
    """

    filename = filename.strip()

    if not Path(filename).suffix:
        filename += default_extension

    return filename


# ==========================================================
# Confirm Overwrite
# ==========================================================


def confirm_overwrite(file_path: Path) -> bool:
    """
    Ask the user whether an existing file should be overwritten.
    """

    while True:

        choice = input(f"\nFile already exists:\n" f"{file_path}\n\n" f"Overwrite it? [y/N]: ").strip().lower()

        if choice in {"y", "yes"}:
            return True

        if choice in {"", "n", "no"}:
            return False

        print("Please enter Y or N.")


def prompt_menu_choice(prompt: str = "Choose an option: ") -> str | None:
    """
    Read a menu choice and return None when the user interrupts input.
    """

    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return None


def pause_for_user(prompt: str = "\nPress Enter to continue...") -> bool:
    """
    Pause after an interactive action.

    Returns False when the user interrupts the pause.
    """

    try:
        input(prompt)
        return True
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return False


# ==========================================================
# Choose Output File
# ==========================================================


def choose_output_file(
    directory: Path = PROCESSED_DATA_DIR,
    default_extension: str = ".csv",
) -> Path:
    """
    Interactively ask the user for an output filename.

    The function:
        1. Creates the output directory if necessary.
        2. Asks for a filename.
        3. Adds .csv if no extension is provided.
        4. Checks whether the file already exists.
        5. Asks for overwrite confirmation.

    Parameters
    ----------
    directory : Path
        Directory where the processed file will be saved.

    default_extension : str
        Extension used when the user does not provide one.

    Returns
    -------
    Path
        Full output path.
    """

    directory.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("OUTPUT FILE")
    print("=" * 60)

    print("\nOutput directory:")
    print(directory)

    while True:

        filename = input("\nEnter output filename: ").strip()

        if not validate_output_filename(filename):

            print("Invalid filename. " "Please enter a filename only, " "without a directory path.")

            continue

        filename = ensure_extension(
            filename,
            default_extension,
        )

        output_file = directory / filename

        if output_file.exists():

            if not confirm_overwrite(output_file):
                print("\nChoose another filename.")
                continue

        print("\nOutput file:")
        print(f"  {output_file}")

        return output_file


def generate_output_filename(
    input_file: Path,
    directory=PROCESSED_DATA_DIR,
) -> Path:
    """
    Generate an automatic output filename.

    Format:
        YYYYMMDD_cleaned_<original_filename>

    Example:
        sensor_readings.csv
        ->
        20260814_cleaned_sensor_readings.csv
    """

    directory.mkdir(parents=True, exist_ok=True)

    current_date = datetime.now().strftime("%Y%m%d")

    filename = f"{current_date}_cleaned_" f"{input_file.stem}" f"{input_file.suffix}"

    output_file = directory / filename

    # Check whether the generated filename already exists.
    if output_file.exists():

        if not confirm_overwrite(output_file):
            raise FileExistsError(f"Output file already exists and overwrite was declined:\n" f"{output_file}")

    return output_file


def strip_existing_phase_prefix(stem: str) -> str:
    """
    Remove leading date and pipeline phase prefixes from a dataset filename.

    Examples
    --------
    20260821_cleaned_cropdata_updated
        -> cropdata_updated

    20260821_cleaned_20260821_cleaned_cropdata_updated
        -> cropdata_updated
    """

    parts = stem.split("_")

    while parts:
        if re.fullmatch(r"\d{8}", parts[0]):
            parts = parts[1:]
            continue

        if parts[0] in FILENAME_PHASES:
            parts = parts[1:]
            continue

        break

    return "_".join(parts) if parts else stem


def generate_phase_output_filename(
    input_file: Path,
    phase: str,
    directory: Path = PROCESSED_DATA_DIR,
) -> Path:
    """
    Generate an automatic output filename for a specific pipeline phase.

    Format:
        YYYYMMDD_<phase>_<base_filename>
    """

    directory.mkdir(parents=True, exist_ok=True)

    current_date = datetime.now().strftime("%Y%m%d")
    base_stem = strip_existing_phase_prefix(input_file.stem)
    filename = f"{current_date}_{phase}_{base_stem}{input_file.suffix}"
    output_file = directory / filename

    if output_file.exists() and not confirm_overwrite(output_file):
        raise FileExistsError(f"Output file already exists and overwrite was declined:\n{output_file}")

    return output_file


# ==========================================================
# Select Input + Output
# ==========================================================


def choose_files() -> tuple[Path, Path]:
    """
    Select both the input file and output file.

    Returns
    -------
    tuple[Path, Path]
        (input_file, output_file)
    """

    input_file = choose_input_file()

    output_file = generate_output_filename(
        input_file=input_file,
    )
    return input_file, output_file


# ==========================================================
# File Information
# ==========================================================


def display_file_information(
    input_file: Path,
    output_file: Path,
) -> None:
    """
    Display the selected input and output paths.
    """

    print("\n" + "=" * 60)
    print("FILE SELECTION SUMMARY")
    print("=" * 60)

    print("\nInput:")
    print(f"  {input_file}")

    print("\nOutput:")
    print(f"  {output_file}")

    print()


# ==========================================================
# Main Test
# ==========================================================


def main() -> None:
    """
    Test the file selection functions.

    This is only used when running file_prompter.py directly.

    Example
    -------
    python file_prompter.py
    """

    try:

        input_file, output_file = choose_files()

        display_file_information(
            input_file,
            output_file,
        )

    except KeyboardInterrupt:

        print("\n\nFile selection cancelled.")

    except FileNotFoundError as error:

        print(f"\nError: {error}")


# ==========================================================
# Script Entry Point
# ==========================================================

if __name__ == "__main__":
    main()
