#!/usr/bin/env python3
"""
run_missing_plant_extraction.py

Purpose:
- Read data/seeds/missing_plant_seed.json
- Build a plant list from missing plants
- Run your existing extraction scripts only for those plants

Default pipeline:
    scripts/plant/extract_fpi.py
    scripts/plant/extract_pfaf.py
    scripts/plant/enrich_gbif.py
    scripts/plant/merge_profiles.py
    scripts/build_indexes.py
    scripts/validate_data_bank.py

Optional:
    scripts/plant/enrich_perenual.py
    scripts/prolog/update_prolog_from_profiles.py
    scripts/prolog/reorder_prolog_facts_by_plant.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_paths import PATHS  # noqa: E402

ROOT = PATHS.plant_data_bank_scripts


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}") from exc


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def choose_plant_query(item: Dict[str, Any], prefer_scientific: bool) -> Optional[str]:
    """
    Choose the best query for external extraction.

    For unknown plants, scientific name is usually safer.
    But if you prefer common names, use --prefer-common.
    """

    scientific_name = item.get("scientific_name")
    common_name = item.get("common_name")
    plant_atom = item.get("plant_atom")

    if prefer_scientific:
        return scientific_name or common_name or plant_atom

    return common_name or scientific_name or plant_atom


def build_missing_plant_list(
    missing_seed_path: Path,
    include_completed: bool,
    prefer_scientific: bool,
    limit: Optional[int],
) -> List[Dict[str, Any]]:
    seed = load_json(missing_seed_path, default=[])

    if not isinstance(seed, list):
        raise RuntimeError(f"Expected JSON list in {missing_seed_path}")

    plants: List[Dict[str, Any]] = []
    seen = set()

    for item in seed:
        if not isinstance(item, dict):
            continue

        status = item.get("status")

        if not include_completed and status in ["extracted", "completed", "validated"]:
            continue

        query = choose_plant_query(item, prefer_scientific=prefer_scientific)

        if not query:
            continue

        key = query.strip().lower()

        if key not in seen:
            seen.add(key)
            plants.append(dict(item))

        if limit is not None and len(plants) >= limit:
            break

    return plants


def run_command(cmd: List[str], dry_run: bool) -> None:
    print("")
    print(">>>", " ".join(cmd))

    if dry_run:
        return

    subprocess.run(cmd, cwd=ROOT, check=True)


def mark_seed_as_attempted(missing_seed_path: Path, plants: List[str]) -> None:
    seed = load_json(missing_seed_path, default=[])

    if not isinstance(seed, list):
        return

    plant_keys = {p.strip().lower() for p in plants}

    for item in seed:
        if not isinstance(item, dict):
            continue

        possible_keys = {
            str(item.get("scientific_name") or "").strip().lower(),
            str(item.get("common_name") or "").strip().lower(),
            str(item.get("plant_atom") or "").strip().lower(),
        }

        if plant_keys.intersection(possible_keys):
            if item.get("status") == "pending_extraction":
                item["status"] = "extraction_attempted"

    save_json(missing_seed_path, seed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run extraction pipeline only for plants listed in missing_plant_seed.json.")

    parser.add_argument(
        "--missing-seed",
        default=str(PATHS.missing_plant_seed),
        help="Missing plant seed JSON path.",
    )

    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Print resolved project paths before running.",
    )

    parser.add_argument(
        "--include-perenual",
        action="store_true",
        help="Also run scripts/plant/enrich_perenual.py. Usually unnecessary because snapshots already came from Perenual.",
    )

    parser.add_argument(
        "--prefer-common",
        action="store_true",
        help="Use common_name before scientific_name for extraction queries.",
    )

    parser.add_argument(
        "--update-prolog",
        action="store_true",
        help="Run scripts/prolog/update_prolog_from_profiles.py after data-bank validation.",
    )

    parser.add_argument(
        "--apply-prolog",
        action="store_true",
        help="Append missing facts to the live Prolog KB. Without this, the Prolog update step is preview-only.",
    )

    parser.add_argument(
        "--reorder-prolog",
        action="store_true",
        help="Run scripts/prolog/reorder_prolog_facts_by_plant.py after the Prolog update step.",
    )

    parser.add_argument(
        "--apply-reorder",
        action="store_true",
        help="Apply Prolog fact reordering. Without this, the reorder step is preview-only.",
    )

    parser.add_argument(
        "--include-completed",
        action="store_true",
        help="Also include seed items already marked extracted/completed/validated.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of missing plants to process.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands but do not run them.",
    )

    args = parser.parse_args()
    PATHS.ensure_dirs()

    if args.apply_prolog:
        args.update_prolog = True

    if args.apply_reorder:
        args.reorder_prolog = True

    if args.show_paths:
        PATHS.print_summary()

    missing_seed_path = Path(args.missing_seed)

    plant_records = build_missing_plant_list(
        missing_seed_path=missing_seed_path,
        include_completed=args.include_completed,
        prefer_scientific=not args.prefer_common,
        limit=args.limit,
    )

    if not plant_records:
        print("[OK] No missing plants to extract.")
        return

    plants = [choose_plant_query(item, prefer_scientific=not args.prefer_common) for item in plant_records]
    plants = [plant for plant in plants if plant]
    runtime_seed_path = PATHS.missing_plant_seed_runtime
    plants_arg = str(runtime_seed_path)

    print("")
    print("========== Missing Plant Extraction ==========")
    print(f"Missing seed file : {missing_seed_path}")
    print(f"Runtime seed file : {runtime_seed_path}")
    print(f"Plants to process : {len(plant_records)}")
    print("----------------------------------------------")

    for plant in plants:
        print(f" - {plant}")

    print("==============================================")

    py = sys.executable

    if not args.dry_run:
        save_json(runtime_seed_path, plant_records)

    pipeline = [
        [py, "scripts/plant/extract_fpi.py", "--plants", plants_arg],
        [py, "scripts/plant/extract_pfaf.py", "--plants", plants_arg],
        [py, "scripts/plant/enrich_gbif.py", "--plants", plants_arg],
    ]

    if args.include_perenual:
        pipeline.append([py, "scripts/plant/enrich_perenual.py", "--plants", plants_arg])

    pipeline.extend(
        [
            [py, "scripts/plant/merge_profiles.py", "--plants", plants_arg],
            [py, "scripts/build_indexes.py"],
            [py, "scripts/validate_data_bank.py"],
        ]
    )

    for cmd in pipeline:
        run_command(cmd, dry_run=args.dry_run)

    if args.update_prolog:
        prolog_cmd = [
            py,
            "scripts/prolog/update_prolog_from_profiles.py",
            "--profiles",
            str(PATHS.normalized_plants),
            "--project-root",
            str(PATHS.project_root),
        ]

        if args.apply_prolog:
            prolog_cmd.append("--apply")

        run_command(prolog_cmd, dry_run=args.dry_run)

    if args.reorder_prolog:
        reorder_cmd = [
            py,
            "scripts/prolog/reorder_prolog_facts_by_plant.py",
            "--project-root",
            str(PATHS.project_root),
        ]

        if args.apply_reorder:
            reorder_cmd.append("--apply")

        run_command(reorder_cmd, dry_run=args.dry_run)

    if not args.dry_run:
        mark_seed_as_attempted(missing_seed_path, plants)
        print(f"[OK] Marked processed seed items as extraction_attempted in {missing_seed_path}")

    print("[OK] Missing plant extraction pipeline finished.")


if __name__ == "__main__":
    main()
