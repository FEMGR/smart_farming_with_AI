#!/usr/bin/env python3
"""
sync_perenual_discoveries.py

Convenience launcher:
1. Enrich data bank from Perenual snapshots.
2. Dry-run or run missing plant extraction.

Run:
python3 plant_data_bank_scripts/scripts/sync_perenual_discoveries.py --show-paths

Or with missing extraction:
python3 plant_data_bank_scripts/scripts/sync_perenual_discoveries.py \
  --extract-missing \
  --dry-run

Then real run:
python3 plant_data_bank_scripts/scripts/sync_perenual_discoveries.py \
  --extract-missing
"""

from __future__ import annotations

import argparse
import subprocess
import sys

from project_paths import PATHS


def run(cmd: list[str], dry_run: bool = False) -> None:
    print("")
    print(">>>", " ".join(cmd))

    if not dry_run:
        subprocess.run(cmd, cwd=PATHS.plant_data_bank_scripts, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Perenual snapshots and optionally extract missing plants.")

    parser.add_argument(
        "--extract-missing",
        action="store_true",
        help="Run missing plant extraction after enrichment.",
    )

    parser.add_argument(
        "--export-prolog",
        action="store_true",
        help="Export/update Prolog after missing extraction.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands but do not run extraction commands.",
    )

    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Print resolved project paths.",
    )

    args = parser.parse_args()

    PATHS.ensure_dirs()

    if args.show_paths:
        PATHS.print_summary()

    py = sys.executable

    run(
        [
            py,
            "scripts/enrich_from_perenual_snapshots.py",
        ],
        dry_run=False,
    )

    if args.extract_missing:
        cmd = [
            py,
            "scripts/run_missing_plant_extraction.py",
        ]

        if args.export_prolog:
            cmd.append("--export-prolog")

        if args.dry_run:
            cmd.append("--dry-run")

        run(cmd, dry_run=False)


if __name__ == "__main__":
    main()
