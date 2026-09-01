#!/usr/bin/env python3
"""
sync_perenual_discoveries.py

Convenience launcher:
1. Enrich data bank from Perenual snapshots.
2. Dry-run or run missing plant extraction.

Run:
python3 data_bank/scripts/plant/sync_perenual_discoveries.py --show-paths

Or with missing extraction:
python3 data_bank/scripts/plant/sync_perenual_discoveries.py \
  --extract-missing \
  --dry-run

Then real run:
python3 data_bank/scripts/plant/sync_perenual_discoveries.py \
  --extract-missing
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_paths import PATHS  # noqa: E402


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
        "--dry-run",
        action="store_true",
        help="Print commands but do not run extraction commands.",
    )

    parser.add_argument(
        "--update-prolog",
        action="store_true",
        help="Run Prolog update after missing plant extraction.",
    )

    parser.add_argument(
        "--apply-prolog",
        action="store_true",
        help="Apply Prolog updates instead of previewing them.",
    )

    parser.add_argument(
        "--reorder-prolog",
        action="store_true",
        help="Run Prolog fact reorder after updating Prolog.",
    )

    parser.add_argument(
        "--apply-reorder",
        action="store_true",
        help="Apply Prolog fact reorder instead of previewing it.",
    )

    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Print resolved project paths.",
    )

    args = parser.parse_args()

    if args.apply_prolog:
        args.update_prolog = True

    if args.apply_reorder:
        args.reorder_prolog = True

    PATHS.ensure_dirs()

    if args.show_paths:
        PATHS.print_summary()

    py = sys.executable

    run(
        [
            py,
            "scripts/plant/enrich_from_perenual_snapshots.py",
        ],
        dry_run=False,
    )

    if args.extract_missing:
        cmd = [
            py,
            "scripts/plant/run_missing_plant_extraction.py",
        ]

        if args.update_prolog:
            cmd.append("--update-prolog")

        if args.apply_prolog:
            cmd.append("--apply-prolog")

        if args.reorder_prolog:
            cmd.append("--reorder-prolog")

        if args.apply_reorder:
            cmd.append("--apply-reorder")

        if args.dry_run:
            cmd.append("--dry-run")

        run(cmd, dry_run=False)


if __name__ == "__main__":
    main()
