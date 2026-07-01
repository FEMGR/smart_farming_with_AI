#!/usr/bin/env python3
"""
build_pnw_pest_seed.py

Builds a pest seed file from the PNW Insect Management Handbook:
Vegetable Crops -> Hosts and Pests of Vegetable Crops.

Input:
- PNW host-pest index page

Outputs:
- config/pnw_seed_pest_ver01.json
- data_bank/raw_sources/pnw/pnw_seed_pest_ver01.json

Purpose:
- Discover all vegetable pest pages.
- Normalize pest names into pest atoms.
- Normalize crop headings into plant atoms.
- Group all host plants under each pest.
- Preserve source URLs for verification and later enrichment.

Run from:
    plant_data_bank_scripts/

Example:
    python3 scripts/pest/build_pnw_pest_seed.py
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://pnwhandbooks.org"
HOSTS_PESTS_URL = "https://pnwhandbooks.org/insect/vegetable/vegetable-pests/hosts-pests"

SOURCE_NAME = "PNW Insect Management Handbook"
SOURCE_SECTION = "Hosts and Pests of Vegetable Crops"
DATA_ORIGIN = "pnw_vegetable_pest_seed"


# ------------------------------------------------------------
# Crop heading expansion
# ------------------------------------------------------------
# PNW has grouped crop headings. Your KB usually wants individual
# plant atoms. This map controls the normalization.
# ------------------------------------------------------------

CROP_HEADING_EXPANSIONS: Dict[str, List[str]] = {
    "artichoke (globe artichoke)": ["artichoke"],
    "asparagus": ["asparagus"],
    "bean, dry": ["bean"],
    "bean, lima": ["lima_bean"],
    "bean, snap": ["bean"],
    "beet, table": ["beet"],
    "broccoli, brussels sprout, cabbage, cauliflower": [
        "broccoli",
        "brussels_sprout",
        "cabbage",
        "cauliflower",
    ],
    "cantaloupe-see melon": ["cantaloupe"],
    "carrot": ["carrot"],
    "celery": ["celery"],
    "chard, swiss": ["swiss_chard"],
    "collard and kale": ["collard", "kale"],
    "corn, sweet": ["sweet_corn", "corn"],
    "cucumber": ["cucumber"],
    "dill": ["dill"],
    "eggplant": ["eggplant"],
    "endive (escarole)": ["endive", "escarole"],
    "garlic": ["garlic"],
    "horseradish": ["horseradish"],
    "kohlrabi": ["kohlrabi"],
    "leek and shallot": ["leek", "shallot"],
    "lentil": ["lentil"],
    "lettuce": ["lettuce"],
    "melon (cantaloupe, muskmelon, and watermelon)": [
        "melon",
        "cantaloupe",
        "muskmelon",
        "watermelon",
    ],
    "mushroom": ["mushroom"],
    "muskmelon-see melon": ["muskmelon"],
    "mustard greens": ["mustard_green"],
    "onion": ["onion"],
    "parsley": ["parsley"],
    "parsnip": ["parsnip"],
    "pea, green and dry": ["pea"],
    "pepper": ["pepper", "bell_pepper", "chili_pepper"],
    "potato, irish": ["potato"],
    "potato, sweet": ["sweet_potato"],
    "pumpkin and squash": ["pumpkin", "squash"],
    "radish": ["radish"],
    "rhubarb": ["rhubarb"],
    "salsify": ["salsify"],
    "spinach": ["spinach"],
    "tomato": ["tomato"],
    "turnip (roots and tops) and rutabaga": ["turnip", "rutabaga"],
    "watercress": ["watercress"],
    "watermelon-see melon": ["watermelon"],
}


# These headings are redirects or empty sections in the PNW index.
SKIP_EMPTY_HEADINGS = {
    "cantaloupe-see melon",
    "mushroom",
    "muskmelon-see melon",
    "potato, irish",
    "watermelon-see melon",
}


# ------------------------------------------------------------
# Pest expansion
# ------------------------------------------------------------
# Some PNW pest labels are combined, e.g. "Armyworm and cutworm".
# For Prolog, it is usually better to split them into individual pests_ver01.
# The original display name and URL are still preserved.
# ------------------------------------------------------------

PEST_NAME_EXPANSIONS: Dict[str, List[str]] = {
    "armyworm and cutworm": ["armyworm", "cutworm"],
    "cutworm and armyworm": ["cutworm", "armyworm"],
    "armyworm and looper": ["armyworm", "looper"],
    "armyworm, cutworm, and looper": ["armyworm", "cutworm", "looper"],
    "stink bug and plant bug": ["stink_bug", "plant_bug"],
    "onion maggot and seedcorn maggot": ["onion_maggot", "seedcorn_maggot"],
    "tomato fruitworm (corn earworm)": ["tomato_fruitworm", "corn_earworm"],
    "four-spotted spider mite": ["spider_mite"],
    "painted lady or thistle butterfly": [
        "painted_lady_butterfly",
        "thistle_butterfly",
    ],
    "collembola (springtail)": ["springtail", "collembola"],
}


def normalize_text(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def to_atom(value: str) -> str:
    value = normalize_text(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def expand_crop_heading(crop_heading: str) -> List[str]:
    key = normalize_text(crop_heading).lower()
    if key in CROP_HEADING_EXPANSIONS:
        return CROP_HEADING_EXPANSIONS[key]
    return [to_atom(key)]


def expand_pest_name(pest_name: str) -> List[str]:
    key = normalize_text(pest_name).lower()
    if key in PEST_NAME_EXPANSIONS:
        return PEST_NAME_EXPANSIONS[key]
    return [to_atom(key)]


def fetch_html(url: str, sleep_seconds: float = 1.0, timeout: int = 30) -> str:
    headers = {"User-Agent": ("SmartFarmingDataBot/1.0 " "(educational research crawler; respectful single-page request)")}

    print(f"[INFO] Fetching {url}")
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    time.sleep(sleep_seconds)
    return response.text


def get_latest_revision(soup: BeautifulSoup) -> Optional[str]:
    text = soup.get_text("\n", strip=True)
    match = re.search(r"Latest revision:\s*([A-Za-z]+\s+\d{4})", text)
    return match.group(1) if match else None


def parse_seed(html: str, source_url: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find("h1")
    if not h1:
        raise RuntimeError("Could not find H1 on PNW host-pest page")

    latest_revision = get_latest_revision(soup)
    extracted_at = datetime.now(timezone.utc).isoformat()

    pest_map: Dict[str, Dict[str, Any]] = {}

    current_crop_heading: Optional[str] = None

    for node in h1.find_all_next():
        if not isinstance(node, Tag):
            continue

        if node.name == "h2":
            h2_text = normalize_text(node.get_text(" ", strip=True))
            if h2_text == "Vegetable Crops":
                break

        if node.name == "h3":
            current_crop_heading = normalize_text(node.get_text(" ", strip=True))
            continue

        if node.name != "ul" or not current_crop_heading:
            continue

        crop_key = current_crop_heading.lower()
        if crop_key in SKIP_EMPTY_HEADINGS:
            continue

        host_plants = expand_crop_heading(current_crop_heading)

        for li in node.find_all("li", recursive=False):
            pest_name = normalize_text(li.get_text(" ", strip=True))
            if not pest_name:
                continue

            link = li.find("a")
            source_page_url = None
            if link and link.get("href"):
                source_page_url = urljoin(BASE_URL, link["href"])

            pest_atoms = expand_pest_name(pest_name)

            for pest_atom in pest_atoms:
                if not pest_atom:
                    continue

                if pest_atom not in pest_map:
                    pest_map[pest_atom] = {
                        "pest_atom": pest_atom,
                        "pest_name": pest_name,
                        "pest_type": "insect",
                        "host_plants": [],
                        "source_pages": [],
                        "source_name": SOURCE_NAME,
                        "source_section": SOURCE_SECTION,
                        "source_index_url": source_url,
                        "latest_revision": latest_revision,
                        "data_origin": DATA_ORIGIN,
                        "confidence": 0.9,
                        "extracted_at": extracted_at,
                    }

                entry = pest_map[pest_atom]

                for plant_atom in host_plants:
                    if plant_atom not in entry["host_plants"]:
                        entry["host_plants"].append(plant_atom)

                source_page = {
                    "crop_heading": current_crop_heading,
                    "pest_name_on_page": pest_name,
                    "url": source_page_url,
                }

                if source_page not in entry["source_pages"]:
                    entry["source_pages"].append(source_page)

    seeds = list(pest_map.values())

    for seed in seeds:
        seed["host_plants"] = sorted(seed["host_plants"])
        seed["source_pages"] = sorted(
            seed["source_pages"],
            key=lambda x: (
                x.get("crop_heading") or "",
                x.get("pest_name_on_page") or "",
                x.get("url") or "",
            ),
        )

    return sorted(seeds, key=lambda item: item["pest_atom"])


def write_seed_file(seeds: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "source_name": SOURCE_NAME,
        "source_section": SOURCE_SECTION,
        "source_index_url": HOSTS_PESTS_URL,
        "count": len(seeds),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pests_ver01": seeds,
    }

    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"[OK] Wrote {output_path}")
    print(f"[OK] Pest seed count: {len(seeds)}")


def print_summary(seeds: List[Dict[str, Any]]) -> None:
    host_count = len({host for seed in seeds for host in seed["host_plants"]})
    source_page_count = sum(len(seed["source_pages"]) for seed in seeds)

    print("")
    print("========== PNW PEST SEED SUMMARY ==========")
    print(f"Pests:        {len(seeds)}")
    print(f"Host plants:  {host_count}")
    print(f"Source pages: {source_page_count}")
    print("")
    print("Sample pests_ver01:")
    for seed in seeds[:20]:
        print(f"  - {seed['pest_atom']} ({len(seed['host_plants'])} hosts)")
    print("===========================================")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=HOSTS_PESTS_URL)
    parser.add_argument(
        "--output-config",
        default="config/pnw_seed_pest_ver01.json",
    )
    parser.add_argument(
        "--output-raw",
        default="data_bank/raw_sources/pnw/pnw_seed_pest_ver01.json",
    )
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    html = fetch_html(args.url, sleep_seconds=args.sleep)
    seeds = parse_seed(html, args.url)

    write_seed_file(seeds, Path(args.output_config))
    write_seed_file(seeds, Path(args.output_raw))

    print_summary(seeds)


if __name__ == "__main__":
    main()
