from __future__ import annotations
import argparse
import sys
from pathlib import Path
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from common import (
    RAW_DIR,
    clean_text,
    ensure_dirs,
    extract_sentences_containing,
    guess_edible_parts,
    guess_life_cycle,
    guess_propagation_methods,
    guess_use_categories,
    html_title,
    http_get,
    load_plants,
    plant_filename,
    source_snapshot,
    soup_text,
    write_json,
)  # noqa: E402
from project_paths import PATHS  # noqa: E402


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


FPI_SOURCE_NAME = "Food Plants International"
FPI_BASE = "https://foodplantsinternational.com"


def urls(plant):
    qs = []
    for k in ["scientific_name", "common_name", "plant_atom"]:
        v = plant.get(k)
        if v and v not in qs:
            qs.append(v)
    return [f"{FPI_BASE}/?s={quote_plus(q)}" for q in qs]


def links(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        txt = clean_text(a.get_text(" "))
        href = a["href"]
        if txt and href:
            out.append({"text": txt, "href": href})
    return out[:80]


def parse(html, url):
    text = soup_text(html)
    return {
        "title": html_title(html),
        "page_text": text[:25000],
        "links": links(html),
        "guessed_fields": {
            "life_cycle": guess_life_cycle(text),
            "edible_parts": guess_edible_parts(text),
            "use_categories": guess_use_categories(text),
            "propagation_methods": guess_propagation_methods(text),
            "propagation_notes": extract_sentences_containing(text, ["propagat", "seed", "cutting", "sow", "germin"]),
            "cultivation_notes": extract_sentences_containing(text, ["cultivat", "grow", "soil", "sun", "shade", "water"]),
            "nutrition_notes": extract_sentences_containing(text, ["nutrition", "protein", "vitamin", "mineral", "food value"]),
            "pest_disease_notes": extract_sentences_containing(text, ["pest", "disease", "fungus", "virus", "bacterial", "rot"]),
            "cautions": extract_sentences_containing(text, ["poison", "toxic", "caution", "warning", "hazard"]),
        },
    }


def extract_one(plant):
    snapshots = []
    q = plant.get("scientific_name") or plant.get("common_name") or plant.get("plant_atom")
    for u in urls(plant):
        try:
            r = http_get(u, delay_seconds=2.0)
            snapshots.append(source_snapshot(FPI_SOURCE_NAME, r.url, q, "ok", r.text, parse(r.text, r.url)))
        except Exception as e:
            snapshots.append(source_snapshot(FPI_SOURCE_NAME, u, q, f"error: {e}", "", {}))
    return {"plant": plant, "source": FPI_SOURCE_NAME, "snapshots": snapshots}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plants", default=str(PATHS.plants_seed), help="Path to plant seed JSON file.")
    args = ap.parse_args()
    PATHS.ensure_dirs()
    ensure_dirs()
    for plant in load_plants(Path(args.plants)):
        out = RAW_DIR / "food_plants_international" / plant_filename(plant)
        write_json(out, extract_one(plant))
        print("[FPI] wrote", out)


if __name__ == "__main__":
    main()
