#!/usr/bin/env python3
"""
enrich_plants_with_pest_ids.py

Purpose:
- Read normalized pest_bank.json.bak.
- Match pests_ver01 to normalized plant profiles.
- Add only lightweight pest relationships to each plant profile:

    pests_and_diseases.known_pest_ids

- Remove old/heavy field:

    pests_and_diseases.known_pests

Design decision:
- Plant profile stores only pest IDs.
- pest_bank.json.bak stores pest details.
- Prolog later uses pest IDs to look up damage, prevention, predators, treatment.

Input:
    data_bank/normalized/pest_bank.json.bak
    data_bank/normalized/plants/*.json

Output:
    updated data_bank/normalized/plants/*.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_paths import PATHS  # noqa: E402

# =========================================================
# BASIC HELPERS
# =========================================================


def clean_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)

    return text or None


def to_snake(value: Any) -> Optional[str]:
    text = clean_text(value)

    if not text:
        return None

    text = text.lower()
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^a-z0-9\s_]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_")

    return text or None


def dedupe_keep_order(items: Iterable[Any]) -> List[str]:
    seen = set()
    result: List[str] = []

    for item in items:
        text = clean_text(item)

        if not text:
            continue

        key = text.lower()

        if key not in seen:
            seen.add(key)
            result.append(text)

    return result


def clean_atom_list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, list):
        raw_items = value
    else:
        raw_items = [value]

    result: List[str] = []

    for item in raw_items:
        atom = to_snake(item)

        if atom:
            result.append(atom)

    return dedupe_keep_order(result)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON file: {path}") from exc


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# =========================================================
# ORDERING
# =========================================================


def reorder_dict_keys(data: Dict[str, Any], preferred_order: List[str]) -> Dict[str, Any]:
    ordered: Dict[str, Any] = {}

    for key in preferred_order:
        if key in data:
            ordered[key] = data[key]

    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value

    return ordered


def reorder_pests_and_diseases(pests: Dict[str, Any]) -> Dict[str, Any]:
    preferred_order = [
        "disease_notes",
        "known_disease_ids",
        "known_pest_ids",
        "treatment_notes",
    ]

    return reorder_dict_keys(pests, preferred_order)


def reorder_profile_sections(profile: Dict[str, Any]) -> Dict[str, Any]:
    preferred_order = [
        "plant_atom",
        "identity",
        "classification",
        "growth",
        "germination",
        "spacing",
        "care",
        "biodiversity",
        "pests_and_diseases",
        "field_sources",
        "source_metadata",
        "missing_fields",
    ]

    return reorder_dict_keys(profile, preferred_order)


# =========================================================
# PROFILE TOKEN EXTRACTION
# =========================================================


def collect_strings_recursive(value: Any) -> Set[str]:
    result: Set[str] = set()

    if isinstance(value, dict):
        for key, nested in value.items():
            key_norm = to_snake(key)

            if key_norm in {
                "description",
                "notes",
                "source_url",
                "image_url",
                "raw_text",
                "cultivation_notes",
                "edible_uses_notes",
                "nutrition_notes",
                "other_uses_notes",
                "propagation_notes",
                "soil_notes",
                "water_notes",
                "light_notes",
            }:
                continue

            result.update(collect_strings_recursive(nested))

    elif isinstance(value, list):
        for item in value:
            result.update(collect_strings_recursive(item))

    else:
        norm = to_snake(value)

        if norm:
            result.add(norm)

    return result


def plant_identity_tokens(profile: Dict[str, Any], file_path: Path) -> Set[str]:
    tokens: Set[str] = set()

    for key in [
        "plant_atom",
        "name",
        "common_name",
        "scientific_name",
        "genus",
    ]:
        atom = to_snake(profile.get(key))

        if atom:
            tokens.add(atom)

    identity = profile.get("identity")

    if isinstance(identity, dict):
        for key in [
            "plant_atom",
            "name",
            "common_name",
            "scientific_name",
            "genus",
            "family",
        ]:
            atom = to_snake(identity.get(key))

            if atom:
                tokens.add(atom)

        for key in ["common_names", "synonyms", "aliases"]:
            for atom in clean_atom_list(identity.get(key)):
                tokens.add(atom)

    filename_atom = to_snake(file_path.stem)

    if filename_atom:
        tokens.add(filename_atom)

    return tokens


def plant_group_tokens(profile: Dict[str, Any]) -> Set[str]:
    tokens: Set[str] = set()

    candidate_sections = [
        profile.get("classification"),
        profile.get("taxonomy"),
        profile.get("groups"),
        profile.get("plant_groups"),
        profile.get("use_categories"),
        profile.get("edible_uses"),
        profile.get("traits"),
    ]

    for section in candidate_sections:
        tokens.update(collect_strings_recursive(section))

    for key in [
        "family",
        "genus",
        "plant_type",
        "type",
        "life_cycle",
    ]:
        atom = to_snake(profile.get(key))

        if atom:
            tokens.add(atom)

    identity = profile.get("identity")

    if isinstance(identity, dict):
        for key in ["family", "genus"]:
            atom = to_snake(identity.get(key))

            if atom:
                tokens.add(atom)

    classification = profile.get("classification")

    if isinstance(classification, dict):
        for key in [
            "use_categories",
            "edible_parts",
            "life_cycle",
            "crop_life_cycle",
            "botanical_life_cycle",
        ]:
            tokens.update(clean_atom_list(classification.get(key)))

    return tokens


# =========================================================
# PEST BANK MATCHING
# =========================================================


def normalize_pest_bank(raw_bank: Any) -> Dict[str, Dict[str, Any]]:
    bank: Dict[str, Dict[str, Any]] = {}

    if isinstance(raw_bank, dict):
        for key, value in raw_bank.items():
            if not isinstance(value, dict):
                continue

            pest_id = to_snake(value.get("pest_id") or key)

            if not pest_id:
                continue

            normalized = dict(value)
            normalized["pest_id"] = pest_id
            bank[pest_id] = normalized

        return bank

    if isinstance(raw_bank, list):
        for item in raw_bank:
            if not isinstance(item, dict):
                continue

            pest_id = to_snake(item.get("pest_id") or item.get("display_name"))

            if not pest_id:
                continue

            normalized = dict(item)
            normalized["pest_id"] = pest_id
            bank[pest_id] = normalized

        return bank

    raise RuntimeError("Pest bank must be a JSON object or list.")


def pest_matches_plant(
    pest: Dict[str, Any],
    identity_tokens: Set[str],
    group_tokens: Set[str],
) -> bool:
    plants_affected = set(clean_atom_list(pest.get("plants_affected")))
    groups_affected = set(clean_atom_list(pest.get("plant_groups_affected")))

    if plants_affected.intersection(identity_tokens):
        return True

    if groups_affected.intersection(group_tokens):
        return True

    return False


def find_matching_pest_ids(
    profile: Dict[str, Any],
    profile_path: Path,
    pest_bank: Dict[str, Dict[str, Any]],
) -> List[str]:
    identity_tokens = plant_identity_tokens(profile, profile_path)
    group_tokens = plant_group_tokens(profile)

    matched_ids: List[str] = []

    for pest_id, pest in pest_bank.items():
        if pest_matches_plant(pest, identity_tokens, group_tokens):
            matched_ids.append(pest_id)

    return dedupe_keep_order(sorted(matched_ids))


# =========================================================
# MISSING FIELDS CLEANUP
# =========================================================


def remove_resolved_missing_fields(profile: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = profile.get("missing_fields")

    if not isinstance(missing_fields, list):
        return profile

    fields_to_remove = {
        "pests_and_diseases.known_pests",
        "pests_and_diseases.known_pest_ids",
    }

    profile["missing_fields"] = [field for field in missing_fields if field not in fields_to_remove]

    return profile


# =========================================================
# PROFILE ENRICHMENT
# =========================================================


def normalize_pests_section(existing: Any) -> Dict[str, Any]:
    if isinstance(existing, dict):
        pests = dict(existing)
    else:
        pests = {}

    pests.setdefault("disease_notes", None)
    pests.setdefault("known_disease_ids", [])
    pests.setdefault("known_pest_ids", [])
    pests.setdefault("treatment_notes", None)

    # Long-term decision:
    # pest details do NOT live in plant profiles.
    pests.pop("known_pests", None)

    # Also remove known_diseases if previous disease enrichment left it there.
    pests.pop("known_diseases", None)

    pests["known_disease_ids"] = clean_atom_list(pests.get("known_disease_ids"))
    pests["known_pest_ids"] = clean_atom_list(pests.get("known_pest_ids"))

    return reorder_pests_and_diseases(pests)


def enrich_profile_with_pests(
    profile: Dict[str, Any],
    profile_path: Path,
    pest_bank: Dict[str, Dict[str, Any]],
    remove_unmatched_existing: bool = False,
) -> Tuple[Dict[str, Any], bool, List[str]]:
    matched_ids = find_matching_pest_ids(profile, profile_path, pest_bank)

    old_profile_json = json.dumps(profile, sort_keys=True, ensure_ascii=False)

    updated = dict(profile)
    pests = normalize_pests_section(updated.get("pests_and_diseases"))

    existing_ids = clean_atom_list(pests.get("known_pest_ids"))

    if remove_unmatched_existing:
        new_ids = matched_ids
    else:
        new_ids = dedupe_keep_order(existing_ids + matched_ids)

    pests["known_pest_ids"] = new_ids

    # Keep lightweight.
    pests.pop("known_pests", None)

    pests = reorder_pests_and_diseases(pests)

    updated["pests_and_diseases"] = pests
    updated = remove_resolved_missing_fields(updated)
    updated = reorder_profile_sections(updated)

    new_profile_json = json.dumps(updated, sort_keys=True, ensure_ascii=False)
    changed = old_profile_json != new_profile_json

    return updated, changed, matched_ids


# =========================================================
# BULK ENRICHMENT
# =========================================================


def find_plant_profiles(profiles_dir: Path) -> List[Path]:
    if not profiles_dir.exists():
        raise RuntimeError(f"Profiles directory does not exist: {profiles_dir}")

    return sorted(profiles_dir.glob("*.json"))


def enrich_all_profiles(
    profiles_dir: Path,
    pest_bank_path: Path,
    dry_run: bool = False,
    only: Optional[str] = None,
    remove_unmatched_existing: bool = False,
) -> Dict[str, Any]:
    raw_bank = load_json(pest_bank_path, default={})
    pest_bank = normalize_pest_bank(raw_bank)

    profile_paths = find_plant_profiles(profiles_dir)

    if only:
        only_atom = to_snake(only)
        profile_paths = [path for path in profile_paths if to_snake(path.stem) == only_atom]

    changed_count = 0
    matched_count = 0
    scanned_count = 0
    details = []

    for profile_path in profile_paths:
        profile = load_json(profile_path, default={})

        if not isinstance(profile, dict):
            print(f"[SKIP] Invalid profile JSON object: {profile_path}")
            continue

        scanned_count += 1

        updated, changed, matched_ids = enrich_profile_with_pests(
            profile=profile,
            profile_path=profile_path,
            pest_bank=pest_bank,
            remove_unmatched_existing=remove_unmatched_existing,
        )

        if matched_ids:
            matched_count += 1

        if changed:
            changed_count += 1

            if not dry_run:
                save_json(profile_path, updated)

        details.append(
            {
                "plant_file": str(profile_path),
                "matched_pest_ids": matched_ids,
                "changed": changed,
            }
        )

    return {
        "profiles_scanned": scanned_count,
        "profiles_with_matches": matched_count,
        "profiles_changed": changed_count,
        "pest_bank_entries": len(pest_bank),
        "details": details,
    }


# =========================================================
# REPORTING
# =========================================================


def print_summary(summary: Dict[str, Any], dry_run: bool) -> None:
    print("")
    print("========== Plant Pest ID Enrichment Summary ==========")
    print(f"Dry run              : {dry_run}")
    print(f"Pest bank entries    : {summary['pest_bank_entries']}")
    print(f"Profiles scanned     : {summary['profiles_scanned']}")
    print(f"Profiles with matches: {summary['profiles_with_matches']}")
    print(f"Profiles changed     : {summary['profiles_changed']}")
    print("======================================================")

    print("")
    print("Changed or matched profiles:")

    shown = 0

    for item in summary["details"]:
        if not item["changed"] and not item["matched_pest_ids"]:
            continue

        plant_file = Path(item["plant_file"]).name
        pest_ids = ", ".join(item["matched_pest_ids"]) or "-"
        changed = item["changed"]

        print(f" - {plant_file}: {pest_ids} | changed={changed}")
        shown += 1

        if shown >= 60:
            break

    remaining = len([item for item in summary["details"] if item["changed"] or item["matched_pest_ids"]]) - shown

    if remaining > 0:
        print(f" ... and {remaining} more")

    print("")


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Add lightweight known_pest_ids to plant profiles from central pest bank.")

    parser.add_argument(
        "--profiles",
        default=str(PATHS.normalized_plants),
        help="Directory containing normalized plant profile JSON files.",
    )

    parser.add_argument(
        "--pest-bank",
        default=str(PATHS.pest_bank),
        help="Normalized pest bank JSON file.",
    )

    parser.add_argument(
        "--only",
        default=None,
        help="Only enrich one plant profile by plant atom or filename stem, e.g. tomato.",
    )

    parser.add_argument(
        "--replace",
        action="store_true",
        help=("Replace existing known_pest_ids with current pest bank matches. " "Default is append/merge."),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying plant profiles.",
    )

    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Print resolved project paths.",
    )

    args = parser.parse_args()

    PATHS.ensure_dirs()

    if args.show_paths:
        PATHS.print_summary()

    profiles_dir = Path(args.profiles)
    pest_bank_path = Path(args.pest_bank)

    if not pest_bank_path.exists():
        raise RuntimeError(f"Pest bank does not exist: {pest_bank_path}. " f"Run scripts/pest/extract_pest_bank.py first.")

    summary = enrich_all_profiles(
        profiles_dir=profiles_dir,
        pest_bank_path=pest_bank_path,
        dry_run=args.dry_run,
        only=args.only,
        remove_unmatched_existing=args.replace,
    )

    print_summary(summary, dry_run=args.dry_run)

    if args.dry_run:
        print("[DRY-RUN] No plant profiles were modified.")
    else:
        print("[OK] Plant profiles updated with lightweight known_pest_ids.")


if __name__ == "__main__":
    main()
