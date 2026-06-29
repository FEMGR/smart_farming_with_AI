"""
extract_pfaf_v4.py

ID-based PFAF extractor.

Major fixes:
1. Uses exact PFAF page fields by HTML ID.
2. Does not use generic names like "Mentha spp." as trusted detail pages.
3. Does not merge common-name search pages as facts.
4. Prevents section bleeding:
   - tomato edible parts should become fruit/oil/seed, not leaf/root/flower.
5. Extracts companion planting from PFAF Other Uses.
"""

from __future__ import annotations

import argparse
from pathlib import Path
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
from project_paths import PATHS
from source_parse_patch import (
    clean_text,
    extract_identity_from_pfaf_sections,
    extract_biodiversity_from_pfaf,
    extract_edible_parts_from_pfaf,
    extract_germination_from_propagation,
    extract_growth_from_pfaf,
    extract_life_cycle_from_pfaf,
    extract_pfaf_sections_from_html,
    extract_use_categories_from_pfaf,
    is_generic_scientific_name,
    is_real_pfaf_plant_page,
    is_search_page,
    page_text,
    source_relevance_score,
    title_text,
)


PFAF_BASE = "https://pfaf.org"
SOURCE_NAME = "Plants For A Future"


def get_url(url: str) -> requests.Response:
    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "SmartUrbanFarmingResearchBot/0.4",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    response.raise_for_status()
    return response


def build_urls(plant: dict) -> list[dict[str, str]]:
    """
    Prefer exact scientific name.

    Common name search is snapshot only.
    Generic names like Mentha spp. are NOT trusted PFAF plant targets.
    """
    urls: list[dict[str, str]] = []

    scientific_name = plant.get("scientific_name")
    common_name = plant.get("common_name")

    if scientific_name and not is_generic_scientific_name(scientific_name):
        urls.append(
            {
                "url": f"{PFAF_BASE}/user/Plant.aspx?LatinName={quote_plus(scientific_name)}",
                "lookup_type": "scientific_exact",
            }
        )

    # Optional source-specific override, useful for generic records.
    # Example:
    # {
    #   "plant_atom": "mint",
    #   "common_name": "Mint",
    #   "scientific_name": "Mentha spp.",
    #   "pfaf_latin_name": "Mentha spicata"
    # }
    pfaf_latin_name = plant.get("pfaf_latin_name")

    if pfaf_latin_name:
        urls.append(
            {
                "url": f"{PFAF_BASE}/user/Plant.aspx?LatinName={quote_plus(pfaf_latin_name)}",
                "lookup_type": "pfaf_override",
            }
        )

    # Common name search only for trace/snapshot, not trusted facts.
    if common_name:
        urls.append(
            {
                "url": f"{PFAF_BASE}/user/DatabaseSearhResult.aspx?SearchFor={quote_plus(common_name)}",
                "lookup_type": "common_search_snapshot",
            }
        )

    return urls


