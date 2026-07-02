#!/usr/bin/env python3
"""
run_pnw_pest_pipeline.py

Runs the PNW pest data pipeline:

1. Build pest seed from Common Pests of Vegetable Crops
2. Extract normalized pest profiles
3. Export generated Prolog facts

Run from:
    plant_data_bank_scripts/

Examples:
    python3 scripts/pest/run_pnw_pest_pipeline.py
    python3 scripts/pest/run_pnw_pest_pipeline.py --limit 5
    python3 scripts/pest/run_pnw_pest_pipeline.py --only aphid
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(cmd: list[str], dry_run: bool = False) -> None:
    print("")
    print(">>>", " ".join(cmd))
    print(f"[CWD] {ROOT}")

    if dry_run:
        print("[DRY-RUN] Command not executed.")
        return

    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--only")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--update-prolog",
        action="store_true",
        help="Preview or apply generated PNW pest facts into live Prolog files after export.",
    )
    parser.add_argument(
        "--apply-prolog",
        action="store_true",
        help="Apply generated PNW pest facts to live Prolog files. Implies --update-prolog.",
    )

    args = parser.parse_args()
    if args.apply_prolog:
        args.update_prolog = True

    py = sys.executable

    run(
        [
            py,
            "scripts/pest/build_pnw_pest_seed.py",
            "--sleep",
            str(args.sleep),
        ],
        dry_run=args.dry_run,
    )

    extract_cmd = [
        py,
        "scripts/pest/extract_pnw_pest_profiles.py",
        "--sleep",
        str(args.sleep),
    ]

    if args.refresh:
        extract_cmd.append("--refresh")

    if args.limit is not None:
        extract_cmd.extend(["--limit", str(args.limit)])

    if args.only:
        extract_cmd.extend(["--only", args.only])

    run(extract_cmd, dry_run=args.dry_run)

    run(
        [
            py,
            "scripts/pest/merge_pest_profiles.py",
            "--clean-output",
        ],
        dry_run=args.dry_run,
    )

    run(
        [
            py,
            "scripts/pest/export_pests_to_prolog.py",
        ],
        dry_run=args.dry_run,
    )

    if args.update_prolog:
        update_cmd = [
            py,
            "scripts/prolog/update_prolog_from_pnw_pests.py",
        ]

        if args.apply_prolog:
            update_cmd.append("--apply")

        run(update_cmd, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
