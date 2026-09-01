#!/usr/bin/env python3

"""
convert_pfaf_to_plant_seed.py

Converts PFAF crawler output into an app-ready plants_seed.json file.

Input:
    output/pfaf_edible_plants.json

Output:
    config/plants_seed.json

Why this exists:
    The PFAF crawler output is a source extraction file.
    plant_seed.json should be cleaner and shaped for your Smart Farming app.

Example input item:
    {
      "scientific_name": "Abelmoschus esculentus",
      "url": "https://pfaf.org/user/Plant.aspx?LatinName=Abelmoschus+esculentus",
      "categories": ["Flowers", "Fruit", "Leaves", "Oil", "Seed"],
      "source": "PFAF",
      "source_page": "https://pfaf.org/user/Search_Use.aspx?glossary=Fruit"
    }

Example output item:
    {
      "plant_atom": "abelmoschus_esculentus",
      "name": "Abelmoschus esculentus",
      "common_name": null,
      "scientific_name": "Abelmoschus esculentus",
      "genus": "Abelmoschus",
      "is_edible": true,
      "is_medicinal": null,
      "edible_uses": ["Flowers", "Fruit", "Leaves", "Oil", "Seed"],
      "source_name": "PFAF",
      "source_url": "https://pfaf.org/user/Plant.aspx?LatinName=Abelmoschus+esculentus",
      "source_page": "https://pfaf.org/user/Search_Use.aspx?glossary=Fruit"
    }

Install:
    No external dependencies needed.

Run:
    python3 scripts/convert_pfaf_to_plant_seed.py

Optional:
    python3 scripts/convert_pfaf_to_plant_seed.py \
      --input output/pfaf_edible_plants.json \
      --output config/plants_seed.json

Merge with existing:
    python3 scripts/convert_pfaf_to_plant_seed.py \
      --input output/pfaf_edible_plants.json \
      --output config/plants_seed.json \
      --merge-existing
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_INPUT = Path("output/pfaf_edible_plants.json")
DEFAULT_OUTPUT = Path("output/config/plants_seed.json")


def normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)

    return text or None


def make_plant_atom(scientific_name: str) -> str:
    """
    Converts:
        "Abelmoschus esculentus"
    into:
        "abelmoschus_esculentus"

    Keeps it Prolog/Python-friendly.
    """
    value = scientific_name.lower().strip()

    # Remove characters that are not letters, numbers, spaces, hyphens, or underscores.
    value = re.sub(r"[^a-z0-9\s_-]", "", value)

    # Convert spaces and hyphens to underscores.
    value = re.sub(r"[\s-]+", "_", value)

    # Remove repeated underscores.
    value = re.sub(r"_+", "_", value)

    return value.strip("_")


def extract_genus(scientific_name: Optional[str]) -> Optional[str]:
    if not scientific_name:
        return None

    parts = scientific_name.split()
    if not parts:
        return None

    return parts[0]


def clean_categories(categories: Any) -> List[str]:
    if not isinstance(categories, list):
        return []

    cleaned = []

    for item in categories:
        text = normalize_text(item)
        if text:
            cleaned.append(text)

    return sorted(set(cleaned), key=str.lower)


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def normalize_existing_seed_key(item: Dict[str, Any]) -> Optional[str]:
    """
    Used for merging.

    Prefer scientific_name, then plant_atom, then name.
    """
    scientific_name = normalize_text(item.get("scientific_name"))
    if scientific_name:
        return scientific_name.lower()

    plant_atom = normalize_text(item.get("plant_atom"))
    if plant_atom:
        return plant_atom.lower()

    name = normalize_text(item.get("name"))
    if name:
        return name.lower()

    return None


def convert_pfaf_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    scientific_name = normalize_text(item.get("scientific_name"))

    if not scientific_name:
        return None

    categories = clean_categories(item.get("categories"))
    source_url = normalize_text(item.get("url"))
    source_page = normalize_text(item.get("source_page"))

    plant_atom = make_plant_atom(scientific_name)
    genus = extract_genus(scientific_name)

    common_name = normalize_text(item.get("common_name"))

    edibility_rating = item.get("edibility_rating")
    medicinal_rating = item.get("medicinal_rating")

    is_medicinal = None
    if isinstance(medicinal_rating, int):
        is_medicinal = medicinal_rating > 0

    display_name = common_name or scientific_name

    return {
        "plant_atom": plant_atom,
        # Use common name as user-facing name when available.
        "name": display_name,
        "common_name": common_name,
        "scientific_name": scientific_name,
        "genus": genus,
        # Classification flags
        "is_edible": True,
        "is_medicinal": is_medicinal,
        # Ratings from PFAF category table
        "edibility_rating": edibility_rating,
        "medicinal_rating": medicinal_rating,
        # PFAF edible-use categories
        "edible_uses": categories,
        # Source tracking
        "source_name": "PFAF",
        "source_url": source_url,
        "source_page": source_page,
        # Useful for later pipeline logic
        "data_origin": "pfaf_edible_uses_crawler",
    }


def merge_seed_data(
    existing_items: List[Dict[str, Any]],
    new_items: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], int, int]:
    """
    Merges by scientific_name.

    Existing items are preserved.
    New PFAF items are added only if not already present.

    Returns:
        merged_items, added_count, skipped_count
    """
    merged: List[Dict[str, Any]] = []
    seen_keys = set()

    for item in existing_items:
        key = normalize_existing_seed_key(item)
        if not key:
            continue

        merged.append(item)
        seen_keys.add(key)

    added_count = 0
    skipped_count = 0

    for item in new_items:
        key = normalize_existing_seed_key(item)
        if not key:
            skipped_count += 1
            continue

        if key in seen_keys:
            skipped_count += 1
            continue

        merged.append(item)
        seen_keys.add(key)
        added_count += 1

    merged = sorted(
        merged,
        key=lambda x: str(x.get("scientific_name") or x.get("name") or "").lower(),
    )

    return merged, added_count, skipped_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert PFAF edible plant JSON into plants_seed.json.")

    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Path to pfaf_edible_plants.json",
    )

    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path to generated plants_seed.json",
    )

    parser.add_argument(
        "--merge-existing",
        action="store_true",
        help="Merge with existing output file instead of replacing it.",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    raw_data = load_json(input_path)

    if not isinstance(raw_data, list):
        raise ValueError("Expected input JSON to be a list of plant records.")

    converted_items: List[Dict[str, Any]] = []
    invalid_count = 0

    for item in raw_data:
        if not isinstance(item, dict):
            invalid_count += 1
            continue

        converted = convert_pfaf_item(item)

        if not converted:
            invalid_count += 1
            continue

        converted_items.append(converted)

    # Deduplicate converted items before writing.
    unique_converted: Dict[str, Dict[str, Any]] = {}

    for item in converted_items:
        key = normalize_existing_seed_key(item)
        if key:
            unique_converted[key] = item

    new_items = sorted(
        unique_converted.values(),
        key=lambda x: str(x.get("scientific_name") or "").lower(),
    )

    if args.merge_existing and output_path.exists():
        existing_data = load_json(output_path)

        if not isinstance(existing_data, list):
            raise ValueError("Existing plant seed file must be a JSON list.")

        final_items, added_count, skipped_count = merge_seed_data(
            existing_items=existing_data,
            new_items=new_items,
        )

        save_json(output_path, final_items)

        print("DONE")
        print(f"Input PFAF records: {len(raw_data)}")
        print(f"Valid converted records: {len(new_items)}")
        print(f"Invalid skipped records: {invalid_count}")
        print(f"Existing records: {len(existing_data)}")
        print(f"Added new records: {added_count}")
        print(f"Skipped duplicates: {skipped_count}")
        print(f"Final plants_seed records: {len(final_items)}")
        print(f"Output: {output_path}")

    else:
        save_json(output_path, new_items)

        print("DONE")
        print(f"Input PFAF records: {len(raw_data)}")
        print(f"Valid converted records: {len(new_items)}")
        print(f"Invalid skipped records: {invalid_count}")
        print(f"Final plants_seed records: {len(new_items)}")
        print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
