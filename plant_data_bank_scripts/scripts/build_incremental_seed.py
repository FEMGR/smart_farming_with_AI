from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from common import load_plants, plant_filename
from project_paths import PATHS

IMPORTANT_FIELDS = {
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
}

SOURCE_FIELD_COVERAGE = {
    "gbif": {
        "identity.scientific_name",
        "identity.genus",
        "identity.family",
    },
    "pfaf": {
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
    },
    "perenual": {
        "identity.scientific_name",
        "classification.life_cycle",
        "growth.sunlight",
        "growth.water_need",
        "germination.propagation_methods",
    },
    # FPI is currently snapshot-only in merge_profiles.py, so it should not
    # trigger incremental extraction for any missing normalized field.
    "fpi": set(),
}

SOURCE_NAME_KEYS = {
    "gbif": "gbif",
    "plants for a future": "pfaf",
    "pfaf": "pfaf",
    "perenual": "perenual",
    "food plants international": "fpi",
    "fpi": "fpi",
}


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def parse_csv(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(",") if item.strip()}


def parse_iso_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def selected_field_coverage(source_keys: set[str]) -> set[str]:
    fields: set[str] = set()

    for source_key in source_keys:
        fields.update(SOURCE_FIELD_COVERAGE.get(source_key, set()))

    return fields


def normalized_source_key(source_name: Any) -> str | None:
    return SOURCE_NAME_KEYS.get(str(source_name or "").strip().lower())


def latest_source_verified_at_by_key(profile: dict[str, Any], source_keys: set[str]) -> dict[str, datetime]:
    latest_by_key: dict[str, datetime] = {}

    for source in (profile.get("source_metadata") or {}).get("sources") or []:
        if not isinstance(source, dict):
            continue

        source_key = normalized_source_key(source.get("source_name"))
        if source_key not in source_keys:
            continue

        verified_at = parse_iso_datetime(source.get("last_verified_at"))
        if verified_at and (source_key not in latest_by_key or verified_at > latest_by_key[source_key]):
            latest_by_key[source_key] = verified_at

    return latest_by_key


def latest_source_verified_at(profile: dict[str, Any], source_keys: set[str]) -> datetime | None:
    latest_by_key = latest_source_verified_at_by_key(profile, source_keys)

    if not latest_by_key:
        return None

    return max(latest_by_key.values())


def is_stale(profile: dict[str, Any], source_keys: set[str], cutoff: datetime) -> bool:
    last_merged_at = parse_iso_datetime((profile.get("source_metadata") or {}).get("last_merged_at"))
    latest_verified_at = latest_source_verified_at(profile, source_keys)

    if last_merged_at and last_merged_at < cutoff:
        return True

    if latest_verified_at and latest_verified_at < cutoff:
        return True

    return False


def missing_fields_fillable_by_selected_sources(
    profile: dict[str, Any],
    important_fields: set[str],
    fillable_fields: set[str],
) -> list[str]:
    missing_fields = profile.get("missing_fields") or []

    if not isinstance(missing_fields, list):
        return []

    return sorted({str(field) for field in missing_fields if field in important_fields and field in fillable_fields})


def missing_fields_need_refresh(
    profile: dict[str, Any],
    missing_fields: list[str],
    source_keys: set[str],
    cutoff: datetime,
) -> bool:
    last_merged_at = parse_iso_datetime((profile.get("source_metadata") or {}).get("last_merged_at"))

    if last_merged_at and last_merged_at < cutoff:
        return True

    latest_by_key = latest_source_verified_at_by_key(profile, source_keys)

    for field in missing_fields:
        relevant_sources = {source_key for source_key in source_keys if field in SOURCE_FIELD_COVERAGE.get(source_key, set())}

        for source_key in relevant_sources:
            verified_at = latest_by_key.get(source_key)

            if verified_at is None or verified_at < cutoff:
                return True

    return False