def parse_pfaf_page(html: str, url: str, plant: dict, lookup_type: str) -> dict:
    raw_text = page_text(html)
    title = title_text(html)
    search_page = is_search_page(raw_text, title)
    relevance = source_relevance_score(raw_text, plant)

    sections = extract_pfaf_sections_from_html(html)
    real_plant_page = is_real_pfaf_plant_page(sections)

    identity = extract_identity_from_pfaf_sections(
        sections=sections,
        fallback_common_name=plant.get("common_name"),
        fallback_scientific_name=plant.get("scientific_name"),
    )

    trusted_detail = real_plant_page and not search_page and lookup_type in {"scientific_exact", "pfaf_override"} and relevance >= 0.55

    summary_section = sections.get("summary")
    physical_section = sections.get("physical_characteristics")
    edible_section = sections.get("edible_uses")
    medicinal_section = sections.get("medicinal_uses")
    other_uses_section = sections.get("other_uses")
    cultivation_section = sections.get("cultivation")
    propagation_section = sections.get("propagation")
    known_hazards = sections.get("known_hazards")

    if trusted_detail:
        edible_parts = extract_edible_parts_from_pfaf(edible_section)

        use_categories = extract_use_categories_from_pfaf(
            edible_section=edible_section,
            medicinal_section=medicinal_section,
            other_uses_section=other_uses_section,
            common_name=plant.get("common_name"),
        )

        growth = extract_growth_from_pfaf(
            physical_section=physical_section,
            cultivation_section=cultivation_section,
        )

        life_cycle = extract_life_cycle_from_pfaf(
            physical_section=physical_section,
            cultivation_section=cultivation_section,
            summary_section=summary_section,
        )

        germination = extract_germination_from_propagation(propagation_section)

        biodiversity = extract_biodiversity_from_pfaf(
            other_uses_section=other_uses_section,
            cultivation_section=cultivation_section,
            summary_section=summary_section,
            physical_section=physical_section,
        )
    else:
        edible_parts = []
        use_categories = []
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
            "temperature_notes": None,
            "rainfall_notes": None,
        }
        life_cycle = {
            "life_cycle": None,
            "botanical_life_cycle": None,
            "crop_life_cycle": None,
            "life_cycle_context": None,
        }
        germination = {
            "propagation_methods": [],
            "propagation_notes": None,
            "germination_days_min": None,
            "germination_days_max": None,
            "sowing_depth_cm": None,
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
        "lookup_type": lookup_type,
        "relevance_score": relevance,
        "is_search_page": search_page,
        "real_plant_page": real_plant_page,
        # Clean parsed identity
        "identity": identity,
        # PFAF identity hints
        "pfaf_display_latin_name": sections.get("display_latin_name"),
        "pfaf_common_name": sections.get("common_name"),
        "pfaf_family": sections.get("family"),
        "pfaf_synonyms": sections.get("synonyms"),
        "pfaf_other_names": sections.get("other_names"),
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
        # Biodiversity
        "biodiversity": biodiversity,
    }

    return {
        "title": title,
        "trusted_detail": trusted_detail,
        "lookup_type": lookup_type,
        "is_search_page": search_page,
        "real_plant_page": real_plant_page,
        "relevance_score": relevance,
        "sections": sections,
        "guessed_fields": guessed_fields,
        "page_text_excerpt": raw_text[:3000],
    }


def extract_one_plant(plant: dict) -> dict:
    snapshots = []

    query = plant.get("pfaf_latin_name") or plant.get("scientific_name") or plant.get("common_name") or plant.get("plant_atom")

    urls = build_urls(plant)

    if not urls:
        snapshots.append(
            source_snapshot(
                source_name=SOURCE_NAME,
                source_url="",
                query=query,
                status="skipped_no_valid_pfaf_query",
                parsed={"reason": ("No exact scientific name or pfaf_latin_name provided. " "Generic names like 'Mentha spp.' are skipped.")},
            )
        )

    for item in urls:
        url = item["url"]
        lookup_type = item["lookup_type"]

        try:
            response = get_url(url)
            parsed = parse_pfaf_page(
                html=response.text,
                url=response.url,
                plant=plant,
                lookup_type=lookup_type,
            )

            if parsed["trusted_detail"]:
                status = "trusted_detail"
            elif parsed["real_plant_page"]:
                status = "plant_page_low_confidence"
            else:
                status = "snapshot_only"

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


def has_trusted_or_useful_snapshot(data: dict) -> bool:
    for snap in data.get("snapshots") or []:
        status = str(snap.get("status") or "")

        if status == "trusted_detail":
            return True

        parsed = snap.get("parsed") or {}
        if parsed.get("trusted_detail") is True:
            return True

    return False


def is_error_only_snapshot(data: dict) -> bool:
    snapshots = data.get("snapshots") or []

    if not snapshots:
        return True

    for snap in snapshots:
        status = str(snap.get("status") or "")

        if not status.startswith("error"):
            return False

    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plants",
        default=str(PATHS.plants_seed),
        help="Path to plant seed JSON file.",
    )
    parser.add_argument(
        "--overwrite-errors",
        action="store_true",
        help="Allow error-only fetches to overwrite existing raw files.",
    )
    args = parser.parse_args()

    PATHS.ensure_dirs()
    ensure_dirs()
    plants = load_plants(Path(args.plants))

    for plant in plants:
        data = extract_one_plant(plant)
        out = RAW_DIR / "pfaf" / plant_filename(plant)

        existing = None
        if out.exists():
            try:
                import json

                existing = json.loads(out.read_text(encoding="utf-8"))
            except Exception:
                existing = None

        new_is_error_only = is_error_only_snapshot(data)
        existing_is_useful = bool(existing and has_trusted_or_useful_snapshot(existing))

        if new_is_error_only and existing_is_useful and not args.overwrite_errors:
            print(f"[PFAF v4] skipped overwrite for {plant.get('plant_atom')} " f"because new fetch failed but existing raw file is useful: {out}")
            continue

        write_json(out, data)
        print(f"[PFAF v4] wrote {out}")


if __name__ == "__main__":
    main()
