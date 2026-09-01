#!/usr/bin/env python3
"""
data_bank/scripts/data_bank_manager.py

Interactive workflow manager for the Smart Farming plant data bank.

Purpose:
- Centralize common data-bank workflows.
- Avoid repeatedly typing long commands.
- Let the user choose what to run.
- Reuse centralized project paths from project_paths.py.

Run from anywhere:

    python data_bank/scripts/data_bank_manager.py

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
import json
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
    print("Note: options 1-3 use predefined files. Choose 4 to enter a custom path.")

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
        "scripts/plant/enrich_from_perenual_snapshots.py",
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

    update_live_prolog = ask_yes_no(
        "Update existing Prolog KB from normalized profiles after extraction?",
        default=False,
    )

    apply_prolog = False
    reorder_after_update = False
    apply_reorder = False

    if update_live_prolog:
        apply_prolog = ask_yes_no(
            "Apply Prolog updates? Say no for preview only",
            default=False,
        )

        reorder_after_update = ask_yes_no(
            "Run Prolog fact reorder after the update step?",
            default=False,
        )

        if reorder_after_update:
            apply_reorder = ask_yes_no(
                "Apply reorder to actual Prolog files? Say no for preview only",
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
        "scripts/plant/run_missing_plant_extraction.py",
        "--missing-seed",
        str(PATHS.missing_plant_seed),
    ]

    if limit is not None:
        cmd.extend(["--limit", str(limit)])

    if include_perenual:
        cmd.append("--include-perenual")

    if update_live_prolog:
        cmd.append("--update-prolog")

    if apply_prolog:
        cmd.append("--apply-prolog")

    if reorder_after_update:
        cmd.append("--reorder-prolog")

    if apply_reorder:
        cmd.append("--apply-reorder")

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
        "scripts/prolog/update_prolog_from_profiles.py",
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
        "scripts/prolog/reorder_prolog_facts_by_plant.py",
        "--project-root",
        str(PATHS.project_root),
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
            "scripts/plant/enrich_from_perenual_snapshots.py",
        ]
    )

    missing_cmd = [
        PYTHON,
        "scripts/plant/run_missing_plant_extraction.py",
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
        "scripts/prolog/update_prolog_from_profiles.py",
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
        "scripts/prolog/reorder_prolog_facts_by_plant.py",
        "--project-root",
        str(PATHS.project_root),
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
        "scripts/prolog/update_prolog_from_profiles.py",
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
        "scripts/prolog/reorder_prolog_facts_by_plant.py",
        "--project-root",
        str(PATHS.project_root),
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


def run_incremental_extraction(dry_run: bool = False) -> None:
    """
    Build a runtime seed for plants that need work, then run extraction.
    """

    print("")
    print("Incremental extraction workflow:")
    print("1. Build plants_seed_incremental_runtime.json from selected seed JSON")
    print("2. Include plants with no normalized profile")
    print("3. Include plants with missing fields that selected extractors can fill")
    print("4. Optionally include complete profiles older than the freshness threshold")
    print("5. Run extraction from the runtime seed")

    seed_path = choose_seed_file()

    if not seed_path.exists():
        print(f"[ERROR] Seed file does not exist: {seed_path}")
        return

    runtime_seed_path = ask_path(
        "Incremental runtime seed output path",
        PATHS.plants_seed_incremental_runtime,
    )

    if not confirm_file_overwrite(runtime_seed_path, dry_run):
        return

    include_perenual = ask_yes_no(
        "Include direct Perenual API enrichment? Usually say no because of API limits",
        default=False,
    )

    stale_days = ask_int("Freshness threshold in days", default=30)
    if stale_days is None:
        stale_days = 30

    include_stale_complete = ask_yes_no(
        "Include complete plants older than the freshness threshold?",
        default=False,
    )

    sources = ["gbif", "pfaf", "fpi"]

    if include_perenual:
        sources.append("perenual")

    print("")
    print(f"Selected seed file       : {seed_path}")
    print(f"Incremental runtime seed : {runtime_seed_path}")
    print(f"Selected extractors      : {', '.join(sources)}")
    print(f"Freshness threshold      : {stale_days} days")
    print(f"Include stale complete   : {include_stale_complete}")

    if not confirm_before_running("Incremental extraction from selected seed JSON", dry_run):
        return

    build_cmd = [
        PYTHON,
        "scripts/build_incremental_seed.py",
        "--plants",
        str(seed_path),
        "--output",
        str(runtime_seed_path),
        "--sources",
        ",".join(sources),
        "--stale-days",
        str(stale_days),
    ]

    if include_stale_complete:
        build_cmd.append("--include-stale-complete")

    if not run_command(build_cmd, dry_run=dry_run):
        print("[STOP] Incremental seed build failed.")
        return

    if not dry_run:
        try:
            runtime_items = json.loads(runtime_seed_path.read_text(encoding="utf-8"))
        except Exception:
            runtime_items = []

        if not runtime_items:
            print("[OK] Incremental runtime seed is empty. No extraction needed.")
            return

    pipeline_cmd = [
        PYTHON,
        "scripts/run_pipeline.py",
        "--plants",
        str(runtime_seed_path),
    ]

    if include_perenual:
        pipeline_cmd.append("--include-perenual")

    if not run_command(pipeline_cmd, dry_run=dry_run):
        print("[STOP] Incremental extraction failed.")
        return

    print("")
    print("[OK] Incremental extraction workflow finished.")


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


def extract_disease_bank(dry_run: bool = False) -> None:
    if not confirm_before_running("Extract disease bank from source pages", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/disease/extract_disease_bank.py",
        "--show-paths",
    ]

    if dry_run:
        cmd.append("--dry-run")

    run_command(cmd, dry_run=False)


def enrich_plants_with_disease_ids(dry_run: bool = False) -> None:
    preview_only = ask_yes_no(
        "Preview only without modifying plant profiles?",
        default=True,
    )

    if not confirm_before_running("Enrich plant profiles with known_disease_ids", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/plant/enrich_plants_with_disease_ids.py",
    ]

    if dry_run or preview_only:
        cmd.append("--dry-run")

    run_command(cmd, dry_run=False)


def extract_disease_details(dry_run: bool = False) -> None:
    only = input("Only enrich one disease? Enter disease ID or leave blank for all: ").strip()

    limit = ask_int(
        "Limit number of disease detail pages to process?",
        default=None,
    )

    overwrite = ask_yes_no(
        "Overwrite/re-extract existing disease details?",
        default=False,
    )

    if not confirm_before_running("Extract disease details into disease_bank.json", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/disease/extract_disease_details.py",
    ]

    if only:
        cmd.extend(["--only", only])

    if limit is not None:
        cmd.extend(["--limit", str(limit)])

    if overwrite:
        cmd.append("--overwrite")

    if dry_run:
        cmd.append("--dry-run")

    run_command(cmd, dry_run=False)


def extract_pest_bank(dry_run: bool = False) -> None:
    """
    Extract pest-to-plant mappings into normalized pest_bank.json.bak.
    """

    use_local_html = ask_yes_no(
        "Use a local saved HTML file instead of fetching from URL?",
        default=False,
    )

    local_html_path = None

    if use_local_html:
        local_html_input = input("Enter local HTML path, relative to project root or absolute: ").strip()

        if not local_html_input:
            print("[ERROR] Local HTML path cannot be empty.")
            return

        local_html_path = local_html_input

    if not confirm_before_running("Extract pest bank from source pages", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/pest/extract_pest_bank.py",
        "--show-paths",
    ]

    if local_html_path:
        cmd.extend(["--local-html", local_html_path])

    if dry_run:
        cmd.append("--dry-run")

    # dry-run is handled by the child script.
    run_command(cmd, dry_run=False)


def enrich_plants_with_pest_ids(dry_run: bool = False) -> None:
    """
    Add lightweight known_pest_ids to normalized plant profiles.
    """

    print("")
    print("Pest enrichment scope:")
    print("1. All normalized plant profiles")
    print("2. One plant only")

    while True:
        scope = input("Choose scope [1]: ").strip() or "1"

        if scope in {"1", "2"}:
            break

        print("Please enter 1 or 2.")

    only = ""

    if scope == "2":
        only = input("Enter plant atom or filename stem: ").strip()

        if not only:
            print("[ERROR] Plant atom cannot be empty when choosing one plant only.")
            return

    replace_existing = ask_yes_no(
        "Replace existing known_pest_ids instead of appending?",
        default=False,
    )

    preview_only = ask_yes_no(
        "Preview only without modifying plant profiles?",
        default=True,
    )

    if not confirm_before_running("Enrich plant profiles with known_pest_ids", dry_run):
        return

    print("")
    print(f"Selected scope: {'all plant profiles' if not only else only}")

    cmd = [
        PYTHON,
        "scripts/plant/enrich_plants_with_pest_ids.py",
    ]

    if only:
        cmd.extend(["--only", only])

    if replace_existing:
        cmd.append("--replace")

    if dry_run or preview_only:
        cmd.append("--dry-run")

    # dry-run is handled by the child script.
    run_command(cmd, dry_run=False)


def extract_pest_details(dry_run: bool = False) -> None:
    only = input("Only enrich one pest? Enter pest ID or leave blank for all: ").strip()

    limit = ask_int(
        "Limit number of pest detail pages to process?",
        default=None,
    )

    overwrite = ask_yes_no(
        "Overwrite/re-extract existing pest details?",
        default=False,
    )

    if not confirm_before_running("Extract pest details into pest_bank.json.bak", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/pest/extract_pest_details.py",
    ]

    if only:
        cmd.extend(["--only", only])

    if limit is not None:
        cmd.extend(["--limit", str(limit)])

    if overwrite:
        cmd.append("--overwrite")

    if dry_run:
        cmd.append("--dry-run")

    run_command(cmd, dry_run=False)


def run_pnw_pest_pipeline(dry_run: bool = False) -> None:
    """
    Build PNW vegetable pest seed data, extract normalized PNW pest profiles,
    and export generated Prolog facts.
    """

    sleep_seconds = ask_float(
        "Sleep seconds between PNW requests",
        default=1.0,
    )

    refresh = ask_yes_no(
        "Refresh cached PNW pest detail pages?",
        default=False,
    )

    only = input("Only extract one PNW pest atom? Leave blank for all: ").strip()

    limit = ask_int(
        "Limit number of PNW pests_ver01 to process?",
        default=None,
    )

    update_live_prolog = ask_yes_no(
        "Update live Prolog from generated PNW pest facts after export?",
        default=False,
    )

    apply_prolog = False
    if update_live_prolog:
        apply_prolog = ask_yes_no(
            "Apply PNW pest Prolog updates? Say no for preview only",
            default=False,
        )

    if not confirm_before_running("Run PNW pest extraction pipeline", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/pest/run_pnw_pest_pipeline.py",
        "--sleep",
        str(sleep_seconds),
    ]

    if refresh:
        cmd.append("--refresh")

    if only:
        cmd.extend(["--only", only])

    if limit is not None:
        cmd.extend(["--limit", str(limit)])

    if update_live_prolog:
        cmd.append("--update-prolog")

    if apply_prolog:
        cmd.append("--apply-prolog")

    run_command(cmd, dry_run=dry_run)


def update_prolog_from_pnw_pests(dry_run: bool = False) -> None:
    """
    Append generated PNW pest Prolog facts into insect_fact.pl,
    insect_group.pl, and sources_fact.pl.
    """

    apply_changes = ask_yes_no(
        "Apply generated PNW pest facts to live Prolog files? Say no for preview only",
        default=False,
    )

    if not confirm_before_running("Update Prolog from generated PNW pest facts", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/prolog/update_prolog_from_pnw_pests.py",
    ]

    if apply_changes:
        cmd.append("--apply")

    run_command(cmd, dry_run=dry_run)


def merge_pest_profiles(dry_run: bool = False) -> None:
    """
    Merge normalized/pests and normalized/pests_ver01 into normalized/pests_merged.
    """

    output_dir = ask_path(
        "Merged pest profile output directory",
        PATHS.data_bank_normalized / "pests_merged",
    )

    clean_output = ask_yes_no(
        "Clean output directory before writing merged profiles?",
        default=True,
    )

    if not confirm_before_running("Merge normalized pest profile directories", dry_run):
        return

    cmd = [
        PYTHON,
        "scripts/pest/merge_pest_profiles.py",
        "--output-dir",
        str(output_dir),
    ]

    if clean_output:
        cmd.append("--clean-output")

    if dry_run:
        cmd.append("--dry-run")

    run_command(cmd, dry_run=False)


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
    "12": ("Run incremental extraction from selected seed JSON", run_incremental_extraction),
    "13": ("Extract disease bank from source pages", extract_disease_bank),
    "14": ("Enrich plant profiles with disease IDs", enrich_plants_with_disease_ids),
    "15": ("Extract disease details into disease bank", extract_disease_details),
    "16": ("Extract pest bank from source pages", extract_pest_bank),
    "17": ("Enrich plant profiles with pest IDs", enrich_plants_with_pest_ids),
    "18": ("Extract pest details into pest bank", extract_pest_details),
    "19": ("Run PNW pest extraction pipeline", run_pnw_pest_pipeline),
    "20": ("Update Prolog from generated PNW pest facts", update_prolog_from_pnw_pests),
    "21": ("Merge PNW pest profile directories", merge_pest_profiles),
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

    print("")
    print("Note: option 2 opens a seed-file menu; choose seed option 4 there to enter a custom path.")
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
        "incremental": run_incremental_extraction,
        "extract-diseases": extract_disease_bank,
        "enrich-diseases": enrich_plants_with_disease_ids,
        "extract-disease-details": extract_disease_details,
        "extract-pests": extract_pest_bank,
        "extract-pests_ver01": extract_pest_bank,
        "enrich-pests": enrich_plants_with_pest_ids,
        "enrich-pests_ver01": enrich_plants_with_pest_ids,
        "extract-pest-details": extract_pest_details,
        "pnw-pests": run_pnw_pest_pipeline,
        "pnw-pests_ver01": run_pnw_pest_pipeline,
        "update-pnw-pests-prolog": update_prolog_from_pnw_pests,
        "merge-pests": merge_pest_profiles,
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
            "incremental",
            "extract-diseases",
            "enrich-diseases",
            "extract-pests",
            "extract-pests_ver01",
            "enrich-pests",
            "enrich-pests_ver01",
            "extract-disease-details",
            "extract-pest-details",
            "pnw-pests",
            "pnw-pests_ver01",
            "update-pnw-pests-prolog",
            "merge-pests",
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
