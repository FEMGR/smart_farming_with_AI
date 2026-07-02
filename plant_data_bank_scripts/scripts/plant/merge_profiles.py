"""
merge_profiles_v3.py

Merge raw source snapshots into centralized normalized plant JSON profiles.

Main changes from v2:
- Merges PFAF biodiversity / companion planting facts.
- Merges PFAF growth fields from Physical Characteristics + Cultivation details.
- Separates:
    life_cycle
    botanical_life_cycle
    crop_life_cycle
    life_cycle_context
- Keeps PFAF search pages as low-confidence snapshots only.
- Does not let FPI search pages populate facts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
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
from project_paths import PATHS

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


# =========================================================
# MERGE HELPERS
# =========================================================


def set_field(
    profile: dict[str, Any],
    path: str,
    value: Any,
    source: str,
    overwrite: bool = False,
) -> None:
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


def extend_list_field(
    profile: dict[str, Any],
    path: str,
    values: list[Any],
    source: str,
) -> None:
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
        if item not in combined:
            combined.append(item)

    cursor[key] = combined
    profile.setdefault("field_sources", {})[path] = source


def dedupe_dict_list(items: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    seen = set()
    result = []

    for item in items:
        marker = tuple(item.get(key) for key in keys)

        if marker in seen:
            continue

        seen.add(marker)
        result.append(item)

    return result


def extend_dict_list_field(
    profile: dict[str, Any],
    path: str,
    values: list[dict[str, Any]],
    source: str,
    dedupe_keys: list[str],
) -> None:
    if not values:
        return

    parts = path.split(".")
    cursor = profile

    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})

    key = parts[-1]
    existing = cursor.get(key) or []
    combined = dedupe_dict_list(existing + values, dedupe_keys)

    cursor[key] = combined
    profile.setdefault("field_sources", {})[path] = source


def infer_preferred_propagation(profile: dict[str, Any], source: str = "Plants For A Future") -> None:
    """
    Adds DSS-friendly propagation interpretation.

    Example:
    PFAF may list both seed and division for mint, but its notes say seed
    cannot be relied on to breed true and division is best.
    """
    plant_atom = str(profile.get("plant_atom") or "").lower()

    germination = profile.setdefault("germination", {})
    methods = germination.get("propagation_methods") or []
    notes = str(germination.get("propagation_notes") or "").lower()

    preferred = germination.get("preferred_propagation_methods") or []

    # Mint / Mentha rule
    if plant_atom in {"mint", "peppermint", "spearmint"} or profile.get("identity", {}).get("genus") == "Mentha":
        if "division" in methods:
            if "division" not in preferred:
                preferred.append("division")

        if "seed" in methods and (
            "seed cannot be relied on to breed true" in notes or "best to propagate them by division" in notes or "prone to hybridisation" in notes
        ):
            germination["propagation_warning"] = (
                "Seed may not breed true; division is preferred for consistent aroma, cultivar traits, and medicinal oil profile."
            )

    if preferred:
        germination["preferred_propagation_methods"] = preferred
        profile.setdefault("field_sources", {})["germination.preferred_propagation_methods"] = source

    if germination.get("propagation_warning"):
        profile.setdefault("field_sources", {})["germination.propagation_warning"] = source


def add_source_metadata(profile: dict[str, Any], raw: dict[str, Any], source_name: str) -> None:
    for snap in raw.get("snapshots") or []:
        parsed = snap.get("parsed") or {}
        guessed = parsed.get("guessed_fields") or {}

        fields_provided = []

        for key, value in guessed.items():
            if key in ["trusted_detail", "note", "relevance_score", "is_search_page"]:
                continue

            if value not in (None, "", [], {}):
                fields_provided.append(key)

        profile["source_metadata"]["sources"].append(
            {
                "source_name": source_name,
                "source_url": snap.get("source_url"),
                "status": snap.get("status"),
                "trusted_detail": parsed.get("trusted_detail"),
                "relevance_score": parsed.get("relevance_score"),
                "fields_provided": fields_provided,
                "confidence": 0.80 if snap.get("status") == "trusted_detail" else 0.30,
                "last_verified_at": snap.get("fetched_at"),
            }
        )


# =========================================================
# GBIF
# =========================================================


def merge_gbif(profile: dict[str, Any], raw: dict[str, Any]) -> None:
    for snap in raw.get("snapshots") or []:
        payload = (snap.get("parsed") or {}).get("payload") or {}

        if not payload or payload.get("matchType") == "NONE":
            continue

        set_field(profile, "identity.scientific_name", payload.get("scientificName"), "GBIF")
        set_field(profile, "identity.genus", payload.get("genus"), "GBIF")
        set_field(profile, "identity.family", payload.get("family"), "GBIF")


# =========================================================
# PERENUAL
# =========================================================


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
        extend_list_field(
            profile,
            "germination.propagation_methods",
            _as_list(detail.get("propagation")),
            "Perenual",
        )
        set_field(profile, "growth.growth_speed", detail.get("growth_rate"), "Perenual")


# =========================================================
# PFAF
# =========================================================


def merge_pfaf(profile: dict[str, Any], raw: dict[str, Any]) -> None:
    for snap in raw.get("snapshots") or []:
        if snap.get("status") != "trusted_detail":
            continue

        guessed = (snap.get("parsed") or {}).get("guessed_fields") or {}
        # -----------------------------
        # Identity from PFAF
        # -----------------------------
        pfaf_identity = guessed.get("identity") or {}

        if isinstance(pfaf_identity, dict):
            set_field(
                profile,
                "identity.common_name",
                pfaf_identity.get("common_name"),
                "Plants For A Future",
            )

            set_field(
                profile,
                "identity.scientific_name",
                pfaf_identity.get("scientific_name"),
                "Plants For A Future",
            )

            set_field(
                profile,
                "identity.genus",
                pfaf_identity.get("genus"),
                "Plants For A Future",
            )

            set_field(
                profile,
                "identity.family",
                pfaf_identity.get("family"),
                "Plants For A Future",
            )

            extend_list_field(
                profile,
                "identity.synonyms",
                pfaf_identity.get("synonyms") or [],
                "Plants For A Future",
            )

            extend_list_field(
                profile,
                "identity.common_names",
                pfaf_identity.get("common_names") or [],
                "Plants For A Future",
            )

        # Backward-compatible fallback if older raw PFAF files do not yet have guessed["identity"].
        pfaf_family = guessed.get("pfaf_family")
        pfaf_display_latin_name = guessed.get("pfaf_display_latin_name")

        if pfaf_display_latin_name:
            genus = str(pfaf_display_latin_name).split()[0]
            set_field(
                profile,
                "identity.genus",
                genus,
                "Plants For A Future",
            )

        set_field(
            profile,
            "identity.family",
            pfaf_family,
            "Plants For A Future",
        )

        # -----------------------------
        # Classification
        # -----------------------------
        extend_list_field(
            profile,
            "classification.edible_parts",
            guessed.get("edible_parts") or [],
            "Plants For A Future",
        )

        extend_list_field(
            profile,
            "classification.use_categories",
            guessed.get("use_categories") or [],
            "Plants For A Future",
        )

        set_field(
            profile,
            "classification.life_cycle",
            guessed.get("life_cycle"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "classification.botanical_life_cycle",
            guessed.get("botanical_life_cycle"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "classification.crop_life_cycle",
            guessed.get("crop_life_cycle"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "classification.life_cycle_context",
            guessed.get("life_cycle_context"),
            "Plants For A Future",
        )

        # If edible parts exist, mark as edible.
        if guessed.get("edible_parts"):
            set_field(
                profile,
                "classification.edible",
                True,
                "Plants For A Future",
            )

        # -----------------------------
        # Germination / propagation
        # -----------------------------
        extend_list_field(
            profile,
            "germination.propagation_methods",
            guessed.get("propagation_methods") or [],
            "Plants For A Future",
        )

        set_field(
            profile,
            "germination.propagation_notes",
            guessed.get("propagation_notes"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "germination.germination_days_min",
            guessed.get("germination_days_min"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "germination.germination_days_max",
            guessed.get("germination_days_max"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "germination.sowing_depth_cm",
            guessed.get("sowing_depth_cm"),
            "Plants For A Future",
        )

        # -----------------------------
        # Growth
        # -----------------------------
        growth = guessed.get("growth") or {}

        extend_list_field(
            profile,
            "growth.sunlight",
            growth.get("sunlight") or [],
            "Plants For A Future",
        )

        extend_list_field(
            profile,
            "growth.soil_type",
            growth.get("soil_type") or [],
            "Plants For A Future",
        )

        set_field(
            profile,
            "growth.soil_ph_min",
            growth.get("soil_ph_min"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "growth.soil_ph_max",
            growth.get("soil_ph_max"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "growth.water_need",
            growth.get("water_need"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "growth.growth_speed",
            growth.get("growth_speed"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "growth.soil_notes",
            growth.get("soil_notes"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "growth.water_notes",
            growth.get("water_notes"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "growth.light_notes",
            growth.get("light_notes"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "growth.temperature_notes",
            growth.get("temperature_notes"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "growth.rainfall_notes",
            growth.get("rainfall_notes"),
            "Plants For A Future",
        )

        # -----------------------------
        # Care / notes
        # -----------------------------
        set_field(
            profile,
            "care.cultivation_notes",
            guessed.get("cultivation_notes"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "care.cautions",
            guessed.get("known_hazards"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "care.nutrition_notes",
            guessed.get("medicinal_notes"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "care.other_uses_notes",
            guessed.get("other_uses_notes"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "care.edible_uses_notes",
            guessed.get("edible_uses_notes"),
            "Plants For A Future",
        )

        # -----------------------------
        # Biodiversity / companion planting
        # -----------------------------
        biodiversity = guessed.get("biodiversity") or {}

        extend_dict_list_field(
            profile,
            "biodiversity.companions",
            biodiversity.get("companions") or [],
            "Plants For A Future",
            dedupe_keys=["plant", "relationship"],
        )

        extend_dict_list_field(
            profile,
            "biodiversity.conflicts",
            biodiversity.get("conflicts") or [],
            "Plants For A Future",
            dedupe_keys=["plant", "relationship"],
        )

        extend_dict_list_field(
            profile,
            "biodiversity.repels_pests",
            biodiversity.get("repels_pests") or [],
            "Plants For A Future",
            dedupe_keys=["target", "mechanism"],
        )

        extend_dict_list_field(
            profile,
            "biodiversity.attracts_beneficial_insects",
            biodiversity.get("attracts_beneficial_insects") or [],
            "Plants For A Future",
            dedupe_keys=["insect_group"],
        )

        set_field(
            profile,
            "biodiversity.pollinator_support",
            biodiversity.get("pollinator_support"),
            "Plants For A Future",
        )

        set_field(
            profile,
            "biodiversity.pest_confuser",
            biodiversity.get("pest_confuser"),
            "Plants For A Future",
        )

        extend_list_field(
            profile,
            "biodiversity.biodiversity_notes",
            biodiversity.get("biodiversity_notes") or [],
            "Plants For A Future",
        )


# =========================================================
# FPI
# =========================================================


def merge_fpi(profile: dict[str, Any], raw: dict[str, Any]) -> None:
    """
    FPI is snapshot-only until a source-specific plant-page/PDF parser is added.
    This prevents search-page menu text from becoming plant facts.
    """
    for snap in raw.get("snapshots") or []:
        if snap.get("status") != "trusted_detail":
            continue

        # Add trusted FPI mapping later only after real FPI detail/PDF parsing.
        pass


# =========================================================
# MISSING FIELD CHECK
# =========================================================


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


# =========================================================
# MAIN MERGE
# =========================================================


def merge_one(plant: dict[str, Any]) -> dict[str, Any]:
    profile = canonical_profile_template(plant)

    # Make sure new fields exist even if your old template does not have them.
    profile.setdefault("classification", {})
    profile["classification"].setdefault("botanical_life_cycle", None)
    profile["classification"].setdefault("crop_life_cycle", None)
    profile["classification"].setdefault("life_cycle_context", None)

    profile.setdefault("biodiversity", {})
    profile["biodiversity"].setdefault("companions", [])
    profile["biodiversity"].setdefault("conflicts", [])
    profile["biodiversity"].setdefault("repels_pests", [])
    profile["biodiversity"].setdefault("attracts_beneficial_insects", [])
    profile["biodiversity"].setdefault("pollinator_support", None)
    profile["biodiversity"].setdefault("pest_confuser", None)
    profile["biodiversity"].setdefault("biodiversity_notes", [])

    profile.setdefault("care", {})
    profile["care"].setdefault("other_uses_notes", None)
    profile["care"].setdefault("edible_uses_notes", None)

    profile.setdefault("germination", {})
    profile["germination"].setdefault("preferred_propagation_methods", [])
    profile["germination"].setdefault("propagation_warning", None)

    profile.setdefault("growth", {})
    profile["growth"].setdefault("temperature_notes", None)
    profile["growth"].setdefault("rainfall_notes", None)

    # Local seed identity is the anchor.
    if plant.get("scientific_name"):
        set_field(
            profile,
            "identity.scientific_name",
            plant["scientific_name"],
            "local_seed",
            overwrite=True,
        )

    if plant.get("common_name"):
        set_field(
            profile,
            "identity.common_name",
            plant["common_name"],
            "local_seed",
            overwrite=True,
        )

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

    infer_preferred_propagation(profile)

    profile["source_metadata"]["last_merged_at"] = utc_now()
    compute_missing_fields(profile)

    return profile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plants",
        default=str(PATHS.plants_seed),
        help="Path to plant seed JSON file.",
    )
    args = parser.parse_args()

    PATHS.ensure_dirs()
    ensure_dirs()
    plants = load_plants(Path(args.plants))

    for plant in plants:
        profile = merge_one(plant)
        out = NORMALIZED_DIR / plant_filename(plant)
        write_json(out, profile)
        print(f"[MERGE v3] wrote {out}")


if __name__ == "__main__":
    main()
