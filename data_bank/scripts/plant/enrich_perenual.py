from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import RAW_DIR, ensure_dirs, load_plants, plant_filename, source_snapshot, write_json  # noqa: E402
from project_paths import PATHS  # noqa: E402

load_dotenv()
PERENUAL_API_KEY = os.getenv("PERENUAL_API_KEY", "")
PERENUAL_BASE_URL = os.getenv("PERENUAL_BASE_URL", "https://perenual.com/api/v2")


def search(q):
    if not PERENUAL_API_KEY:
        return {"error": "missing PERENUAL_API_KEY"}
    r = requests.get(f"{PERENUAL_BASE_URL}/species-list", params={"key": PERENUAL_API_KEY, "q": q}, timeout=25)
    r.raise_for_status()
    return r.json()


def detail(i):
    if not PERENUAL_API_KEY:
        return {"error": "missing PERENUAL_API_KEY"}
    r = requests.get(f"{PERENUAL_BASE_URL}/species/details/{i}", params={"key": PERENUAL_API_KEY}, timeout=25)
    r.raise_for_status()
    return r.json()


def one(plant, delay):
    q = plant.get("scientific_name") or plant.get("common_name") or plant.get("plant_atom")
    snaps = []
    try:
        time.sleep(delay)
        s = search(q)
        snaps.append(source_snapshot("Perenual", f"{PERENUAL_BASE_URL}/species-list", q, "ok", parsed={"endpoint": "species-list", "payload": s}))
        details = []
        for item in (s.get("data") or [])[:3]:
            sid = item.get("id")
            if sid:
                time.sleep(delay)
                details.append(detail(sid))
        snaps.append(
            source_snapshot("Perenual", f"{PERENUAL_BASE_URL}/species/details/{{id}}", q, "ok", parsed={"endpoint": "species-details", "payload": details})
        )
    except Exception as e:
        snaps.append(source_snapshot("Perenual", PERENUAL_BASE_URL, q, f"error: {e}", parsed={}))
    return {"plant": plant, "source": "Perenual", "snapshots": snaps}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plants", default=str(PATHS.plants_seed), help="Path to plant seed JSON file.")
    ap.add_argument("--delay", type=float, default=6.0)
    args = ap.parse_args()
    PATHS.ensure_dirs()
    ensure_dirs()
    for plant in load_plants(Path(args.plants)):
        out = RAW_DIR / "perenual" / plant_filename(plant)
        write_json(out, one(plant, args.delay))
        print("[PERENUAL] wrote", out)


if __name__ == "__main__":
    main()
