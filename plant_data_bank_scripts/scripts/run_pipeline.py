from __future__ import annotations

import argparse
import subprocess
import sys

from project_paths import PATHS


ROOT = PATHS.plant_data_bank_scripts


def run(cmd: list[str]) -> None:
    print("\n>>>", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    PATHS.ensure_dirs()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plants",
        default=str(PATHS.plants_seed),
        help="Plant seed JSON file. Defaults to config/plants_seed.json.",
    )
    parser.add_argument("--include-perenual", action="store_true")
    args = parser.parse_args()

    py = sys.executable

    run([py, "scripts/plant/extract_fpi.py", "--plants", args.plants])
    run([py, "scripts/plant/extract_pfaf.py", "--plants", args.plants])
    run([py, "scripts/plant/enrich_gbif.py", "--plants", args.plants])

    if args.include_perenual:
        run([py, "scripts/plant/enrich_perenual.py", "--plants", args.plants])

    run([py, "scripts/plant/merge_profiles.py", "--plants", args.plants])
    run([py, "scripts/build_indexes.py"])
    run([py, "scripts/validate_data_bank.py"])


if __name__ == "__main__":
    main()
