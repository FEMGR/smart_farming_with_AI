"""
Cleaner PFAF extractor.

Key changes:
- Uses scientific-name page first.
- Labels search pages as low confidence.
- Extracts edible parts only from the Edible Uses section.
- Extracts propagation methods only from the Propagation section.
"""

from __future__ import annotations

import argparse
from urllib.parse import quote_plus

import requests

from common import RAW_DIR, ensure_dirs, load_plants, plant_filename, source_snapshot, write_json
from source_parse_patch import (
    clean_text,
    extract_edible_parts_from_section,
    extract_propagation_methods_from_section,
    extract_use_categories_from_sections,
    is_search_page,
    page_text,
    section_after_heading,
    source_relevance_score,
    strip_noise,
    strongly_detect_life_cycle,
    title_text,
)

PFAF_BASE = "https://pfaf.org"
SOURCE_NAME = "Plants For A Future"


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
        urls.append(f"{PFAF_BASE}/user/Plant.aspx?LatinName={quote_plus(plant['scientific_name'])}")

    # Only use common name search as fallback snapshot, not as trusted detail.
    if plant.get("common_name"):
        urls.append(f"{PFAF_BASE}/user/DatabaseSearhResult.aspx?SearchFor={quote_plus(plant['common_name'])}")

    return urls


def parse(html: str, url: str, plant: dict) -> dict:
    text = strip_noise(page_text(html))
    title = title_text(html)
    search_page = is_search_page(text, title)
    relevance = source_relevance_score(text, plant)

    edible_section = section_after_heading(
        text,
        "Edible Uses",
        stop_headings=["Medicinal Uses", "Other Uses", "Propagation", "Cultivation Details", "Known Hazards", "Plant Habitats"],
    )
    medicinal_section = section_after_heading(
        text,
        "Medicinal Uses",
        stop_headings=["Other Uses", "Propagation", "Cultivation Details", "Known Hazards", "Plant Habitats"],
    )
    propagation_section = section_after_heading(
        text,
        "Propagation",
        stop_headings=["Cultivation Details", "Other Uses", "Known Hazards", "Plant Habitats", "References"],
    )
    cultivation_section = section_after_heading(
        text,
        "Cultivation Details",
        stop_headings=["Propagation", "Other Uses", "Known Hazards", "Plant Habitats", "References"],
    )
    hazard_section = section_after_heading(
        text,
        "Known Hazards",
        stop_headings=["Edible Uses", "Medicinal Uses", "Other Uses", "Propagation", "Cultivation Details"],
    )

    trusted_detail = (not search_page) and relevance >= 0.55

    guessed = {
        "trusted_detail": trusted_detail,
        "relevance_score": relevance,
        "is_search_page": search_page,
        "life_cycle": strongly_detect_life_cycle(text) if trusted_detail else None,
        "edible_parts": extract_edible_parts_from_section(edible_section) if trusted_detail else [],
        "use_categories": (
            extract_use_categories_from_sections(
                edible_section,
                medicinal_section,
                plant.get("common_name"),
            )
            if trusted_detail
            else []
        ),
        "propagation_methods": extract_propagation_methods_from_section(propagation_section) if trusted_detail else [],
        "propagation_notes": clean_text(propagation_section) if trusted_detail else None,
        "cultivation_notes": clean_text(cultivation_section) if trusted_detail else None,
        "known_hazards": clean_text(hazard_section) if trusted_detail else None,
        "edible_uses_notes": clean_text(edible_section) if trusted_detail else None,
        "medicinal_notes": clean_text(medicinal_section) if trusted_detail else None,
    }

    return {
        "title": title,
        "trusted_detail": trusted_detail,
        "is_search_page": search_page,
        "relevance_score": relevance,
        "sections": {
            "edible_uses": edible_section,
            "medicinal_uses": medicinal_section,
            "propagation": propagation_section,
            "cultivation": cultivation_section,
            "known_hazards": hazard_section,
        },
        "guessed_fields": guessed,
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

        out = RAW_DIR / "pfaf" / plant_filename(plant)
        write_json(out, {"plant": plant, "source": SOURCE_NAME, "snapshots": snapshots})
        print(f"[PFAF v2] wrote {out}")


if __name__ == "__main__":
    main()
