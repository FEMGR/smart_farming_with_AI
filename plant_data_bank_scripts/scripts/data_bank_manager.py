#!/usr/bin/env python3
"""
plant_data_bank_scripts/scripts/data_bank_manager.py

Interactive workflow manager for the Smart Farming plant data bank.

Purpose:
- Centralize common data-bank workflows.
- Avoid repeatedly typing long commands.
- Let the user choose what to run.
- Reuse centralized project paths from project_paths.py.

Run from anywhere:

    python plant_data_bank_scripts/scripts/data_bank_manager.py

Recommended workflows:

1. Full known-seed rebuild:
    plants_seed.json
        -> extraction pipeline
        -> update Prolog
        -> reorder Prolog

2. Runtime Perenual discovery:
    backend/cache/species_snapshots
        -> perenual_enriched_species.json
        -> missing_plant_seed.json
        -> missing plant extraction
        -> update Prolog
        -> reorder Prolog
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

from project_paths import PATHS


ROOT = PATHS.plant_data_bank_scripts
PYTHON = sys.executable
SEED_GENERATOR_ROOT = PATHS.plant_data_bank_config / "plant_seed_generator"
PLANT_SEED_BUILDER_ROOT = SEED_GENERATOR_ROOT / "plant_seed_builder"
PFAF_CRAWLER_ROOT = SEED_GENERATOR_ROOT / "pfaf_crawler"


# =========================================================
# COMMAND HELPERS
# =========================================================


def run_command(cmd: list[str], dry_run: bool = False, cwd: Path = ROOT) -> bool:
    """
    Run one command from the requested working directory.
    """

    print("")
    print(">>>", " ".join(cmd))
    print(f"[CWD] {cwd}")

    if dry_run:
        print("[DRY-RUN] Command not executed.")
        return True

    try:
        subprocess.run(cmd, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as exc:
        print("")
        print(f"[ERROR] Command failed with exit code {exc.returncode}")
        return False


def ask_yes_no(question: str, default: bool = False) -> bool:
    default_text = "Y/n" if default else "y/N"

    while True:
        answer = input(f"{question} [{default_text}]: ").strip().lower()

        if not answer:
            return default

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("Please enter y or n.")


def ask_int(question: str, default: Optional[int] = None) -> Optional[int]:
    while True:
        suffix = f" [{default}]" if default is not None else " [blank = no limit]"
        answer = input(f"{question}{suffix}: ").strip()

        if not answer:
            return default

        try:
            value = int(answer)

            if value <= 0:
                print("Please enter a positive number.")
                continue

            return value
        except ValueError:
            print("Please enter a valid number.")


def ask_float(question: str, default: float) -> float:
    while True:
        answer = input(f"{question} [{default}]: ").strip()

        if not answer:
            return default

        try:
            return float(answer)
        except ValueError:
            print("Please enter a valid number.")


def ask_path(question: str, default: Path) -> Path:
    answer = input(f"{question} [{default}]: ").strip()

    if not answer:
        return default

    path = Path(answer).expanduser()

    if not path.is_absolute():
        path = (PATHS.project_root / path).resolve()

    return path


def choose_seed_file() -> Path:
    """
    Let user choose which plant seed JSON file to use.
    """

    options: dict[str, tuple[str, Path | None]] = {
        "1": ("Main plants_seed.json", PATHS.plants_seed),
        "2": ("Missing plant seed", PATHS.missing_plant_seed),
        "3": ("Missing plant runtime seed", PATHS.missing_plant_seed_runtime),
        "4": ("Custom path", None),
    }

    print("")
    print("Choose seed JSON file:")

    for key, (label, path) in options.items():
        if path is None:
            print(f"{key}. {label}")
        else:
            exists = "exists" if path.exists() else "missing"
            print(f"{key}. {label}: {path} [{exists}]")

    while True:
        choice = input("Seed option: ").strip()

        if choice not in options:
            print("Invalid option.")
            continue

        _, path = options[choice]

        if choice == "4":
            custom = input("Enter seed JSON path: ").strip()

            if not custom:
                print("Path cannot be empty.")
                continue

            custom_path = Path(custom).expanduser()

            if not custom_path.is_absolute():
                custom_path = (PATHS.project_root / custom_path).resolve()

            return custom_path

        assert path is not None
        return path


def pause() -> None:
    input("\nPress Enter to continue...")


def confirm_before_running(workflow_name: str, dry_run: bool) -> bool:
    print("")
    print(f"Workflow: {workflow_name}")
    print(f"Working directory: {ROOT}")
    print(f"Dry run: {dry_run}")

    return ask_yes_no("Continue?", default=True)


def confirm_file_overwrite(path: Path, dry_run: bool) -> bool:
    if dry_run or not path.exists():
        return True

    return ask_yes_no(f"Output file exists. Overwrite {path}?", default=False)


# =========================================================
# WORKFLOWS
# =========================================================


def show_paths(_: bool = False) -> None:
    PATHS.ensure_dirs()
    PATHS.print_summary()


def run_full_extraction(dry_run: bool = False) -> None:
    """
    Run the normal data extraction pipeline from a selected seed JSON file.
    """

    seed_path = choose_seed_file()

    if not seed_path.exists():
        print(f"[ERROR] Seed file does not exist: {seed_path}")
        return

    include_perenual = ask_yes_no(
        "Include direct Perenual API enrichment? Usually say no if you want to avoid API limits",
        default=False,
    )

    print("")
    print(f"Selected seed file: {seed_path}")

    if not confirm_before_running("Extraction from selected seed JSON", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/run_pipeline.py",
        "--plants",
        str(seed_path),
    ]

    if include_perenual:
        cmd.append("--include-perenual")

    run_command(cmd, dry_run=dry_run)


def sync_perenual_snapshots(dry_run: bool = False) -> None:
    """
    Sync backend/cache/species_snapshots into enriched data bank and missing seed.
    """

    if not confirm_before_running("Sync Perenual snapshots", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/enrich_from_perenual_snapshots.py",
        "--show-paths",
    ]

    run_command(cmd, dry_run=dry_run)


def run_missing_extraction(dry_run: bool = False) -> None:
    """
    Run extraction only for plants listed in missing_plant_seed.json.
    """

    limit = ask_int("Limit number of missing plants to process?", default=None)

    include_perenual = ask_yes_no(
        "Include direct Perenual API enrichment for missing plants?",
        default=False,
    )

    export_prolog = ask_yes_no(
        "Run export_to_prolog.py after missing extraction?",
        default=False,
    )

    prefer_common = ask_yes_no(
        "Prefer common name over scientific name for extraction query?",
        default=False,
    )

    if not confirm_before_running("Missing plant extraction", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/run_missing_plant_extraction.py",
        "--missing-seed",
        str(PATHS.missing_plant_seed),
    ]

    if limit is not None:
        cmd.extend(["--limit", str(limit)])

    if include_perenual:
        cmd.append("--include-perenual")

    if export_prolog:
        cmd.append("--export-prolog")

    if prefer_common:
        cmd.append("--prefer-common")

    if dry_run:
        cmd.append("--dry-run")

    run_command(cmd, dry_run=False)


def update_prolog_from_profiles(dry_run: bool = False) -> None:
    """
    Preview or apply Prolog updates from normalized plant profiles.
    """

    apply_changes = ask_yes_no(
        "Apply changes to Prolog files? Say no for preview only",
        default=False,
    )

    if not confirm_before_running("Update Prolog from normalized profiles", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/update_prolog_from_profiles.py",
        "--profiles",
        str(PATHS.normalized_plants),
        "--project-root",
        str(PATHS.project_root),
    ]

    if apply_changes:
        cmd.append("--apply")

    run_command(cmd, dry_run=dry_run)


def reorder_prolog_facts(dry_run: bool = False) -> None:
    """
    Reorder Prolog facts by plant.
    """

    apply_changes = ask_yes_no(
        "Apply reorder to actual Prolog files? Say no for preview only",
        default=False,
    )

    if not confirm_before_running("Reorder Prolog facts", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/reorder_prolog_facts_by_plant.py",
    ]

    if apply_changes:
        cmd.append("--apply")

    run_command(cmd, dry_run=dry_run)


def runtime_discovery_workflow(dry_run: bool = False) -> None:
    """
    Full runtime discovery workflow:

    1. Sync Perenual snapshots
    2. Run missing extraction
    3. Update Prolog
    4. Reorder Prolog
    """

    print("")
    print("Runtime discovery workflow:")
    print("1. Sync Perenual snapshots")
    print("2. Create/update missing_plant_seed.json")
    print("3. Run extraction for missing plants")
    print("4. Update Prolog from normalized profiles")
    print("5. Reorder Prolog facts")

    limit = ask_int("Limit missing plants to process?", default=None)

    apply_prolog = ask_yes_no(
        "Apply Prolog updates?",
        default=False,
    )

    apply_reorder = ask_yes_no(
        "Apply Prolog reorder?",
        default=False,
    )

    if not confirm_before_running("Full runtime Perenual discovery workflow", dry_run):
        return

    commands: list[list[str]] = []

    commands.append(
        [
            PYTHON,
            "scripts/enrich_from_perenual_snapshots.py",
        ]
    )

    missing_cmd = [
        PYTHON,
        "scripts/run_missing_plant_extraction.py",
        "--missing-seed",
        str(PATHS.missing_plant_seed),
    ]

    if limit is not None:
        missing_cmd.extend(["--limit", str(limit)])

    if dry_run:
        missing_cmd.append("--dry-run")

    commands.append(missing_cmd)

    prolog_cmd = [
        PYTHON,
        "scripts/update_prolog_from_profiles.py",
        "--profiles",
        str(PATHS.normalized_plants),
        "--project-root",
        str(PATHS.project_root),
    ]

    if apply_prolog:
        prolog_cmd.append("--apply")

    commands.append(prolog_cmd)

    reorder_cmd = [
        PYTHON,
        "scripts/reorder_prolog_facts_by_plant.py",
    ]

    if apply_reorder:
        reorder_cmd.append("--apply")

    commands.append(reorder_cmd)

    for cmd in commands:
        ok = run_command(cmd, dry_run=dry_run)

        if not ok:
            print("[STOP] Workflow stopped because a command failed.")
            return

    print("")
    print("[OK] Runtime discovery workflow finished.")


def known_seed_rebuild_workflow(dry_run: bool = False) -> None:
    """
    Full rebuild from a selected seed JSON file:

    1. Run extraction pipeline
    2. Update Prolog
    3. Reorder Prolog
    """

    print("")
    print("Known-seed rebuild workflow:")
    print("1. Run extraction from selected seed JSON")
    print("2. Update Prolog from normalized profiles")
    print("3. Reorder Prolog facts")

    seed_path = choose_seed_file()

    if not seed_path.exists():
        print(f"[ERROR] Seed file does not exist: {seed_path}")
        return

    include_perenual = ask_yes_no(
        "Include direct Perenual API enrichment? Usually say no because of API limits",
        default=False,
    )

    apply_prolog = ask_yes_no(
        "Apply Prolog updates?",
        default=False,
    )

    apply_reorder = ask_yes_no(
        "Apply Prolog reorder?",
        default=False,
    )

    print("")
    print(f"Selected seed file: {seed_path}")

    if not confirm_before_running("Full rebuild workflow from selected seed JSON", dry_run):
        return

    commands: list[list[str]] = []

    pipeline_cmd = [
        PYTHON,
        "scripts/run_pipeline.py",
        "--plants",
        str(seed_path),
    ]

    if include_perenual:
        pipeline_cmd.append("--include-perenual")

    commands.append(pipeline_cmd)

    prolog_cmd = [
        PYTHON,
        "scripts/update_prolog_from_profiles.py",
        "--profiles",
        str(PATHS.normalized_plants),
        "--project-root",
        str(PATHS.project_root),
    ]

    if apply_prolog:
        prolog_cmd.append("--apply")

    commands.append(prolog_cmd)

    reorder_cmd = [
        PYTHON,
        "scripts/reorder_prolog_facts_by_plant.py",
    ]

    if apply_reorder:
        reorder_cmd.append("--apply")

    commands.append(reorder_cmd)

    for cmd in commands:
        ok = run_command(cmd, dry_run=dry_run)

        if not ok:
            print("[STOP] Workflow stopped because a command failed.")
            return

    print("")
    print("[OK] Known-seed rebuild workflow finished.")


def generate_plant_seed(dry_run: bool = False) -> None:
    """
    Generate plants_seed.json using the seed generator helper scripts.
    """

    options = {
        "1": "Convert PFAF crawler output to seed JSON",
        "2": "Build seed JSON from plant_seed_builder/input_sources",
        "3": "Convert PFAF output, then build seed JSON",
    }

    print("")
    print("Generate plant seed JSON:")
    for key, label in options.items():
        print(f"{key}. {label}")

    while True:
        choice = input("Generator option: ").strip()

        if choice in options:
            break

        print("Invalid option.")

    output_path = ask_path("Output seed JSON path", PATHS.plants_seed)

    if not confirm_file_overwrite(output_path, dry_run):
        return

    commands: list[tuple[list[str], Path]] = []

    if choice in {"1", "3"}:
        pfaf_input = PFAF_CRAWLER_ROOT / "output" / "pfaf_edible_plants.json"
        pfaf_output = output_path

        if choice == "3":
            pfaf_output = PLANT_SEED_BUILDER_ROOT / "input_sources" / "pfaf_crawler_seed.json"

        if not pfaf_input.exists():
            print(f"[ERROR] PFAF crawler output does not exist: {pfaf_input}")
            return

        pfaf_cmd = [
            PYTHON,
            "scripts/convert_pfaf_to_plant_seed.py",
            "--input",
            str(pfaf_input),
            "--output",
            str(pfaf_output),
        ]

        if choice == "1" and ask_yes_no("Merge with existing output instead of replacing?", default=False):
            pfaf_cmd.append("--merge-existing")

        commands.append((pfaf_cmd, PFAF_CRAWLER_ROOT))

    if choice in {"2", "3"}:
        input_dir = ask_path(
            "Builder input_sources directory",
            PLANT_SEED_BUILDER_ROOT / "input_sources",
        )
        rejected_output = ask_path(
            "Rejected seed output path",
            PATHS.plant_data_bank_config / "plants_seed_rejected.json",
        )
        min_confidence = ask_float("Minimum confidence", default=0.0)

        if not input_dir.exists():
            print(f"[ERROR] Builder input directory does not exist: {input_dir}")
            return

        builder_cmd = [
            PYTHON,
            "scripts/build_plants_seed.py",
            "--input-dir",
            str(input_dir),
            "--output",
            str(output_path),
            "--rejected-output",
            str(rejected_output),
            "--min-confidence",
            str(min_confidence),
        ]

        commands.append((builder_cmd, PLANT_SEED_BUILDER_ROOT))

    print("")
    print(f"Selected generator: {options[choice]}")
    print(f"Output seed file: {output_path}")

    if choice == "3":
        print("PFAF intermediate seed: " f"{PLANT_SEED_BUILDER_ROOT / 'input_sources' / 'pfaf_crawler_seed.json'}")

    if not confirm_before_running("Generate plant seed JSON", dry_run):
        return

    for cmd, cwd in commands:
        ok = run_command(cmd, dry_run=dry_run, cwd=cwd)

        if not ok:
            print("[STOP] Seed generation stopped because a command failed.")
            return

    print("")
    print(f"[OK] Seed generation finished: {output_path}")


def validate_data_bank(dry_run: bool = False) -> None:
    if not confirm_before_running("Validate data bank", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/validate_data_bank.py",
    ]

    run_command(cmd, dry_run=dry_run)


def build_indexes(dry_run: bool = False) -> None:
    if not confirm_before_running("Build data bank indexes", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/build_indexes.py",
    ]

    run_command(cmd, dry_run=dry_run)


# =========================================================
# MENU
# =========================================================

MENU: dict[str, tuple[str, Callable[[bool], None]]] = {
    "1": ("Show resolved project paths", show_paths),
    "2": ("Run extraction from selected seed JSON", run_full_extraction),
    "3": ("Sync Perenual snapshots into data bank / missing seed", sync_perenual_snapshots),
    "4": ("Run missing plant extraction", run_missing_extraction),
    "5": ("Update Prolog from normalized profiles", update_prolog_from_profiles),
    "6": ("Reorder Prolog facts", reorder_prolog_facts),
    "7": ("Build data bank indexes", build_indexes),
    "8": ("Validate data bank", validate_data_bank),
    "9": ("Full runtime Perenual discovery workflow", runtime_discovery_workflow),
    "10": ("Full rebuild workflow from selected seed JSON", known_seed_rebuild_workflow),
    "11": ("Generate plant seed JSON", generate_plant_seed),
    "0": ("Exit", lambda dry_run: None),
}


def print_menu(dry_run: bool) -> None:
    print("")
    print("=================================================")
    print(" Smart Farming Plant Data Bank Manager")
    print("=================================================")
    print(f"Project root : {PATHS.project_root}")
    print(f"Data bank    : {PATHS.data_bank}")
    print(f"Dry-run mode : {dry_run}")
    print("-------------------------------------------------")

    for key, (label, _) in MENU.items():
        print(f"{key}. {label}")

    print("=================================================")


def interactive_loop(dry_run: bool = False) -> None:
    PATHS.ensure_dirs()

    while True:
        print_menu(dry_run)
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            return

        menu_item = MENU.get(choice)

        if not menu_item:
            print("Invalid option.")
            pause()
            continue

        label, action = menu_item

        print("")
        print(f"Selected: {label}")

        action(dry_run)

        pause()


# =========================================================
# NON-INTERACTIVE SHORTCUTS
# =========================================================


def run_non_interactive(command: str, dry_run: bool = False) -> None:
    shortcuts: dict[str, Callable[[bool], None]] = {
        "paths": show_paths,
        "extract": run_full_extraction,
        "sync-perenual": sync_perenual_snapshots,
        "missing": run_missing_extraction,
        "update-prolog": update_prolog_from_profiles,
        "reorder": reorder_prolog_facts,
        "indexes": build_indexes,
        "validate": validate_data_bank,
        "runtime": runtime_discovery_workflow,
        "rebuild": known_seed_rebuild_workflow,
        "generate-seed": generate_plant_seed,
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


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive manager for Smart Farming plant data bank workflows.")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them where supported.",
    )

    parser.add_argument(
        "--command",
        choices=[
            "paths",
            "extract",
            "sync-perenual",
            "missing",
            "update-prolog",
            "reorder",
            "indexes",
            "validate",
            "runtime",
            "rebuild",
            "generate-seed",
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
