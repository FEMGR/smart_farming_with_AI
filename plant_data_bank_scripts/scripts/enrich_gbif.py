from __future__ import annotations

import argparse
from pathlib import Path

import requests

from common import RAW_DIR, ensure_dirs, load_plants, plant_filename, source_snapshot, write_json
from project_paths import PATHS

GBIF_BASE_URL = "https://api.gbif.org/v1"


def match(name):
    r = requests.get(f"{GBIF_BASE_URL}/species/match", params={"name": name, "kingdom": "Plantae", "verbose": "true"}, timeout=25)
    r.raise_for_status()
    return r.json()


def one(plant):
    q = plant.get("scientific_name") or plant.get("common_name") or plant.get("plant_atom")
    snaps = []
    try:
        snaps.append(source_snapshot("GBIF", f"{GBIF_BASE_URL}/species/match", q, "ok", parsed={"endpoint": "species/match", "payload": match(q)}))
    except Exception as e:
        snaps.append(source_snapshot("GBIF", f"{GBIF_BASE_URL}/species/match", q, f"error: {e}", parsed={}))
    return {"plant": plant, "source": "GBIF", "snapshots": snaps}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plants", default=str(PATHS.plants_seed), help="Path to plant seed JSON file.")
    args = ap.parse_args()
    PATHS.ensure_dirs()
    ensure_dirs()
    for plant in load_plants(Path(args.plants)):
        out = RAW_DIR / "gbif" / plant_filename(plant)
        write_json(out, one(plant))
        print("[GBIF] wrote", out)


if __name__ == "__main__":
    main()
