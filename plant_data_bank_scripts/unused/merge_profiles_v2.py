"""
Cleaner profile merger.

Key changes:
- Only merges source snapshots with status == trusted_detail for text websites.
- Does not let FPI search pages populate cultivation notes.
- Does not infer broad use categories from whole-page text.
- Keeps missing fields explicit.
"""

from __future__ import annotations

import argparse
from typing import Any

from common import (
    NORMALIZED_DIR,
    RAW_DIR,
    canonical_profile_template,
    ensure_dirs,
    load_plants,
    plant_filename,
    read_json,
    utc_now,
    write_json,
)


def set_field(profile: dict[str, Any], path: str, value: Any, source: str, overwrite: bool = False) -> None:
    if value in (None, "", [], {}):
        return

    parts = path.split(".")
    cursor = profile
    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})

    key = parts[-1]

    if overwrite or cursor.get(key) in (None, "", [], {}):
        cursor[key] = value
        profile.setdefault("field_sources", {})[path] = source


def extend_list_field(profile: dict[str, Any], path: str, values: list[Any], source: str) -> None:
    if not values:
        return

    parts = path.split(".")
    cursor = profile
    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})

    key = parts[-1]
    existing = cursor.get(key) or []
    combined = []

    for item in existing + values:
        if item and item not in combined:
            combined.append(item)

    cursor[key] = combined
    profile.setdefault("field_sources", {})[path] = source


def add_source_metadata(profile: dict[str, Any], raw: dict[str, Any], source_name: str) -> None:
    for snap in raw.get("snapshots") or []:
        parsed = snap.get("parsed") or {}
        guessed = parsed.get("guessed_fields") or {}
        profile["source_metadata"]["sources"].append(
            {
                "source_name": source_name,
                "source_url": snap.get("source_url"),
                "status": snap.get("status"),
                "trusted_detail": parsed.get("trusted_detail"),
                "relevance_score": parsed.get("relevance_score"),
                "fields_provided": [
                    key
                    for key, value in guessed.items()
                    if value not in (None, "", [], {}) and key not in ["trusted_detail", "note", "relevance_score", "is_search_page"]
                ],
                "confidence": 0.80 if snap.get("status") == "trusted_detail" else 0.30,
                "last_verified_at": snap.get("fetched_at"),
            }
        )


def merge_gbif(profile: dict[str, Any], raw: dict[str, Any]) -> None:
    for snap in raw.get("snapshots") or []:
        payload = (snap.get("parsed") or {}).get("payload") or {}
        if not payload or payload.get("matchType") == "NONE":
            continue

        set_field(profile, "identity.scientific_name", payload.get("scientificName"), "GBIF")
        set_field(profile, "identity.genus", payload.get("genus"), "GBIF")
        set_field(profile, "identity.family", payload.get("family"), "GBIF")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v not in (None, "", [], {})]
    return [value]


def merge_perenual(profile: dict[str, Any], raw: dict[str, Any]) -> None:
    detail_payloads = []

    for snap in raw.get("snapshots") or []:
        parsed = snap.get("parsed") or {}
        if parsed.get("endpoint") == "species-details":
            detail_payloads.extend(parsed.get("payload") or [])

    for detail in detail_payloads:
        if not isinstance(detail, dict):
            continue

        set_field(profile, "identity.common_name", detail.get("common_name"), "Perenual")

        sci = detail.get("scientific_name")
        if isinstance(sci, list) and sci:
            set_field(profile, "identity.scientific_name", sci[0], "Perenual")
        elif isinstance(sci, str):
            set_field(profile, "identity.scientific_name", sci, "Perenual")

        set_field(profile, "classification.life_cycle", detail.get("cycle"), "Perenual")
        extend_list_field(profile, "growth.sunlight", _as_list(detail.get("sunlight")), "Perenual")
        set_field(profile, "growth.water_need", detail.get("watering"), "Perenual")
        extend_list_field(profile, "germination.propagation_methods", _as_list(detail.get("propagation")), "Perenual")
        set_field(profile, "growth.growth_speed", detail.get("growth_rate"), "Perenual")


