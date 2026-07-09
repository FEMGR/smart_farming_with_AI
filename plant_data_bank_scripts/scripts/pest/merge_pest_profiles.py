#!/usr/bin/env python3
"""
merge_pest_profiles.py

Merge the two PNW pest profile outputs into one richer normalized pest set.

Default inputs:
    data_bank/normalized/pests
    data_bank/normalized/pests_ver01

Default output:
    data_bank/normalized/pests_merged

Merge policy:
    - Prefer data_bank/normalized/pests for overlapping common pest detail fields
      such as images, included species, scientific names, and common-page metadata.
    - Add host mappings, source pages, detail URLs, monitoring, and management
      coverage from data_bank/normalized/pests_ver01.
    - Keep pests that exist only in pests_ver01.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_paths import PATHS  # noqa: E402


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def is_nonempty(value: Any) -> bool:
    return value not in (None, "", [], {})


def text_size(value: Any) -> int:
    if isinstance(value, str):
        return len(value.strip())
    if isinstance(value, list):
        return sum(text_size(item) for item in value)
    if isinstance(value, dict):
        return sum(text_size(item) for item in value.values())
    return 0


def item_key(item: Any) -> str:
    return json.dumps(item, sort_keys=True, ensure_ascii=False) if isinstance(item, dict) else clean_text(item).lower()


def merge_list(*values: Any) -> list[Any]:
    merged = []
    seen = set()

    for value in values:
        if not isinstance(value, list):
            continue

        for item in value:
            if item in (None, "", [], {}):
                continue

            key = item_key(item)
            if key in seen:
                continue

            seen.add(key)
            merged.append(item)

    try:
        return sorted(merged)
    except TypeError:
        return merged


def choose_scalar(primary: Any, secondary: Any, prefer_longer: bool = False) -> Any:
    if not is_nonempty(primary):
        return secondary

    if not is_nonempty(secondary):
        return primary

    if prefer_longer and text_size(secondary) > text_size(primary):
        return secondary

    return primary


def merge_management(primary: Any, secondary: Any) -> dict[str, Any]:
    primary = primary if isinstance(primary, dict) else {}
    secondary = secondary if isinstance(secondary, dict) else {}
    keys = sorted(set(primary) | set(secondary))
    merged: dict[str, Any] = {}

    for key in keys:
        left = primary.get(key)
        right = secondary.get(key)

        if isinstance(left, list) or isinstance(right, list):
            merged[key] = merge_list(
                left if isinstance(left, list) else [left] if is_nonempty(left) else [],
                right if isinstance(right, list) else [right] if is_nonempty(right) else [],
            )
            continue

        merged[key] = choose_scalar(left, right, prefer_longer=True)

    return merged


def load_profiles(directory: Path) -> dict[str, dict[str, Any]]:
    profiles: dict[str, dict[str, Any]] = {}

    if not directory.exists():
        raise FileNotFoundError(f"Pest profile directory not found: {directory}")

    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            print(f"[SKIP] JSON root is not an object: {path}")
            continue

        pest_atom = data.get("pest_atom") or path.stem
        data["pest_atom"] = pest_atom
        profiles[pest_atom] = data

    return profiles


def merge_profile(pest_atom: str, primary: dict[str, Any] | None, secondary: dict[str, Any] | None) -> dict[str, Any]:
    if primary is None and secondary is None:
        raise ValueError(f"No profile data for {pest_atom}")

    primary = primary or {}
    secondary = secondary or {}

    merged = dict(primary or secondary)
    merged["pest_atom"] = pest_atom
    merged["name"] = choose_scalar(primary.get("name"), secondary.get("name")) or pest_atom.replace("_", " ").title()
    merged["pest_type"] = choose_scalar(primary.get("pest_type"), secondary.get("pest_type")) or "insect"
    merged["source_name"] = choose_scalar(primary.get("source_name"), secondary.get("source_name"))
    merged["source_section"] = choose_scalar(primary.get("source_section"), secondary.get("source_section"))
    merged["source_index_url"] = choose_scalar(primary.get("source_index_url"), secondary.get("source_index_url"))
    merged["confidence"] = max(primary.get("confidence") or 0, secondary.get("confidence") or 0) or None

    # Identity/detail fields. Prefer common pest detail page values, then enrich with host-index values.
    merged["scientific_names"] = merge_list(primary.get("scientific_names"), secondary.get("scientific_names"))
    merged["primary_scientific_name"] = choose_scalar(
        primary.get("primary_scientific_name"),
        secondary.get("primary_scientific_name"),
    )
    merged["included_species"] = merge_list(primary.get("included_species"), secondary.get("included_species"))
    merged["images"] = merge_list(primary.get("images"), secondary.get("images"))
    merged["meta_dates"] = choose_scalar(primary.get("meta_dates"), secondary.get("meta_dates"))

    # Interaction/source coverage. pests_ver01 is the stronger source for host relationships.
    merged["host_plants"] = merge_list(primary.get("host_plants"), secondary.get("host_plants"))
    merged["source_pages"] = merge_list(primary.get("source_pages"), secondary.get("source_pages"))
    merged["detail_urls"] = merge_list(primary.get("detail_urls"), secondary.get("detail_urls"))
    merged["page_titles"] = merge_list(primary.get("page_titles"), secondary.get("page_titles"))

    # Narrative fields. Use longer text when both exist, because host-index pages often contain management text.
    merged["description_damage"] = choose_scalar(
        primary.get("description_damage"),
        secondary.get("description_damage"),
        prefer_longer=True,
    )
    merged["biology_life_history"] = choose_scalar(
        primary.get("biology_life_history"),
        secondary.get("biology_life_history"),
        prefer_longer=True,
    )
    merged["monitoring"] = choose_scalar(primary.get("monitoring"), secondary.get("monitoring"), prefer_longer=True)
    merged["management"] = merge_management(primary.get("management"), secondary.get("management"))
    merged["damage_tags"] = merge_list(primary.get("damage_tags"), secondary.get("damage_tags"))
    merged["raw_section_keys"] = merge_list(primary.get("raw_section_keys"), secondary.get("raw_section_keys"))

    if primary.get("source_url") or secondary.get("source_url"):
        merged["source_url"] = choose_scalar(primary.get("source_url"), secondary.get("source_url"))

    merged["data_origin"] = "merged_pnw_pest_profile"
    merged["merged_from"] = {
        "pests": bool(primary),
        "pests_ver01": bool(secondary),
    }
    merged["merged_at"] = datetime.now(timezone.utc).isoformat()

    return merged


def write_profiles(profiles: dict[str, dict[str, Any]], output_dir: Path, clean_output: bool) -> None:
    if clean_output and output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    for pest_atom, profile in sorted(profiles.items()):
        path = output_dir / f"{pest_atom}.json"
        path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")


def print_summary(
    primary_profiles: dict[str, dict[str, Any]],
    secondary_profiles: dict[str, dict[str, Any]],
    merged_profiles: dict[str, dict[str, Any]],
    output_dir: Path,
    dry_run: bool,
) -> None:
    primary_ids = set(primary_profiles)
    secondary_ids = set(secondary_profiles)
    merged_ids = set(merged_profiles)

    attack_count = sum(len(profile.get("host_plants") or []) for profile in merged_profiles.values())
    scientific_count = len({sci for profile in merged_profiles.values() for sci in profile.get("scientific_names") or []})
    image_count = sum(len(profile.get("images") or []) for profile in merged_profiles.values())

    print("")
    print("========== MERGED PEST PROFILE SUMMARY ==========")
    print(f"Primary pests dir count   : {len(primary_profiles)}")
    print(f"Secondary ver01 dir count : {len(secondary_profiles)}")
    print(f"Overlapping pests         : {len(primary_ids & secondary_ids)}")
    print(f"Primary-only pests        : {len(primary_ids - secondary_ids)}")
    print(f"Ver01-only pests          : {len(secondary_ids - primary_ids)}")
    print(f"Merged pest count         : {len(merged_ids)}")
    print(f"Merged attack facts       : {attack_count}")
    print(f"Merged scientific names   : {scientific_count}")
    print(f"Merged image records      : {image_count}")
    print(f"Output dir                : {output_dir}")
    print(f"Dry run                   : {dry_run}")
    print("=================================================")

    if primary_ids - secondary_ids:
        print(f"Primary-only: {', '.join(sorted(primary_ids - secondary_ids))}")

    if secondary_ids - primary_ids:
        print(f"Ver01-only: {', '.join(sorted(secondary_ids - primary_ids))}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge normalized PNW pest profile directories.")

    parser.add_argument(
        "--primary-dir",
        default=str(PATHS.data_bank_normalized / "pests"),
        help="Primary pest profile directory. Defaults to normalized/pests.",
    )
    parser.add_argument(
        "--secondary-dir",
        default=str(PATHS.data_bank_normalized / "pests_ver01"),
        help="Secondary pest profile directory. Defaults to normalized/pests_ver01.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PATHS.data_bank_normalized / "pests_merged"),
        help="Merged output directory. Defaults to normalized/pests_merged.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show merge summary without writing output files.",
    )
    parser.add_argument(
        "--clean-output",
        action="store_true",
        help="Delete the output directory before writing merged profiles.",
    )

    args = parser.parse_args()

    primary_dir = Path(args.primary_dir)
    secondary_dir = Path(args.secondary_dir)
    output_dir = Path(args.output_dir)

    primary_profiles = load_profiles(primary_dir)
    secondary_profiles = load_profiles(secondary_dir)

    merged_profiles = {
        pest_atom: merge_profile(
            pest_atom,
            primary_profiles.get(pest_atom),
            secondary_profiles.get(pest_atom),
        )
        for pest_atom in sorted(set(primary_profiles) | set(secondary_profiles))
    }

    print_summary(
        primary_profiles=primary_profiles,
        secondary_profiles=secondary_profiles,
        merged_profiles=merged_profiles,
        output_dir=output_dir,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("[DRY-RUN] No merged profiles written.")
        return

    write_profiles(merged_profiles, output_dir=output_dir, clean_output=args.clean_output)
    print(f"[OK] Wrote {len(merged_profiles)} merged pest profiles to {output_dir}")


if __name__ == "__main__":
    main()
