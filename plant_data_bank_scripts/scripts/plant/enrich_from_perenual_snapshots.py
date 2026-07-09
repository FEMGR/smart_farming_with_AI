#!/usr/bin/env python3
"""
enrich_from_perenual_snapshots.py

Purpose:
- Scan temporary Perenual snapshot JSON files.
- Extract scientific_name, common_name, genus, and useful species traits.
- Check whether the plant already exists in Prolog identity facts.
- If matched:
    update data/extracted/perenual_enriched_species.json
- If not matched:
    create a new candidate in data/extracted/perenual_enriched_species.json
    add it to data/seeds/missing_plant_seed.json

Important:
- This script does NOT update Prolog directly.
- Prolog should be updated later by your existing export/update script.

How to run:
python3 plant_data_bank_scripts/scripts/plant/enrich_from_perenual_snapshots.py --show-paths
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_paths import PATHS  # noqa: E402
from common import read_json, write_json  # noqa: E402

# =========================================================
# GENERAL HELPERS
# =========================================================


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    if isinstance(value, list):
        value = value[0] if value else None

    if value is None:
        return None

    text = str(value).strip()
    return text or None


def clean_list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, list):
        raw_items = value
    else:
        raw_items = [value]

    result: List[str] = []

    for item in raw_items:
        text = clean_text(item)

        if text:
            result.append(text)

    return dedupe_keep_order(result)


def dedupe_keep_order(items: Iterable[str]) -> List[str]:
    seen = set()
    result = []

    for item in items:
        key = str(item).strip().lower()

        if key and key not in seen:
            seen.add(key)
            result.append(str(item).strip())

    return result


def normalize_key(value: Any) -> Optional[str]:
    text = clean_text(value)

    if not text:
        return None

    text = text.lower()
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s_]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)

    text = text.strip("_")
    return text or None


def normalize_scientific_name(value: Any) -> Optional[str]:
    text = clean_text(value)

    if not text:
        return None

    text = re.sub(r"\s+", " ", text.strip())
    return text.lower()


def to_plant_atom(value: Any) -> Optional[str]:
    atom = normalize_key(value)

    if not atom:
        return None

    if atom[0].isdigit():
        atom = f"plant_{atom}"

    return atom


def extract_genus(scientific_name: Optional[str], raw_item: Dict[str, Any]) -> Optional[str]:
    direct_genus = clean_text(raw_item.get("genus"))

    if direct_genus:
        return direct_genus

    if scientific_name:
        parts = scientific_name.split()

        if parts:
            return parts[0]

    return None


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
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def get_path(data: Dict[str, Any], path: str) -> Any:
    cursor: Any = data

    for part in path.split("."):
        if not isinstance(cursor, dict):
            return None

        cursor = cursor.get(part)

    return cursor


def set_path_if_blank(data: Dict[str, Any], path: str, value: Any, source: str) -> bool:
    if value in (None, "", [], {}):
        return False

    parts = path.split(".")
    cursor: Dict[str, Any] = data

    for part in parts[:-1]:
        child = cursor.setdefault(part, {})

        if not isinstance(child, dict):
            return False

        cursor = child

    key = parts[-1]

    if cursor.get(key) not in (None, "", [], {}):
        return False

    cursor[key] = value
    data.setdefault("field_sources", {})[path] = source
    return True


def extend_path_list(data: Dict[str, Any], path: str, values: List[Any], source: str) -> bool:
    clean_values = [value for value in values if value not in (None, "", [], {})]

    if not clean_values:
        return False

    parts = path.split(".")
    cursor: Dict[str, Any] = data

    for part in parts[:-1]:
        child = cursor.setdefault(part, {})

        if not isinstance(child, dict):
            return False

        cursor = child

    key = parts[-1]
    existing = cursor.get(key)

    if existing in (None, "", {}):
        existing_list: List[Any] = []
    elif isinstance(existing, list):
        existing_list = existing
    else:
        existing_list = [existing]

    combined: List[Any] = []

    for item in [*existing_list, *clean_values]:
        if item not in combined:
            combined.append(item)

    if combined == existing_list:
        return False

    cursor[key] = combined
    data.setdefault("field_sources", {})[path] = source
    return True


# =========================================================
# PERENUAL SNAPSHOT PARSING
# =========================================================


def unwrap_perenual_payload(raw: Any) -> List[Dict[str, Any]]:
    """
    Supports common snapshot shapes:

    Detail response:
        {"id": 1, "common_name": "...", "scientific_name": [...]}

    Search response:
        {"data": [{...}, {...}]}

    Wrapped response:
        {"payload": {...}}
        {"response": {...}}
        {"plant": {...}}
    """

    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]

    if not isinstance(raw, dict):
        return []

    data = raw.get("data")

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    if isinstance(data, dict):
        return [data]

    for key in ["payload", "response", "result", "plant", "species", "details"]:
        wrapped = raw.get(key)

        if isinstance(wrapped, dict):
            return unwrap_perenual_payload(wrapped)

        if isinstance(wrapped, list):
            return [item for item in wrapped if isinstance(item, dict)]

    if any(
        key in raw
        for key in [
            "common_name",
            "scientific_name",
            "watering",
            "sunlight",
            "cycle",
            "propagation",
        ]
    ):
        return [raw]

    return []


def extract_scientific_name(item: Dict[str, Any]) -> Optional[str]:
    scientific = item.get("scientific_name")

    if isinstance(scientific, list):
        return clean_text(scientific[0]) if scientific else None

    return clean_text(scientific)


def extract_image_url(item: Dict[str, Any]) -> Optional[str]:
    image = item.get("default_image")

    if isinstance(image, dict):
        for key in [
            "original_url",
            "regular_url",
            "medium_url",
            "small_url",
            "thumbnail",
        ]:
            url = clean_text(image.get(key))

            if url:
                return url

    return clean_text(item.get("image_url"))


def extract_hardiness(item: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
    hardiness = item.get("hardiness")

    if not isinstance(hardiness, dict):
        return None, None

    def parse_int(value: Any) -> Optional[int]:
        if value is None:
            return None

        try:
            return int(str(value).strip())
        except ValueError:
            return None

    return parse_int(hardiness.get("min")), parse_int(hardiness.get("max"))


def normalize_enum(value: Any) -> Optional[str]:
    return normalize_key(value)


def normalize_enum_list(value: Any) -> List[str]:
    result = []

    for item in clean_list(value):
        normalized = normalize_key(item)

        if normalized:
            result.append(normalized)

    return dedupe_keep_order(result)


# =========================================================
# PROLOG IDENTITY INDEX
# =========================================================


def strip_quotes(value: str) -> str:
    value = value.strip()

    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        value = value[1:-1]

    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]

    return value.strip()


def split_prolog_args(arg_text: str) -> List[str]:
    """
    Splits simple Prolog arguments while respecting quoted strings.

    Example:
        "tomato, 'Solanum lycopersicum'"
        -> ["tomato", "'Solanum lycopersicum'"]
    """

    args = []
    current = []
    quote: Optional[str] = None
    escape = False

    for char in arg_text:
        if escape:
            current.append(char)
            escape = False
            continue

        if char == "\\":
            current.append(char)
            escape = True
            continue

        if quote:
            current.append(char)

            if char == quote:
                quote = None

            continue

        if char in ["'", '"']:
            quote = char
            current.append(char)
            continue

        if char == ",":
            args.append("".join(current).strip())
            current = []
            continue

        current.append(char)

    if current:
        args.append("".join(current).strip())

    return args


def parse_prolog_facts_from_file(path: Path) -> List[Tuple[str, List[str]]]:
    facts: List[Tuple[str, List[str]]] = []

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")

    # Remove single-line comments.
    cleaned_lines = []

    for line in text.splitlines():
        line = line.split("%", 1)[0].strip()

        if line:
            cleaned_lines.append(line)

    cleaned = " ".join(cleaned_lines)

    # Match simple facts: predicate(arg1, arg2).
    pattern = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)\s*\.")

    for match in pattern.finditer(cleaned):
        predicate = match.group(1)
        args = split_prolog_args(match.group(2))
        facts.append((predicate, args))

    return facts


def build_prolog_identity_index(prolog_root: Path) -> Dict[str, Dict[str, Any]]:
    """
    Builds identity indexes from existing Prolog files.

    Recognized facts:
        plant(tomato).
        plant_common_name(tomato, 'Tomato').
        plant_scientific_name(tomato, 'Solanum lycopersicum').
        scientific_name(tomato, 'Solanum lycopersicum').
        plant_genus(tomato, solanum).
        genus(tomato, solanum).

    You can add more predicates in the predicate sets below if your project uses different names.
    """

    index = {
        "by_atom": {},
        "by_common": {},
        "by_scientific": {},
        "by_genus": {},
    }

    if not prolog_root.exists():
        print(f"[WARN] Prolog root does not exist: {prolog_root}")
        return index

    scientific_predicates = {
        "plant_scientific_name",
        "scientific_name",
        "species_scientific_name",
    }

    common_predicates = {
        "plant_common_name",
        "common_name",
        "species_common_name",
    }

    genus_predicates = {
        "plant_genus",
        "genus",
        "species_genus",
    }

    plant_predicates = {
        "plant",
        "known_plant",
        "snapshot_plant",
    }

    for path in sorted(prolog_root.rglob("*.pl")):
        facts = parse_prolog_facts_from_file(path)

        for predicate, args in facts:
            if not args:
                continue

            if predicate in plant_predicates and len(args) >= 1:
                plant_atom = strip_quotes(args[0])
                atom_key = normalize_key(plant_atom)

                if atom_key:
                    index["by_atom"][atom_key] = {
                        "plant_atom": atom_key,
                        "source_file": str(path),
                    }

            elif predicate in scientific_predicates and len(args) >= 2:
                plant_atom = strip_quotes(args[0])
                scientific = strip_quotes(args[1])

                atom_key = normalize_key(plant_atom)
                scientific_key = normalize_scientific_name(scientific)

                if atom_key and scientific_key:
                    record = {
                        "plant_atom": atom_key,
                        "scientific_name": scientific,
                        "source_file": str(path),
                    }

                    index["by_scientific"][scientific_key] = record
                    index["by_atom"].setdefault(atom_key, record)

            elif predicate in common_predicates and len(args) >= 2:
                plant_atom = strip_quotes(args[0])
                common = strip_quotes(args[1])

                atom_key = normalize_key(plant_atom)
                common_key = normalize_key(common)

                if atom_key and common_key:
                    record = {
                        "plant_atom": atom_key,
                        "common_name": common,
                        "source_file": str(path),
                    }

                    index["by_common"][common_key] = record
                    index["by_atom"].setdefault(atom_key, record)

            elif predicate in genus_predicates and len(args) >= 2:
                plant_atom = strip_quotes(args[0])
                genus = strip_quotes(args[1])

                atom_key = normalize_key(plant_atom)
                genus_key = normalize_key(genus)

                if atom_key and genus_key:
                    index["by_genus"].setdefault(genus_key, []).append(
                        {
                            "plant_atom": atom_key,
                            "genus": genus,
                            "source_file": str(path),
                        }
                    )

    return index


# =========================================================
# MATCHING
# =========================================================


def resolve_snapshot_identity(
    item: Dict[str, Any],
    source_file: Path,
    prolog_index: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    common_name = clean_text(item.get("common_name")) or clean_text(item.get("name"))
    scientific_name = extract_scientific_name(item)
    genus = extract_genus(scientific_name, item)

    scientific_key = normalize_scientific_name(scientific_name)
    common_key = normalize_key(common_name)
    filename_key = normalize_key(source_file.stem)

    matched_record: Optional[Dict[str, Any]] = None
    match_method = "new_from_snapshot"
    confidence = 0.70

    # 1. Best match: exact scientific name.
    if scientific_key and scientific_key in prolog_index["by_scientific"]:
        matched_record = prolog_index["by_scientific"][scientific_key]
        match_method = "scientific_name_exact"
        confidence = 0.98

    # 2. Common name match.
    elif common_key and common_key in prolog_index["by_common"]:
        matched_record = prolog_index["by_common"][common_key]
        match_method = "common_name_exact"
        confidence = 0.90

    # 3. Plant atom match from common name.
    elif common_key and common_key in prolog_index["by_atom"]:
        matched_record = prolog_index["by_atom"][common_key]
        match_method = "plant_atom_from_common_name"
        confidence = 0.88

    # 4. Filename match.
    elif filename_key and filename_key in prolog_index["by_atom"]:
        matched_record = prolog_index["by_atom"][filename_key]
        match_method = "filename_atom_match"
        confidence = 0.80

    if matched_record:
        plant_atom = matched_record["plant_atom"]

        resolved_common_name = common_name or matched_record.get("common_name") or plant_atom.replace("_", " ")

        resolved_scientific_name = scientific_name or matched_record.get("scientific_name")

        return {
            "plant_atom": plant_atom,
            "common_name": resolved_common_name,
            "scientific_name": resolved_scientific_name,
            "genus": genus,
            "is_known_in_prolog": True,
            "match_method": match_method,
            "confidence": confidence,
            "matched_prolog_source": matched_record.get("source_file"),
        }

    # New plant candidate.
    # Prefer common_name for atom if available, otherwise scientific name.
    fallback_atom = to_plant_atom(common_name) or to_plant_atom(scientific_name) or to_plant_atom(source_file.stem)

    return {
        "plant_atom": fallback_atom,
        "common_name": common_name,
        "scientific_name": scientific_name,
        "genus": genus,
        "is_known_in_prolog": False,
        "match_method": match_method,
        "confidence": confidence,
        "matched_prolog_source": None,
    }


# =========================================================
# NORMALIZED RECORD CREATION
# =========================================================


def normalize_snapshot_record(
    item: Dict[str, Any],
    source_file: Path,
    prolog_index: Dict[str, Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    identity = resolve_snapshot_identity(item, source_file, prolog_index)

    plant_atom = identity.get("plant_atom")

    if not plant_atom:
        return None

    hardiness_min, hardiness_max = extract_hardiness(item)

    record = {
        "plant_atom": plant_atom,
        "common_name": identity.get("common_name"),
        "scientific_name": identity.get("scientific_name"),
        "genus": identity.get("genus"),
        "perenual_id": item.get("id"),
        "family": clean_text(item.get("family")),
        "type": normalize_enum(item.get("type")),
        "cycle": normalize_enum(item.get("cycle")),
        "watering": normalize_enum(item.get("watering")),
        "watering_general_benchmark": item.get("watering_general_benchmark"),
        "sunlight": normalize_enum_list(item.get("sunlight")),
        "propagation": normalize_enum_list(item.get("propagation")),
        "soil": normalize_enum_list(item.get("soil")),
        "growth_rate": normalize_enum(item.get("growth_rate")),
        "maintenance": normalize_enum(item.get("maintenance")),
        "care_level": normalize_enum(item.get("care_level")),
        "drought_tolerant": item.get("drought_tolerant"),
        "salt_tolerant": item.get("salt_tolerant"),
        "thorny": item.get("thorny"),
        "invasive": item.get("invasive"),
        "tropical": item.get("tropical"),
        "indoor": item.get("indoor"),
        "flowers": item.get("flowers"),
        "flowering_season": normalize_enum(item.get("flowering_season")),
        "fruits": item.get("fruits"),
        "edible_fruit": item.get("edible_fruit"),
        "edible_leaf": item.get("edible_leaf"),
        "cuisine": item.get("cuisine"),
        "medicinal": item.get("medicinal"),
        "poisonous_to_humans": item.get("poisonous_to_humans"),
        "poisonous_to_pets": item.get("poisonous_to_pets"),
        "hardiness_min": hardiness_min,
        "hardiness_max": hardiness_max,
        "description": clean_text(item.get("description")),
        "image_url": extract_image_url(item),
        "source_name": "perenual_snapshot",
        "source_file": str(source_file),
        "is_known_in_prolog": identity["is_known_in_prolog"],
        "match_method": identity["match_method"],
        "confidence": identity["confidence"],
        "matched_prolog_source": identity["matched_prolog_source"],
        "last_synced_at": now_iso(),
    }

    return record


# =========================================================
# MERGING
# =========================================================


def merge_record(existing: Optional[Dict[str, Any]], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """
    Missing-only merge.

    Existing values win.
    Incoming values fill blanks.
    Lists are merged.
    """

    if not existing:
        return incoming

    merged = dict(existing)

    for key, incoming_value in incoming.items():
        existing_value = merged.get(key)

        if isinstance(existing_value, list) or isinstance(incoming_value, list):
            merged[key] = dedupe_keep_order(clean_list(existing_value) + clean_list(incoming_value))
            continue

        if existing_value in [None, "", [], {}] and incoming_value not in [None, "", [], {}]:
            merged[key] = incoming_value

    # Keep latest metadata.
    merged["last_synced_at"] = now_iso()

    # If incoming has a stronger confidence, keep matching metadata.
    try:
        existing_conf = float(existing.get("confidence") or 0)
        incoming_conf = float(incoming.get("confidence") or 0)

        if incoming_conf > existing_conf:
            merged["confidence"] = incoming.get("confidence")
            merged["match_method"] = incoming.get("match_method")
            merged["matched_prolog_source"] = incoming.get("matched_prolog_source")
            merged["is_known_in_prolog"] = incoming.get("is_known_in_prolog")
    except (TypeError, ValueError):
        pass

    return merged


def update_enriched_bank(
    records: List[Dict[str, Any]],
    enriched_bank_path: Path,
) -> Dict[str, Dict[str, Any]]:
    bank = load_json(enriched_bank_path, default={})

    if not isinstance(bank, dict):
        raise RuntimeError(f"Expected JSON object in {enriched_bank_path}")

    for record in records:
        plant_atom = record["plant_atom"]
        bank[plant_atom] = merge_record(bank.get(plant_atom), record)

    save_json(enriched_bank_path, bank)
    return bank


def update_missing_seed(
    records: List[Dict[str, Any]],
    missing_seed_path: Path,
) -> List[Dict[str, Any]]:
    existing_seed = load_json(missing_seed_path, default=[])

    if not isinstance(existing_seed, list):
        raise RuntimeError(f"Expected JSON list in {missing_seed_path}")

    by_key: Dict[str, Dict[str, Any]] = {}

    for item in existing_seed:
        if not isinstance(item, dict):
            continue

        key = normalize_scientific_name(item.get("scientific_name")) or normalize_key(item.get("plant_atom")) or normalize_key(item.get("common_name"))

        if key:
            by_key[key] = item

    for record in records:
        if record.get("is_known_in_prolog") is True:
            continue

        key = normalize_scientific_name(record.get("scientific_name")) or normalize_key(record.get("plant_atom")) or normalize_key(record.get("common_name"))

        if not key:
            continue

        seed_item = {
            "plant_atom": record.get("plant_atom"),
            "common_name": record.get("common_name"),
            "scientific_name": record.get("scientific_name"),
            "genus": record.get("genus"),
            "source_name": "perenual_snapshot",
            "source_file": record.get("source_file"),
            "reason": "scientific_name_not_found_in_prolog",
            "confidence": record.get("confidence"),
            "status": "pending_extraction",
            "created_at": now_iso(),
        }

        if key in by_key:
            by_key[key] = merge_record(by_key[key], seed_item)
        else:
            by_key[key] = seed_item

    result = sorted(
        by_key.values(),
        key=lambda item: (
            str(item.get("genus") or ""),
            str(item.get("common_name") or ""),
            str(item.get("scientific_name") or ""),
        ),
    )

    save_json(missing_seed_path, result)
    return result


# =========================================================
# NORMALIZED PROFILE MERGE
# =========================================================


def watering_interval_days(record: Dict[str, Any]) -> Optional[int]:
    benchmark = record.get("watering_general_benchmark")

    if not isinstance(benchmark, dict):
        return None

    value = clean_text(benchmark.get("value"))

    if not value:
        return None

    numbers = [int(match) for match in re.findall(r"\d+", value)]

    if not numbers:
        return None

    return max(1, round(sum(numbers) / len(numbers)))


def perenual_profile_source(record: Dict[str, Any]) -> Dict[str, Any]:
    source_file = record.get("source_file")
    source_url = None

    if record.get("perenual_id"):
        source_url = f"https://perenual.com/plant-species-database-search-finder/species/{record['perenual_id']}"

    return {
        "source_name": "Perenual",
        "source_url": source_url or source_file,
        "status": "snapshot",
        "trusted_detail": True,
        "relevance_score": None,
        "fields_provided": [
            key
            for key in [
                "identity",
                "classification.life_cycle",
                "growth.sunlight",
                "growth.water_need",
                "growth.growth_speed",
                "germination.propagation_methods",
                "care.watering_interval_days",
            ]
            if key
        ],
        "confidence": record.get("confidence") or 0.70,
        "last_verified_at": record.get("last_synced_at") or now_iso(),
    }


def add_profile_source(profile: Dict[str, Any], source: Dict[str, Any]) -> bool:
    metadata = profile.setdefault("source_metadata", {})
    sources = metadata.setdefault("sources", [])

    if not isinstance(sources, list):
        metadata["sources"] = []
        sources = metadata["sources"]

    marker = (source.get("source_name"), source.get("source_url"))

    for existing in sources:
        if not isinstance(existing, dict):
            continue

        if (existing.get("source_name"), existing.get("source_url")) == marker:
            existing.update(source)
            return True

    sources.append(source)
    return True


def compute_profile_missing_fields(profile: Dict[str, Any]) -> None:
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
    ]

    missing = []

    for path in required_paths:
        if get_path(profile, path) in (None, "", [], {}):
            missing.append(path)

    known_diseases = get_path(profile, "pests_and_diseases.known_diseases")
    known_disease_ids = get_path(profile, "pests_and_diseases.known_disease_ids")

    if known_diseases in (None, "", [], {}) and known_disease_ids in (None, "", [], {}):
        missing.append("pests_and_diseases.known_diseases")

    profile["missing_fields"] = missing


def merge_record_into_profile(profile: Dict[str, Any], record: Dict[str, Any]) -> bool:
    changed = False
    previous_missing_fields = list(profile.get("missing_fields") or [])

    changed |= set_path_if_blank(profile, "identity.common_name", record.get("common_name"), "Perenual")
    changed |= set_path_if_blank(profile, "identity.scientific_name", record.get("scientific_name"), "Perenual")
    changed |= set_path_if_blank(profile, "identity.genus", record.get("genus"), "Perenual")
    changed |= set_path_if_blank(profile, "identity.family", record.get("family"), "Perenual")

    changed |= set_path_if_blank(profile, "classification.life_cycle", record.get("cycle"), "Perenual")
    changed |= set_path_if_blank(profile, "classification.edible", record.get("cuisine"), "Perenual")

    edible_parts = []
    if record.get("edible_fruit") is True:
        edible_parts.append("fruit")
    if record.get("edible_leaf") is True:
        edible_parts.append("leaf")

    changed |= extend_path_list(profile, "classification.edible_parts", edible_parts, "Perenual")
    changed |= extend_path_list(profile, "growth.sunlight", record.get("sunlight") or [], "Perenual")
    changed |= extend_path_list(profile, "growth.soil_type", record.get("soil") or [], "Perenual")
    changed |= set_path_if_blank(profile, "growth.water_need", record.get("watering"), "Perenual")
    changed |= set_path_if_blank(profile, "growth.growth_speed", record.get("growth_rate"), "Perenual")
    changed |= extend_path_list(profile, "germination.propagation_methods", record.get("propagation") or [], "Perenual")
    changed |= set_path_if_blank(profile, "care.watering_interval_days", watering_interval_days(record), "Perenual")
    changed |= set_path_if_blank(profile, "care.cultivation_notes", record.get("description"), "Perenual")

    compute_profile_missing_fields(profile)

    if profile.get("missing_fields") != previous_missing_fields:
        changed = True

    if changed:
        add_profile_source(profile, perenual_profile_source(record))
        profile.setdefault("source_metadata", {})["last_merged_at"] = now_iso()

    return changed


def update_normalized_profiles(
    records: List[Dict[str, Any]],
    normalized_dir: Path,
) -> List[Path]:
    updated_paths: List[Path] = []

    for record in records:
        plant_atom = record.get("plant_atom")

        if not plant_atom:
            continue

        profile_path = normalized_dir / f"{plant_atom}.json"
        profile = read_json(profile_path, default=None)

        if not isinstance(profile, dict):
            continue

        if merge_record_into_profile(profile, record):
            write_json(profile_path, profile)
            updated_paths.append(profile_path)

    return updated_paths


def matched_normalized_profiles(records: List[Dict[str, Any]], normalized_dir: Path) -> List[Path]:
    matched_paths: List[Path] = []
    seen = set()

    for record in records:
        plant_atom = record.get("plant_atom")

        if not plant_atom:
            continue

        profile_path = normalized_dir / f"{plant_atom}.json"

        if profile_path.exists() and profile_path not in seen:
            seen.add(profile_path)
            matched_paths.append(profile_path)

    return matched_paths


# =========================================================
# SCANNING
# =========================================================


def find_snapshot_files(snapshot_dir: Path) -> List[Path]:
    if not snapshot_dir.exists():
        raise RuntimeError(f"Snapshot directory does not exist: {snapshot_dir}")

    return sorted(snapshot_dir.rglob("*.json"))


def extract_records_from_snapshots(
    snapshot_dir: Path,
    prolog_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    for file_path in find_snapshot_files(snapshot_dir):
        try:
            raw = load_json(file_path, default=None)
        except RuntimeError as exc:
            print(f"[SKIP] {exc}")
            continue

        items = unwrap_perenual_payload(raw)

        if not items:
            print(f"[SKIP] No recognizable plant payload: {file_path}")
            continue

        for item in items:
            record = normalize_snapshot_record(item, file_path, prolog_index)

            if record:
                records.append(record)

    return records


# =========================================================
# REPORTING
# =========================================================


def print_summary(
    records: List[Dict[str, Any]],
    bank: Dict[str, Any],
    missing_seed: List[Dict[str, Any]],
    matched_profiles: List[Path],
    updated_profiles: List[Path],
) -> None:
    known = [r for r in records if r.get("is_known_in_prolog") is True]
    missing = [r for r in records if r.get("is_known_in_prolog") is False]

    print("")
    print("========== Perenual Snapshot Enrichment Summary ==========")
    print(f"Snapshot records processed : {len(records)}")
    print(f"Matched existing Prolog    : {len(known)}")
    print(f"New missing candidates     : {len(missing)}")
    print(f"Total enriched bank records: {len(bank)}")
    print(f"Total missing seed records : {len(missing_seed)}")
    print(f"Normalized profiles matched: {len(matched_profiles)}")
    print(f"Normalized profiles updated: {len(updated_profiles)}")
    print("==========================================================")
    print("")

    if missing:
        print("Missing candidates:")
        for item in missing[:30]:
            print(f" - {item.get('plant_atom')} | " f"{item.get('common_name')} | " f"{item.get('scientific_name')} | " f"{item.get('match_method')}")

        if len(missing) > 30:
            print(f" ... and {len(missing) - 30} more")

    if matched_profiles:
        print("")
        print("Matched normalized profiles:")
        for path in matched_profiles[:30]:
            status = "updated" if path in updated_profiles else "already current"
            print(f" - {path.stem} | {status}")

        if len(matched_profiles) > 30:
            print(f" ... and {len(matched_profiles) - 30} more")

    if updated_profiles:
        print("")
        print("Updated normalized profiles:")
        for path in updated_profiles[:30]:
            print(f" - {path.stem}")

        if len(updated_profiles) > 30:
            print(f" ... and {len(updated_profiles) - 30} more")


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich extracted species data from temporary Perenual snapshot JSON files.")

    parser.add_argument(
        "--snapshot-dir",
        default=str(PATHS.species_snapshots),
        help="Directory containing temporary Perenual snapshot JSON files.",
    )

    parser.add_argument(
        "--prolog-root",
        default=str(PATHS.logic_companion),
        help="Root directory containing existing Prolog files.",
    )

    parser.add_argument(
        "--enriched-bank",
        default=str(PATHS.perenual_enriched_species),
        help="Output normalized enriched species data bank.",
    )

    parser.add_argument(
        "--missing-seed",
        default=str(PATHS.missing_plant_seed),
        help="Output seed file for plants not found in Prolog.",
    )

    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Print resolved project paths before running.",
    )

    args = parser.parse_args()

    PATHS.ensure_dirs()

    if args.show_paths:
        PATHS.print_summary()

    snapshot_dir = Path(args.snapshot_dir)
    prolog_root = Path(args.prolog_root)
    enriched_bank_path = Path(args.enriched_bank)
    missing_seed_path = Path(args.missing_seed)

    print(f"[INFO] Snapshot directory : {snapshot_dir}")
    print(f"[INFO] Prolog root        : {prolog_root}")
    print(f"[INFO] Enriched bank      : {enriched_bank_path}")
    print(f"[INFO] Missing seed       : {missing_seed_path}")

    prolog_index = build_prolog_identity_index(prolog_root)

    print(f"[INFO] Prolog atoms       : {len(prolog_index['by_atom'])}")
    print(f"[INFO] Scientific names   : {len(prolog_index['by_scientific'])}")
    print(f"[INFO] Common names       : {len(prolog_index['by_common'])}")

    records = extract_records_from_snapshots(snapshot_dir, prolog_index)

    bank = update_enriched_bank(records, enriched_bank_path)
    missing_seed = update_missing_seed(records, missing_seed_path)
    matched_profiles = matched_normalized_profiles(records, PATHS.normalized_plants)
    updated_profiles = update_normalized_profiles(records, PATHS.normalized_plants)

    print_summary(records, bank, missing_seed, matched_profiles, updated_profiles)

    print(f"[OK] Updated enriched bank: {enriched_bank_path}")
    print(f"[OK] Updated missing seed : {missing_seed_path}")
    print(f"[OK] Updated profiles     : {len(updated_profiles)}")
    print("[INFO] Prolog files were not modified. Run the Prolog update step to append pending facts.")


if __name__ == "__main__":
    main()