def build_incremental_seed(
    plants: list[dict[str, Any]],
    source_keys: set[str],
    important_fields: set[str],
    stale_days: int,
    include_stale_complete: bool,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=stale_days)
    fillable_fields = selected_field_coverage(source_keys)
    selected: list[dict[str, Any]] = []
    counts = {
        "no_profile": 0,
        "missing_fillable_fields": 0,
        "recent_missing_fields": 0,
        "stale_complete": 0,
        "skipped": 0,
    }

    for plant in plants:
        if not isinstance(plant, dict):
            counts["skipped"] += 1
            continue

        profile_path = PATHS.normalized_plants / plant_filename(plant)
        profile = read_json(profile_path, default=None)
        reasons: list[str] = []

        if not isinstance(profile, dict):
            reasons.append("no_normalized_profile")
            counts["no_profile"] += 1
        else:
            fillable_missing = missing_fields_fillable_by_selected_sources(
                profile=profile,
                important_fields=important_fields,
                fillable_fields=fillable_fields,
            )

            if fillable_missing:
                if missing_fields_need_refresh(profile, fillable_missing, source_keys, cutoff):
                    reasons.append("missing_fields=" + ",".join(fillable_missing))
                    counts["missing_fillable_fields"] += 1
                else:
                    counts["recent_missing_fields"] += 1
            elif include_stale_complete and is_stale(profile, source_keys, cutoff):
                reasons.append(f"stale_complete_over_{stale_days}_days")
                counts["stale_complete"] += 1

        if reasons:
            item = dict(plant)
            item["incremental_reasons"] = reasons
            selected.append(item)
        else:
            counts["skipped"] += 1

    return selected, counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a runtime seed containing only plants that need incremental extraction.")
    parser.add_argument("--plants", default=str(PATHS.plants_seed), help="Source plants_seed.json path.")
    parser.add_argument(
        "--output",
        default=str(PATHS.plants_seed_incremental_runtime),
        help="Output runtime seed JSON path.",
    )
    parser.add_argument(
        "--sources",
        default="gbif,pfaf,fpi",
        help="Comma-separated extractors that will run. Supported: gbif,pfaf,fpi,perenual.",
    )
    parser.add_argument(
        "--important-fields",
        default=",".join(sorted(IMPORTANT_FIELDS)),
        help="Comma-separated missing_fields that are important enough to trigger extraction.",
    )
    parser.add_argument("--stale-days", type=int, default=30, help="Freshness threshold in days.")
    parser.add_argument(
        "--include-stale-complete",
        action="store_true",
        help="Also include complete profiles whose merge/source metadata is older than stale-days.",
    )
    args = parser.parse_args()

    if args.stale_days <= 0:
        raise ValueError("--stale-days must be positive.")

    source_keys = parse_csv(args.sources)
    unknown_sources = source_keys - set(SOURCE_FIELD_COVERAGE)
    if unknown_sources:
        raise ValueError(f"Unknown sources: {', '.join(sorted(unknown_sources))}")

    important_fields = parse_csv(args.important_fields)
    plants = load_plants(Path(args.plants))
    selected, counts = build_incremental_seed(
        plants=plants,
        source_keys=source_keys,
        important_fields=important_fields,
        stale_days=args.stale_days,
        include_stale_complete=args.include_stale_complete,
    )

    output_path = Path(args.output)
    write_json(output_path, selected)

    print("[OK] Built incremental runtime seed")
    print(f"Source seed records        : {len(plants)}")
    print(f"Runtime seed records       : {len(selected)}")
    print(f"No normalized profile      : {counts['no_profile']}")
    print(f"Missing fields to refresh  : {counts['missing_fillable_fields']}")
    print(f"Recent missing fields      : {counts['recent_missing_fields']}")
    print(f"Stale complete profiles    : {counts['stale_complete']}")
    print(f"Skipped records            : {counts['skipped']}")
    print(f"Selected extractors        : {', '.join(sorted(source_keys))}")
    print(f"Output                     : {output_path}")


if __name__ == "__main__":
    main()
