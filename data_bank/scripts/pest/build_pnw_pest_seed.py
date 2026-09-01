#!/usr/bin/env python3
"""
build_pnw_pest_seed.py

Build pest seed data from PNW:
Common Pests of Vegetable Crops.

This script reads the common vegetable pest page/sidebar and extracts
all pest detail links such as:

- Vegetable crop pests-Aphid
- Vegetable crop pests-Armyworm
- Vegetable crop pests-Cabbage maggot

Output:
- config/pnw_seed_pest.json
- data_bank/raw_sources/pnw/pnw_seed_pest.json
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://pnwhandbooks.org"
COMMON_PESTS_URL = "https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable"

SOURCE_NAME = "PNW Insect Management Handbook"
SOURCE_SECTION = "Common Pests of Vegetable Crops"
DATA_ORIGIN = "pnw_common_vegetable_pest_seed"


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


def clean_pest_title(title: str) -> str:
    """
    Convert:
        Vegetable crop pests-Aphid
    into:
        Aphid
    """
    title = normalize_text(title)

    title = re.sub(
        r"^vegetable\s+crop\s+pests\s*[-:]\s*",
        "",
        title,
        flags=re.IGNORECASE,
    )

    return normalize_text(title)


def pest_atom_from_title(title: str) -> str:
    return to_atom(clean_pest_title(title))


def fetch_html(url: str, sleep_seconds: float = 1.0, timeout: int = 30) -> str:
    headers = {"User-Agent": ("SmartFarmingDataBot/1.0 " "(educational research crawler; polite single-page seed request)")}

    print(f"[INFO] Fetching: {url}")
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    time.sleep(sleep_seconds)
    return response.text


def find_common_pest_links(soup, source_url):
    links = []

    heading = soup.find("h3", string=lambda s: s and "vegetable crop pests" in s.lower())

    if not heading:
        print("[WARN] Vegetable crop pests section not found")
        return []

    pest_list = heading.find_next("ul")

    if not pest_list:
        print("[WARN] Pest list not found")
        return []

    for anchor in soup.select("a[href]"):
        href = anchor.get("href")
        text = normalize_text(anchor.get_text(" ", strip=True))

        if not href:
            continue

        if "/insect/vegetable/vegetable-pests/common-vegetable/" not in href:
            continue

        # skip index page
        if href.rstrip("/").endswith("common-vegetable"):
            continue

        full_url = urljoin(BASE_URL, href)

        pest_name = text.strip()

        pest_atom = to_atom(href.rstrip("/").split("/")[-1].replace("vegetable-crop-", ""))

        links.append(
            {
                "pest_atom": pest_atom,
                "pest_name": pest_name,
                "pest_type": classify_pest_type(pest_atom, pest_name),
                "source_url": full_url,
                "source_name": SOURCE_NAME,
                "source_section": SOURCE_SECTION,
                "source_index_url": source_url,
                "data_origin": DATA_ORIGIN,
                "confidence": 0.95,
                "host_plants": [],
            }
        )

    return dedupe_links(links)


def classify_pest_type(pest_atom: str, pest_name: str) -> str:
    text = f"{pest_atom} {pest_name}".lower()

    if "slug" in text:
        return "mollusk"
    if "mite" in text:
        return "mite"
    if "symphylan" in text:
        return "symphylan"
    if "springtail" in text or "collembola" in text:
        return "springtail"

    return "insect"


def dedupe_links(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    unique = []

    for item in items:
        key = item["pest_atom"]

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    return sorted(unique, key=lambda item: item["pest_atom"])


def write_seed_file(seeds: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "source_name": SOURCE_NAME,
        "source_section": SOURCE_SECTION,
        "source_index_url": COMMON_PESTS_URL,
        "count": len(seeds),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pests": seeds,
    }

    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"[OK] Wrote: {output_path}")
    print(f"[OK] Pest seed count: {len(seeds)}")


def print_summary(seeds: List[Dict[str, Any]]) -> None:
    print("")
    print("========== PNW COMMON PEST SEED SUMMARY ==========")
    print(f"Pests: {len(seeds)}")
    print("")
    for seed in seeds:
        print(f"  - {seed['pest_atom']} -> {seed['pest_name']}")
    print("==================================================")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=COMMON_PESTS_URL)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument(
        "--output-config",
        default="config/pnw_seed_pest.json",
    )
    parser.add_argument(
        "--output-raw",
        default="data_bank/raw_sources/pnw/pnw_seed_pest.json",
    )

    args = parser.parse_args()

    html = fetch_html(args.url, sleep_seconds=args.sleep)

    Path("debug_common_vegetable.html").write_text(html, encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    seeds = find_common_pest_links(soup, args.url)

    write_seed_file(seeds, Path(args.output_config))
    write_seed_file(seeds, Path(args.output_raw))

    print_summary(seeds)


if __name__ == "__main__":
    main()
