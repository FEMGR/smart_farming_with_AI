"""
Purpose
-------
Provide reusable interactive functions for selecting input directories/files
and choosing output filenames for the AI preprocessing pipeline.

Typical workflow
----------------
datasets/
    |
    +-- choose_directory()
    |     |
    |     v
    +-- choose_input_files()
          |
          v
    preprocessing / training
          |
          v
    choose_output_file()
"""

# ai/core/file_prompter.py

import re
from datetime import datetime
from pathlib import Path
from ai.core.constants import ARTIFACTS_DIR

# ==========================================================
# Project Paths
# ==========================================================

AI_FOLDER = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = AI_FOLDER / "datasets" / "raw"
PROCESSED_DATA_DIR = AI_FOLDER / "datasets" / "processed"


# ==========================================================
# Supported File Types
# ==========================================================

SUPPORTED_EXTENSIONS = {
    # Data formats
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
    ".parquet",
    # Image formats
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tiff",
    ".svg",
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
# Directory Helpers & Interactive Selection
# ==========================================================


def ensure_data_directories() -> None:
    """
    Make sure the default raw and processed dataset directories exist.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_subdirectories(base_directory: Path) -> list[Path]:
    """
    Return sorted subdirectories found within a given base path.
    """
    if not base_directory.exists():
        return []
    return sorted(
        [path for path in base_directory.iterdir() if path.is_dir()],
        key=lambda p: p.name.lower(),
    )


def choose_directory(
    default_base_dir: Path = RAW_DATA_DIR,
    prompt_label: str = "Select a Dataset Directory",
) -> Path:
    """
    Interactively ask the user to select an existing subdirectory or enter a custom path.

    Parameters
    ----------
    default_base_dir : Path
        Base folder to search for available dataset subdirectories.
    prompt_label : str
        Header label for the prompt screen.

    Returns
    -------
    Path
        Selected directory path.
    """
    ensure_data_directories()
    subdirs = get_subdirectories(default_base_dir)

    print("\n" + "=" * 60)
    print(prompt_label.upper())
    print("=" * 60)
    print(f"Base Directory: {default_base_dir}\n")

    if subdirs:
        print("Available Directories:")
        for idx, folder in enumerate(subdirs, start=1):
            print(f"{idx}. {folder.name} ({folder})")
        print(f"{len(subdirs) + 1}. [Custom Path] Enter manual path")
        print("0. Cancel")
    else:
        print("No subdirectories found in the base path.")
        print("1. [Custom Path] Enter manual path")
        print("0. Cancel")

    while True:
        choice = input("\nSelect directory option: ").strip()

        if choice == "0":
            raise KeyboardInterrupt("Directory selection cancelled.")

        # Selected an existing subdirectory
        if subdirs and choice.isdigit():
            val = int(choice)
            if 1 <= val <= len(subdirs):
                selected = subdirs[val - 1]
                print(f"\nSelected Directory: {selected}")
                return selected
            elif val == len(subdirs) + 1:
                # Custom path selected
                break

        if not subdirs and choice == "1":
            break

        print("Invalid choice. Please try again.")

    # Manual Custom Path Entry
    while True:
        custom_input = input("\nEnter custom directory path: ").strip()
        if not custom_input:
            print("Path cannot be empty.")
            continue

        custom_path = Path(custom_input).expanduser().resolve()
        if not custom_path.exists():
            print(f"Directory does not exist: {custom_path}")
            create_choice = input("Would you like to create this directory? [y/N]: ").strip().lower()
            if create_choice in {"y", "yes"}:
                custom_path.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {custom_path}")
                return custom_path
            continue

        if not custom_path.is_dir():
            print(f"The path specified is a file, not a directory: {custom_path}")
            continue

        print(f"\nSelected Directory: {custom_path}")
        return custom_path


# ==========================================================
# Find Available Input Files
# ==========================================================


def get_input_files(
    directory: Path = RAW_DATA_DIR,
    recursive: bool = False,
) -> list[Path]:
    """
    Return supported data files from the input directory.
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
    """
    print("\nHow many files do you want to use?")
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
    Supports: 1,3,5 | 1-4 | all
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

    return list(dict.fromkeys(selected_indexes))


def choose_input_files(
    directory: Path | None = None,
    recursive: bool = False,
    ask_selection_mode: bool = True,
    prompt_directory_first: bool = False,
) -> list[Path]:
    """
    Interactively ask the user to select one or multiple input datasets.
    """
    if prompt_directory_first or directory is None:
        directory = choose_directory(
            default_base_dir=directory or RAW_DATA_DIR,
            prompt_label="Select Input Directory",
        )

    files = get_input_files(
        directory=directory,
        recursive=recursive,
    )

    if not files:
        raise FileNotFoundError(f"No supported data files found in:\n{directory}")

    mode = "multiple"
    if ask_selection_mode:
        mode = choose_file_selection_mode()

    print("\n" + "=" * 60)
    print("AVAILABLE INPUT FILES")
    print("=" * 60)
    print(f"\nDirectory: {directory}")

    print("\nFiles:")
    display_files(files, base_directory=directory if recursive else None)
    print("\n0. Cancel")

    if mode == "single":
        while True:
            choice = input("\nSelect file: ").strip()

            if not choice.isdigit():
                print("Please enter a number.")
                continue

            val = int(choice)
            if val == 0:
                raise KeyboardInterrupt("File selection cancelled.")

            if 1 <= val <= len(files):
                selected_file = files[val - 1]
                print(f"\nSelected: {selected_file.name}")
                return [selected_file]

            print(f"Invalid selection. Please choose 0-{len(files)}.")

    while True:
        choice = input("\nSelect files (comma-separated, ranges like 1-3, or 'all'): ").strip()

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


def choose_input_file(
    directory: Path | None = None,
    prompt_directory_first: bool = False,
) -> Path:
    """
    Interactively ask the user to select an input dataset file.
    """
    selected_files = choose_input_files(
        directory=directory,
        ask_selection_mode=False,
        prompt_directory_first=prompt_directory_first,
    )
    return selected_files[0]


# ==========================================================
# Validate Output Filename & Extensions
# ==========================================================


def validate_output_filename(filename: str) -> bool:
    """Validate user-provided output filename."""
    filename = filename.strip()
    if not filename:
        return False

    path = Path(filename)
    if path.name != filename or filename in {".", ".."}:
        return False

    return True


def ensure_extension(filename: str, default_extension: str = ".csv") -> str:
    """Add a default extension if none is provided."""
    filename = filename.strip()
    if not Path(filename).suffix:
        filename += default_extension
    return filename


# ==========================================================
# User Confirmation & Menu Prompt Helpers
# ==========================================================


def confirm_overwrite(file_path: Path) -> bool:
    """Ask the user whether an existing file should be overwritten."""
    while True:
        choice = input(f"\nFile already exists:\n{file_path}\n\nOverwrite it? [y/N]: ").strip().lower()
        if choice in {"y", "yes"}:
            return True
        if choice in {"", "n", "no"}:
            return False
        print("Please enter Y or N.")


def prompt_menu_choice(prompt: str = "Choose an option: ") -> str | None:
    """Read menu choice safely handling KeyboardInterrupt."""
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return None


def pause_for_user(prompt: str = "\nPress Enter to continue...") -> bool:
    """Pause after an interactive action."""
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
    directory: Path | None = None,
    default_extension: str = ".csv",
    prompt_directory_first: bool = False,
) -> Path:
    """Interactively ask the user for an output directory and filename."""
    if prompt_directory_first or directory is None:
        directory = choose_directory(
            default_base_dir=directory or PROCESSED_DATA_DIR,
            prompt_label="Select Output Directory",
        )

    directory.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("OUTPUT FILE SELECTION")
    print("=" * 60)
    print(f"\nTarget directory: {directory}")

    while True:
        filename = input("\nEnter output filename: ").strip()

        if not validate_output_filename(filename):
            print("Invalid filename. Please enter a filename without path separators.")
            continue

        filename = ensure_extension(filename, default_extension)
        output_file = directory / filename

        if output_file.exists():
            if not confirm_overwrite(output_file):
                print("\nChoose another filename.")
                continue

        print(f"\nOutput path set: {output_file}")
        return output_file


def generate_output_filename(
    input_file: Path,
    directory: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Generate an automatic timestamped output filename."""
    directory.mkdir(parents=True, exist_ok=True)
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"{current_date}_cleaned_{input_file.stem}{input_file.suffix}"
    output_file = directory / filename

    if output_file.exists() and not confirm_overwrite(output_file):
        raise FileExistsError(f"Output file exists and overwrite declined:\n{output_file}")

    return output_file


def strip_existing_phase_prefix(stem: str) -> str:
    """Remove leading date and pipeline phase prefixes from a dataset filename."""
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
    """Generate an automatic output filename for a specific pipeline phase."""
    directory.mkdir(parents=True, exist_ok=True)
    current_date = datetime.now().strftime("%Y%m%d")
    base_stem = strip_existing_phase_prefix(input_file.stem)
    filename = f"{current_date}_{phase}_{base_stem}{input_file.suffix}"
    output_file = directory / filename

    if output_file.exists() and not confirm_overwrite(output_file):
        raise FileExistsError(f"Output file exists and overwrite declined:\n{output_file}")

    return output_file


def get_timestamped_artifact_dir(
    data_dir: Path | str,
    model_name: str,
    base_artifact_dir: Path = ARTIFACTS_DIR,
) -> Path:
    current_date = datetime.now().strftime("%Y%m%d")
    dataset_path = Path(data_dir)

    # If path ends in 'train' or 'val', step up to the root dataset folder name
    if dataset_path.stem.lower() in ["train", "val", "test"]:
        dataset_stem = dataset_path.parent.stem
    else:
        dataset_stem = dataset_path.stem

    artifact_dir = base_artifact_dir / f"{current_date}_{dataset_stem}" / model_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir


# ==========================================================
# Select Input + Output
# ==========================================================


def choose_files(prompt_directory_first: bool = False) -> tuple[Path, Path]:
    """Select both the input file and output file."""
    input_file = choose_input_file(prompt_directory_first=prompt_directory_first)
    output_file = generate_output_filename(input_file=input_file)
    return input_file, output_file


def display_file_information(input_file: Path, output_file: Path) -> None:
    """Display selected input and output paths."""
    print("\n" + "=" * 60)
    print("FILE SELECTION SUMMARY")
    print("=" * 60)
    print(f"\nInput : {input_file}")
    print(f"Output: {output_file}\n")


# ==========================================================
# Main Test Entry Point
# ==========================================================


def main() -> None:
    """Test interactive directory and file selection."""
    try:
        # Prompt for directory first
        selected_dir = choose_directory(
            default_base_dir=RAW_DATA_DIR,
            prompt_label="Choose Input Dataset Folder",
        )
        file = choose_input_file(directory=selected_dir)
        print(f"\nFinal Selected Dataset Path: {file}")

    except KeyboardInterrupt:
        print("\n\nSelection cancelled by user.")
    except Exception as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()