def merge_pfaf(profile: dict[str, Any], raw: dict[str, Any]) -> None:
    for snap in raw.get("snapshots") or []:
        if snap.get("status") != "trusted_detail":
            continue

        guessed = (snap.get("parsed") or {}).get("guessed_fields") or {}

        extend_list_field(profile, "classification.edible_parts", guessed.get("edible_parts") or [], "Plants For A Future")
        extend_list_field(profile, "classification.use_categories", guessed.get("use_categories") or [], "Plants For A Future")
        extend_list_field(profile, "germination.propagation_methods", guessed.get("propagation_methods") or [], "Plants For A Future")

        set_field(profile, "classification.life_cycle", guessed.get("life_cycle"), "Plants For A Future")
        set_field(profile, "germination.propagation_notes", guessed.get("propagation_notes"), "Plants For A Future")
        set_field(profile, "care.cultivation_notes", guessed.get("cultivation_notes"), "Plants For A Future")
        set_field(profile, "care.cautions", guessed.get("known_hazards"), "Plants For A Future")
        set_field(profile, "care.nutrition_notes", guessed.get("medicinal_notes"), "Plants For A Future")

    if profile["classification"]["edible_parts"]:
        set_field(profile, "classification.edible", True, "Plants For A Future")


def merge_fpi(profile: dict[str, Any], raw: dict[str, Any]) -> None:
    """
    FPI is snapshot-only until a source-specific plant-page/PDF parser is added.
    This prevents search-page menu text from becoming cultivation notes.
    """
    for snap in raw.get("snapshots") or []:
        if snap.get("status") != "trusted_detail":
            continue

        # Currently no trusted field mapping for generic FPI pages.
        # Add mapping later only after you parse real FPI detail/PDF records.


def compute_missing_fields(profile: dict[str, Any]) -> None:
    required_paths = [
        "identity.scientific_name",
        "identity.genus",
        "identity.family",
        "classification.edible_parts",
        "classification.life_cycle",
        "growth.sunlight",
        "growth.water_need",
        "growth.soil_notes",
        "germination.propagation_methods",
        "germination.germination_days_min",
        "germination.sowing_depth_cm",
        "pests_and_diseases.known_diseases",
    ]

    missing = []
    for path in required_paths:
        cursor = profile
        ok = True
        for part in path.split("."):
            if not isinstance(cursor, dict) or part not in cursor:
                ok = False
                break
            cursor = cursor[part]
        if not ok or cursor in (None, "", [], {}):
            missing.append(path)

    profile["missing_fields"] = missing


def merge_one(plant: dict[str, Any]) -> dict[str, Any]:
    profile = canonical_profile_template(plant)

    if plant.get("scientific_name"):
        set_field(profile, "identity.scientific_name", plant["scientific_name"], "local_seed", overwrite=True)
    if plant.get("common_name"):
        set_field(profile, "identity.common_name", plant["common_name"], "local_seed", overwrite=True)

    source_plan = [
        ("gbif", "GBIF", merge_gbif),
        ("perenual", "Perenual", merge_perenual),
        ("pfaf", "Plants For A Future", merge_pfaf),
        ("food_plants_international", "Food Plants International", merge_fpi),
    ]

    for folder, source_name, merge_func in source_plan:
        raw_path = RAW_DIR / folder / plant_filename(plant)
        raw = read_json(raw_path, default=None)
        if raw:
            merge_func(profile, raw)
            add_source_metadata(profile, raw, source_name)

    profile["source_metadata"]["last_merged_at"] = utc_now()
    compute_missing_fields(profile)
    return profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plants", required=True)
    args = parser.parse_args()

    ensure_dirs()
    plants = load_plants(args.plants)

    for plant in plants:
        profile = merge_one(plant)
        out = NORMALIZED_DIR / plant_filename(plant)
        write_json(out, profile)
        print(f"[MERGE v2] wrote {out}")


if __name__ == "__main__":
    main()
