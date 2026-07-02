"""
extract_pfaf_v3.py

Cleaner PFAF extractor for the plant data bank.

What it extracts:
- identity support
- edible parts
- use categories
- medicinal notes
- other uses
- cultivation details
- growth conditions
- life cycle context
- propagation section
- companion planting / biodiversity facts

Usage:
    python scripts/extract_pfaf_v3.py --plants config/plants_seed.json
"""

from __future__ import annotations

import argparse
from urllib.parse import quote_plus

import requests

from common import (
    RAW_DIR,
    ensure_dirs,
    load_plants,
    plant_filename,
    source_snapshot,
    write_json,
)
from source_parse_patch_v3 import (
    clean_text,
    extract_biodiversity_from_pfaf,
    extract_edible_parts_from_section,
    extract_germination_from_propagation,
    extract_growth_from_pfaf,
    extract_life_cycle_from_pfaf,
    extract_use_categories_from_sections,
    get_pfaf_sections,
    is_search_page,
    page_text,
    source_relevance_score,
    strip_noise,
    title_text,
)

PFAF_BASE = "https://pfaf.org"
SOURCE_NAME = "Plants For A Future"


def get_url(url: str) -> requests.Response:
    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "SmartUrbanFarmingResearchBot/0.3",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    response.raise_for_status()
    return response


def build_urls(plant: dict) -> list[str]:
    urls = []

    # This is the most useful PFAF URL.
    if plant.get("scientific_name"):
        urls.append(f"{PFAF_BASE}/user/Plant.aspx?LatinName={quote_plus(plant['scientific_name'])}")

    # Common-name search is only fallback/snapshot.
    if plant.get("common_name"):
        urls.append(f"{PFAF_BASE}/user/DatabaseSearhResult.aspx?SearchFor={quote_plus(plant['common_name'])}")

    return urls


def parse_pfaf_page(html: str, url: str, plant: dict) -> dict:
    raw_text = page_text(html)
    text = strip_noise(raw_text)
    title = title_text(html)

    search_page = is_search_page(text, title)
    relevance = source_relevance_score(text, plant)

    trusted_detail = (not search_page) and relevance >= 0.55

    sections = get_pfaf_sections(text)

    edible_section = sections.get("edible_uses")
    medicinal_section = sections.get("medicinal_uses")
    other_uses_section = sections.get("other_uses")
    cultivation_section = sections.get("cultivation")
    propagation_section = sections.get("propagation")
    physical_section = sections.get("physical_characteristics")
    summary_section = sections.get("summary")
    known_hazards = sections.get("known_hazards")

    if trusted_detail:
        edible_parts = extract_edible_parts_from_section(edible_section)

        use_categories = extract_use_categories_from_sections(
            edible_section=edible_section,
            medicinal_section=medicinal_section,
            other_uses_section=other_uses_section,
            common_name=plant.get("common_name"),
        )

        germination = extract_germination_from_propagation(propagation_section)

        growth = extract_growth_from_pfaf(
            physical_section=physical_section,
            cultivation_section=cultivation_section,
        )

        life_cycle = extract_life_cycle_from_pfaf(
            physical_section=physical_section,
            cultivation_section=cultivation_section,
        )

        biodiversity = extract_biodiversity_from_pfaf(
            other_uses_section=other_uses_section,
            cultivation_section=cultivation_section,
            summary_section=summary_section,
        )
    else:
        edible_parts = []
        use_categories = []
        germination = {
            "propagation_methods": [],
            "propagation_notes": None,
            "germination_days_min": None,
            "germination_days_max": None,
            "sowing_depth_cm": None,
        }
        growth = {
            "sunlight": [],
            "soil_type": [],
            "soil_ph_min": None,
            "soil_ph_max": None,
            "water_need": None,
            "growth_speed": None,
            "soil_notes": None,
            "light_notes": None,
            "water_notes": None,
        }
        life_cycle = {
            "life_cycle": None,
            "botanical_life_cycle": None,
            "crop_life_cycle": None,
            "life_cycle_context": None,
        }
        biodiversity = {
            "companions": [],
            "conflicts": [],
            "repels_pests": [],
            "attracts_beneficial_insects": [],
            "pest_confuser": False,
            "pollinator_support": False,
            "biodiversity_notes": [],
        }

    guessed_fields = {
        "trusted_detail": trusted_detail,
        "relevance_score": relevance,
        "is_search_page": search_page,
        # Classification/use
        "edible_parts": edible_parts,
        "use_categories": use_categories,
        "life_cycle": life_cycle.get("life_cycle"),
        "botanical_life_cycle": life_cycle.get("botanical_life_cycle"),
        "crop_life_cycle": life_cycle.get("crop_life_cycle"),
        "life_cycle_context": life_cycle.get("life_cycle_context"),
        # Growth/care
        "growth": growth,
        # Germination/propagation
        "propagation_methods": germination.get("propagation_methods") or [],
        "propagation_notes": germination.get("propagation_notes"),
        "germination_days_min": germination.get("germination_days_min"),
        "germination_days_max": germination.get("germination_days_max"),
        "sowing_depth_cm": germination.get("sowing_depth_cm"),
        # Notes
        "summary_notes": clean_text(summary_section),
        "edible_uses_notes": clean_text(edible_section),
        "medicinal_notes": clean_text(medicinal_section),
        "other_uses_notes": clean_text(other_uses_section),
        "cultivation_notes": clean_text(cultivation_section),
        "known_hazards": clean_text(known_hazards),
        # Biodiversity / companion planting
        "biodiversity": biodiversity,
    }

    return {
        "title": title,
        "trusted_detail": trusted_detail,
        "is_search_page": search_page,
        "relevance_score": relevance,
        "sections": sections,
        "guessed_fields": guessed_fields,
        "page_text_excerpt": text[:5000],
    }


def extract_one_plant(plant: dict) -> dict:
    snapshots = []
    query = plant.get("scientific_name") or plant.get("common_name") or plant.get("plant_atom")

    for url in build_urls(plant):
        try:
            response = get_url(url)
            parsed = parse_pfaf_page(response.text, response.url, plant)

            status = "trusted_detail" if parsed["trusted_detail"] else "low_confidence_snapshot"

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

    return {
        "plant": plant,
        "source": SOURCE_NAME,
        "snapshots": snapshots,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plants", required=True)
    args = parser.parse_args()

    ensure_dirs()
    plants = load_plants(args.plants)

    for plant in plants:
        data = extract_one_plant(plant)
        out = RAW_DIR / "pfaf" / plant_filename(plant)
        write_json(out, data)
        print(f"[PFAF v3] wrote {out}")


if __name__ == "__main__":
    main()
