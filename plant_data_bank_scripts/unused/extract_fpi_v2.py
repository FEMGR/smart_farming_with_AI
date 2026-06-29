"""
Cleaner FPI extractor.

FPI search pages are not treated as trusted plant detail pages.
This script stores FPI snapshots for later manual/source-specific parsing,
but does not mark generic search pages as field providers.
"""

from __future__ import annotations

import argparse
from urllib.parse import quote_plus

import requests

from common import RAW_DIR, ensure_dirs, load_plants, plant_filename, source_snapshot, write_json
from source_parse_patch import is_search_page, page_text, source_relevance_score, title_text


SOURCE_NAME = "Food Plants International"
FPI_BASE = "https://foodplantsinternational.com"


def get_url(url: str) -> requests.Response:
    response = requests.get(
        url,
        timeout=25,
        headers={"User-Agent": "SmartUrbanFarmingResearchBot/0.2"},
    )
    response.raise_for_status()
    return response


def build_urls(plant: dict) -> list[str]:
    urls = []
    if plant.get("scientific_name"):
        urls.append(f"{FPI_BASE}/?s={quote_plus(plant['scientific_name'])}")
    if plant.get("common_name"):
        urls.append(f"{FPI_BASE}/?s={quote_plus(plant['common_name'])}")
    return urls


def parse(html: str, url: str, plant: dict) -> dict:
    text = page_text(html)
    title = title_text(html)
    search_page = is_search_page(text, title)
    relevance = source_relevance_score(text, plant)

    # Most FPI public queries return search pages or PDFs/books. Do not parse as facts here.
    trusted_detail = (not search_page) and relevance >= 0.70

    return {
        "title": title,
        "trusted_detail": trusted_detail,
        "is_search_page": search_page,
        "relevance_score": relevance,
        "guessed_fields": {"trusted_detail": trusted_detail, "note": "FPI snapshot stored. Use manual/PDF/source-specific parser before merging facts."},
        "page_text_excerpt": text[:4000],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plants", required=True)
    args = parser.parse_args()

    ensure_dirs()
    plants = load_plants(args.plants)

    for plant in plants:
        snapshots = []
        query = plant.get("scientific_name") or plant.get("common_name") or plant.get("plant_atom")

        for url in build_urls(plant):
            try:
                response = get_url(url)
                parsed = parse(response.text, response.url, plant)
                status = "trusted_detail" if parsed["trusted_detail"] else "snapshot_only"
                snapshots.append(
                    source_snapshot(
                        source_name=SOURCE_NAME,
                        source_url=response.url,
                        query=query,
                        status=status,
                        raw_text=response.text,
                        parsed=parsed,
                    )
                )
            except Exception as exc:
                snapshots.append(
                    source_snapshot(
                        source_name=SOURCE_NAME,
                        source_url=url,
                        query=query,
                        status=f"error: {exc}",
                        parsed={},
                    )
                )

        out = RAW_DIR / "food_plants_international" / plant_filename(plant)
        write_json(out, {"plant": plant, "source": SOURCE_NAME, "snapshots": snapshots})
        print(f"[FPI v2] wrote {out}")


if __name__ == "__main__":
    main()
