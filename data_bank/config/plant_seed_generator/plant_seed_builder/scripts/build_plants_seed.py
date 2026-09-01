"""
Build plants_seed.json from multiple plant source lists.

Purpose:
- Ingest CSV/JSON/TXT exports from PFAF, FPI, EdiblePlantDB, USDA GRIN, etc.
- Normalize plant identity.
- Remove duplicates.
- Produce a clean config/plants_seed.json file for the data bank pipeline.

This script does NOT scrape websites directly.
It builds the seed list from downloaded/exported/prepared source files.

Usage:
    python scripts/build_plants_seed.py --input-dir input_sources --output config/plants_seed.json

Optional:
    python scripts/build_plants_seed.py --input-dir input_sources --output config/plants_seed.json --min-confidence 0.55
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None


# -----------------------------
# Normalization helpers
# -----------------------------

AUTHOR_ABBREVIATIONS = {
    "l",
    "l.",
    "mill",
    "mill.",
    "lam",
    "lam.",
    "dc",
    "dc.",
    "benth",
    "hook",
    "f",
    "f.",
    "willd",
    "willd.",
    "moench",
    "gaertn",
    "roxb",
    "roxb.",
    "poir",
    "poir.",
}


SYNONYM_SEPARATORS = [";", "|", ","]


COMMON_COLUMN_ALIASES = {
    "scientific_name": [
        "scientific_name",
        "scientific name",
        "latin_name",
        "latin name",
        "botanical_name",
        "botanical name",
        "species",
        "taxon",
        "taxon_name",
        "accepted_name",
        "accepted scientific name",
    ],
    "common_name": [
        "common_name",
        "common name",
        "name",
        "english_name",
        "english name",
        "vernacular_name",
        "vernacular name",
    ],
    "family": ["family", "plant_family"],
    "genus": ["genus"],
    "synonyms": ["synonyms", "synonym", "other_names", "other names"],
    "edible_parts": ["edible_parts", "edible parts", "parts_used", "parts used", "part_used"],
    "uses": ["uses", "use", "food_uses", "food uses", "plant_uses", "plant uses"],
    "category": ["category", "categories", "crop_category", "crop category", "type", "plant_type"],
    "life_cycle": ["life_cycle", "life cycle", "cycle", "duration"],
    "source_url": ["source_url", "url", "link", "reference"],
}


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    value = str(value)
    value = value.replace("\ufeff", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def slugify(value: str | None) -> str:
    value = clean_text(value) or "unknown"
    value = value.lower()
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_") or "unknown"


def title_name(value: str | None) -> str | None:
    value = clean_text(value)
    if not value:
        return None
    # Keep existing capitalization for short names, but normalize obvious lowercase.
    return " ".join(part.capitalize() if part.islower() else part for part in value.split())


def normalize_scientific_name(value: str | None) -> str | None:
    """
    Normalize scientific names lightly.

    Examples:
    - "Solanum lycopersicum L." -> "Solanum lycopersicum"
    - "Mentha spp." stays "Mentha spp."
    """
    value = clean_text(value)
    if not value:
        return None

    value = value.replace("×", "x")
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" .,")

    parts = value.split()
    cleaned = []

    for i, part in enumerate(parts):
        low = part.lower().strip(".,")
        if i >= 2 and low in AUTHOR_ABBREVIATIONS:
            continue
        cleaned.append(part.strip(","))

    if not cleaned:
        return None

    # Capitalize genus only if it looks lowercase.
    if cleaned[0].islower():
        cleaned[0] = cleaned[0].capitalize()

    # Species epithet usually lowercase.
    if len(cleaned) >= 2 and cleaned[1].isalpha():
        cleaned[1] = cleaned[1].lower()

    return " ".join(cleaned).strip()


def genus_from_scientific_name(value: str | None) -> str | None:
    value = normalize_scientific_name(value)
    if not value:
        return None
    first = value.split()[0]
    if first.lower() in ["unknown", "sp", "spp"]:
        return None
    return first


def split_multi_value(value: Any) -> list[str]:
    value = clean_text(value)
    if not value:
        return []

    chosen_sep = None
    for sep in SYNONYM_SEPARATORS:
        if sep in value:
            chosen_sep = sep
            break

    if chosen_sep:
        items = [clean_text(v) for v in value.split(chosen_sep)]
    else:
        items = [value]

    return sorted({v for v in items if v})


def get_value(row: dict[str, Any], canonical_key: str) -> str | None:
    aliases = COMMON_COLUMN_ALIASES[canonical_key]
    lowered = {str(k).strip().lower(): v for k, v in row.items()}

    for alias in aliases:
        if alias.lower() in lowered:
            return clean_text(lowered[alias.lower()])

    return None


def guess_use_categories(text: str | None) -> list[str]:
    text = (text or "").lower()
    categories = []

    rules = {
        "culinary_herb": ["herb", "seasoning", "flavouring", "flavoring", "aromatic leaves"],
        "medicinal_herb": ["medicinal", "medicine", "remedy"],
        "leafy_vegetable": ["leafy", "leaf vegetable", "spinach", "leaves eaten", "young leaves"],
        "fruit_crop": ["fruit", "berry"],
        "root_tuber_crop": ["root", "tuber", "rhizome", "corm"],
        "grain_seed_crop": ["grain", "seed crop", "cereal"],
        "legume_crop": ["legume", "bean", "pea", "pulse"],
        "spice_crop": ["spice", "pepper", "ginger", "turmeric", "cinnamon"],
        "edible_flower": ["edible flower", "flowers eaten"],
        "oil_crop": ["oilseed", "oil seed", "edible oil"],
    }

    for category, needles in rules.items():
        if any(n in text for n in needles):
            categories.append(category)

    return sorted(set(categories))


def guess_edible_parts(text: str | None) -> list[str]:
    text = (text or "").lower()
    parts = []

    rules = {
        "leaf": ["leaf", "leaves", "young leaves"],
        "fruit": ["fruit", "berry", "berries"],
        "seed": ["seed", "seeds", "grain"],
        "flower": ["flower", "flowers"],
        "root": ["root", "roots"],
        "tuber": ["tuber", "tubers"],
        "rhizome": ["rhizome", "rhizomes"],
        "stem": ["stem", "stems", "shoot", "shoots"],
        "bulb": ["bulb", "bulbs"],
        "pod": ["pod", "pods"],
        "sap": ["sap"],
    }

    for part, needles in rules.items():
        if any(n in text for n in needles):
            parts.append(part)

    return sorted(set(parts))


def normalize_life_cycle(value: str | None) -> str | None:
    value = (value or "").lower()
    if "perennial" in value:
        return "perennial"
    if "biennial" in value:
        return "biennial"
    if "annual" in value:
        return "annual"
    return None


# -----------------------------
# File readers
# -----------------------------


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except Exception:
            dialect = csv.excel

        reader = csv.DictReader(f, dialect=dialect)
        return [dict(row) for row in reader]


def flatten_json_records(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]

    if isinstance(data, dict):
        # Common wrapper keys.
        for key in ["data", "results", "plants", "items", "records"]:
            if isinstance(data.get(key), list):
                return [x for x in data[key] if isinstance(x, dict)]

        # Single plant record.
        return [data]

    return []


def read_json_file(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return flatten_json_records(data)


def read_txt(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = clean_text(line)
        if not line or line.startswith("#"):
            continue

        # Allow:
        # Scientific name | Common name | Family
        parts = [clean_text(p) for p in line.split("|")]
        if len(parts) >= 2:
            records.append(
                {
                    "scientific_name": parts[0],
                    "common_name": parts[1],
                    "family": parts[2] if len(parts) >= 3 else None,
                }
            )
        else:
            records.append({"scientific_name": line})

    return records


def read_source_file(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv(path)
    if suffix == ".json":
        return read_json_file(path)
    if suffix in [".txt", ".tsv"]:
        if suffix == ".tsv":
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter="\t")
                return [dict(row) for row in reader]
        return read_txt(path)

    return []


def infer_source_name(path: Path) -> str:
    name = path.stem.lower()
    if "pfaf" in name:
        return "pfaf"
    if "fpi" in name or "food" in name:
        return "food_plants_international"
    if "edible" in name:
        return "edibleplantdb"
    if "grin" in name or "usda" in name:
        return "usda_grin"
    return slugify(path.stem)


# -----------------------------
# Record normalization
# -----------------------------


def normalize_record(raw: dict[str, Any], source_name: str, source_file: str) -> dict[str, Any] | None:
    scientific_name = normalize_scientific_name(get_value(raw, "scientific_name"))
    common_name = title_name(get_value(raw, "common_name"))

    family = title_name(get_value(raw, "family"))
    genus = title_name(get_value(raw, "genus")) or genus_from_scientific_name(scientific_name)

    synonyms = split_multi_value(get_value(raw, "synonyms"))
    edible_parts = split_multi_value(get_value(raw, "edible_parts"))
    uses = get_value(raw, "uses")
    category = get_value(raw, "category")
    life_cycle = normalize_life_cycle(get_value(raw, "life_cycle"))

    source_url = get_value(raw, "source_url")

    # Guess additional categories/parts from uses/category.
    text_for_guess = " ".join(
        [
            uses or "",
            category or "",
            " ".join(edible_parts),
            common_name or "",
        ]
    )

    edible_parts = sorted(set(edible_parts + guess_edible_parts(text_for_guess)))
    use_categories = sorted(set(guess_use_categories(text_for_guess) + split_multi_value(category)))

    # Need at least scientific or common.
    if not scientific_name and not common_name:
        return None

    # Build atom using common name if available, else scientific.
    atom_basis = common_name or scientific_name

    normalized = {
        "plant_atom": slugify(atom_basis),
        "common_name": common_name,
        "scientific_name": scientific_name,
        "genus": genus,
        "family": family,
        "synonyms": sorted(set(synonyms)),
        "source_names": [source_name],
        "source_files": [source_file],
        "source_urls": [source_url] if source_url else [],
        "use_categories": use_categories,
        "edible_parts": edible_parts,
        "life_cycle": life_cycle,
        "confidence": compute_initial_confidence(scientific_name, common_name, family, edible_parts, use_categories),
        "raw_examples": [raw],
    }

    return normalized


def compute_initial_confidence(
    scientific_name: str | None,
    common_name: str | None,
    family: str | None,
    edible_parts: list[str],
    use_categories: list[str],
) -> float:
    score = 0.35
    if scientific_name:
        score += 0.25
    if common_name:
        score += 0.15
    if family:
        score += 0.10
    if edible_parts:
        score += 0.10
    if use_categories:
        score += 0.05
    return min(round(score, 2), 0.95)


# -----------------------------
# Deduplication
# -----------------------------


def dedupe_key(record: dict[str, Any]) -> str:
    sci = normalize_scientific_name(record.get("scientific_name"))
    if sci:
        # Genus species is the strongest identity. Keep spp. at genus level.
        return slugify(sci)

    genus = record.get("genus")
    common = record.get("common_name")
    if genus and common:
        return slugify(f"{genus}_{common}")

    return slugify(common or record.get("plant_atom"))


def maybe_same_record(a: dict[str, Any], b: dict[str, Any], fuzzy_threshold: int = 94) -> bool:
    """
    Secondary fuzzy duplicate check.

    Used when scientific name is missing from one side.
    """
    if not fuzz:
        return False

    a_sci = a.get("scientific_name")
    b_sci = b.get("scientific_name")

    if a_sci and b_sci:
        return slugify(a_sci) == slugify(b_sci)

    a_common = a.get("common_name") or ""
    b_common = b.get("common_name") or ""
    a_genus = (a.get("genus") or "").lower()
    b_genus = (b.get("genus") or "").lower()

    if a_genus and b_genus and a_genus != b_genus:
        return False

    if a_common and b_common:
        return fuzz.token_sort_ratio(a_common, b_common) >= fuzzy_threshold

    return False


def merge_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    base = records[0].copy()

    for rec in records[1:]:
        for key in ["common_name", "scientific_name", "genus", "family", "life_cycle"]:
            if not base.get(key) and rec.get(key):
                base[key] = rec[key]

        for key in ["synonyms", "source_names", "source_files", "source_urls", "use_categories", "edible_parts"]:
            combined = []
            for item in (base.get(key) or []) + (rec.get(key) or []):
                if item and item not in combined:
                    combined.append(item)
            base[key] = combined

        base["confidence"] = max(base.get("confidence", 0), rec.get("confidence", 0))
        base.setdefault("raw_examples", [])
        base["raw_examples"].extend(rec.get("raw_examples", [])[:2])

    # Recompute atom after merge.
    atom_basis = base.get("common_name") or base.get("scientific_name") or base.get("plant_atom")
    base["plant_atom"] = slugify(atom_basis)
    base["duplicate_group_id"] = dedupe_key(base)

    # If scientific name exists, make genus consistent.
    if not base.get("genus") and base.get("scientific_name"):
        base["genus"] = genus_from_scientific_name(base["scientific_name"])

    return base


def deduplicate_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = defaultdict(list)

    for rec in records:
        grouped[dedupe_key(rec)].append(rec)

    merged = [merge_records(group) for group in grouped.values()]

    # Fuzzy pass for records missing scientific names.
    final = []
    used = set()

    for i, rec in enumerate(merged):
        if i in used:
            continue

        group = [rec]
        used.add(i)

        for j in range(i + 1, len(merged)):
            if j in used:
                continue
            if maybe_same_record(rec, merged[j]):
                group.append(merged[j])
                used.add(j)

        final.append(merge_records(group))

    final.sort(key=lambda x: (x.get("plant_atom") or "", x.get("scientific_name") or ""))
    return final


# -----------------------------
# Main
# -----------------------------


def collect_records(input_dir: Path) -> list[dict[str, Any]]:
    all_records = []

    files = []
    for pattern in ["*.csv", "*.json", "*.txt", "*.tsv"]:
        files.extend(input_dir.glob(pattern))

    for path in sorted(files):
        source_name = infer_source_name(path)
        raw_records = read_source_file(path)

        print(f"[READ] {path.name}: {len(raw_records)} raw records as source={source_name}")

        for raw in raw_records:
            normalized = normalize_record(raw, source_name=source_name, source_file=path.name)
            if normalized:
                all_records.append(normalized)

    return all_records


def write_outputs(records: list[dict[str, Any]], output: Path, rejected_output: Path | None = None, min_confidence: float = 0.0) -> None:
    accepted = []
    rejected = []

    for rec in records:
        if rec.get("confidence", 0) >= min_confidence:
            # Remove heavy raw examples from final seed but keep traceability.
            final_rec = {k: v for k, v in rec.items() if k != "raw_examples"}
            accepted.append(final_rec)
        else:
            rejected.append(rec)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(accepted, indent=2, ensure_ascii=False), encoding="utf-8")

    if rejected_output:
        rejected_output.parent.mkdir(parents=True, exist_ok=True)
        rejected_output.write_text(json.dumps(rejected, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[WRITE] accepted: {len(accepted)} -> {output}")
    if rejected_output:
        print(f"[WRITE] rejected: {len(rejected)} -> {rejected_output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, help="Folder containing CSV/JSON/TXT source files")
    parser.add_argument("--output", required=True, help="Output plants_seed.json")
    parser.add_argument("--rejected-output", default="config/plants_seed_rejected.json")
    parser.add_argument("--min-confidence", type=float, default=0.0)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output = Path(args.output)
    rejected_output = Path(args.rejected_output) if args.rejected_output else None

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    records = collect_records(input_dir)
    print(f"[COLLECT] normalized records: {len(records)}")

    deduped = deduplicate_records(records)
    print(f"[DEDUPE] final records: {len(deduped)}")

    write_outputs(
        records=deduped,
        output=output,
        rejected_output=rejected_output,
        min_confidence=args.min_confidence,
    )


if __name__ == "__main__":
    main()
