#!/usr/bin/env python3
"""
extract_disease_bank.py

Extracts disease-to-plant mappings from UC IPM disease index pages.

This script extracts ALL table rows from pages like:

    https://ipm.ucanr.edu/PMG/diseases/diseases.vegies.html

It creates:

1. data_bank/raw_sources/uc_ipm_disease_rows.json
   - raw extracted row-level disease records

2. data_bank/manual_sources/disease_seed.json
   - normalized seed records with plants_affected

3. data_bank/normalized/disease_bank.json
   - merged central disease bank

Design:
- Plant profiles should store only known_disease_ids.
- Disease details stay in disease_bank.json / Prolog.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_paths import PATHS  # noqa: E402

# =========================================================
# BASIC HELPERS
# =========================================================


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

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


def dedupe_atoms(items: Iterable[Any]) -> List[str]:
    seen = set()
    result: List[str] = []

    for item in items:
        atom = to_snake(item)

        if not atom:
            continue

        if atom not in seen:
            seen.add(atom)
            result.append(atom)

    return result


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


def read_html_from_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def fetch_html(url: str, timeout: int = 25, sleep_seconds: float = 0.5) -> str:
    time.sleep(sleep_seconds)

    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "SmartFarmingDiseaseBankExtractor/1.0"},
    )
    response.raise_for_status()

    return response.text


# =========================================================
# HOST NORMALIZATION
# =========================================================

PLANT_NAME_ALIASES = {
    "beans": "bean",
    "black_eyed_pea": "black_eyed_pea",
    "brussel_sprouts": "brussels_sprout",
    "brussels_sprouts": "brussels_sprout",
    "cantaloupes": "cantaloupe",
    "cucumbers": "cucumber",
    "eggplants": "eggplant",
    "melons": "melon",
    "onions": "onion",
    "peppers": "pepper",
    "potatoes": "potato",
    "pumpkins": "pumpkin",
    "squashes": "squash",
    "tomatoes": "tomato",
    "watermelons": "watermelon",
}


HOST_GROUP_EXPANSIONS = {
    # These are group names from the UC IPM table.
    # We keep both:
    # - plant_groups_affected
    # - expanded plants_affected
    "cole_crops": {
        "group": "cole_crop",
        "plants": [
            "cabbage",
            "broccoli",
            "cauliflower",
            "kale",
            "brussels_sprout",
            "bok_choy",
            "turnip",
            "radish",
        ],
    },
    "cucurbits": {
        "group": "cucurbit",
        "plants": [
            "cucumber",
            "melon",
            "cantaloupe",
            "watermelon",
            "squash",
            "pumpkin",
        ],
    },
    "onions_and_garlic": {
        "group": "allium",
        "plants": [
            "onion",
            "garlic",
        ],
    },
    "various_vegetables_and_melons": {
        "group": "vegetables_and_melons",
        "plants": [],
    },
}


def normalize_plant_atom(value: Any) -> Optional[str]:
    atom = to_snake(value)

    if not atom:
        return None

    return PLANT_NAME_ALIASES.get(atom, atom)


def split_host_terms(host_text: str) -> List[str]:
    """
    Split host text into terms.

    Examples:
        "onions and garlic" -> ["onions", "garlic"]
        "broccoli, cabbage, cauliflower" -> [...]
        "various vegetables and melons" should stay as one broad host group.
    """

    text = clean_text(host_text)

    if not text:
        return []

    broad = to_snake(text)

    if broad in HOST_GROUP_EXPANSIONS:
        return [text]

    text = text.replace("/", ", ")
    text = text.replace(";", ", ")
    text = re.sub(r"\s+and\s+", ", ", text, flags=re.IGNORECASE)

    return [part.strip() for part in text.split(",") if part.strip()]


def normalize_host(host_text: str) -> Dict[str, List[str]]:
    """
    Converts raw UC IPM host text into:
    - plants_affected
    - plant_groups_affected
    - raw_host_terms
    """

    raw_terms = split_host_terms(host_text)

    plants: List[str] = []
    groups: List[str] = []

    for term in raw_terms:
        atom = normalize_plant_atom(term)

        if not atom:
            continue

        if atom in HOST_GROUP_EXPANSIONS:
            expansion = HOST_GROUP_EXPANSIONS[atom]
            groups.append(expansion["group"])
            plants.extend(expansion["plants"])
            continue

        plants.append(atom)

    return {
        "plants_affected": dedupe_atoms(plants),
        "plant_groups_affected": dedupe_atoms(groups),
        "raw_host_terms": dedupe_keep_order(raw_terms),
    }


# =========================================================
# DISEASE NORMALIZATION
# =========================================================

DISEASE_TYPE_ALIASES = {
    "fungus": "fungal",
    "fungi": "fungal",
    "fungal": "fungal",
    "bacteria": "bacterial",
    "bacterium": "bacterial",
    "bacterial": "bacterial",
    "virus": "viral",
    "viral": "viral",
    "oomycete": "oomycete",
    "phytoplasma": "phytoplasma",
    "nematode": "nematode",
}


def normalize_disease_type(value: Any) -> Optional[str]:
    atom = to_snake(value)

    if not atom:
        return None

    return DISEASE_TYPE_ALIASES.get(atom, atom)


def disease_id_from_common_name(common_name: Any) -> Optional[str]:
    """
    Disease ID is based on common name.

    Example:
        "Powdery mildew" -> powdery_mildew

    This intentionally merges same common disease across plants.
    Pathogens are stored separately in pathogen_records.
    """

    return to_snake(common_name)


def clean_pathogen_name(value: Any) -> Optional[str]:
    text = clean_text(value)

    if not text:
        return None

    lowered = text.lower()

    if lowered in {"none", "various", "unknown", "n/a", "na"}:
        return None

    return text


# =========================================================
# TABLE EXTRACTION
# =========================================================


def extract_table_rows_from_uc_ipm(
    html: str,
    source_url: Optional[str],
    source_name: str,
    source_id: str,
    confidence: float,
) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table", id="VEGETABLES")

    if table is None:
        # fallback: first table with matching headers
        for candidate in soup.find_all("table"):
            headers = [clean_text(th.get_text(" ")) or "" for th in candidate.find_all("th")]
            header_text = " ".join(headers).lower()

            if "plant" in header_text and "common" in header_text and "scientific" in header_text and "type" in header_text:
                table = candidate
                break

    if table is None:
        raise RuntimeError("Could not find UC IPM disease table.")

    rows = table.find_all("tr")
    extracted: List[Dict[str, Any]] = []

    for row in rows:
        cells = row.find_all("td")

        # Skip header rows.
        if len(cells) < 4:
            continue

        host_text = clean_text(cells[0].get_text(" "))
        common_name = clean_text(cells[1].get_text(" "))
        scientific_name = clean_pathogen_name(cells[2].get_text(" "))
        disease_type = normalize_disease_type(cells[3].get_text(" "))

        if not host_text or not common_name:
            continue

        disease_id = disease_id_from_common_name(common_name)

        if not disease_id:
            continue

        host_data = normalize_host(host_text)

        detail_url = None
        link = cells[1].find("a", href=True)

        if link and source_url:
            detail_url = urljoin(source_url, link["href"])

        record = {
            "disease_id": disease_id,
            "display_name": common_name,
            "pathogen_name": scientific_name,
            "pathogen_type": disease_type,
            "plants_affected": host_data["plants_affected"],
            "plant_groups_affected": host_data["plant_groups_affected"],
            "raw_host_text": host_text,
            "raw_host_terms": host_data["raw_host_terms"],
            "source_name": source_name,
            "source_id": source_id,
            "source_url": source_url,
            "detail_url": detail_url,
            "confidence": confidence,
            "extracted_at": now_iso(),
        }

        extracted.append(record)

    return extracted


# =========================================================
# MERGING TO DISEASE SEED / BANK
# =========================================================


def pathogen_record_from_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "pathogen_name": row.get("pathogen_name"),
        "pathogen_type": row.get("pathogen_type"),
        "plants_affected": row.get("plants_affected") or [],
        "plant_groups_affected": row.get("plant_groups_affected") or [],
        "raw_host_text": row.get("raw_host_text"),
        "source_id": row.get("source_id"),
        "source_name": row.get("source_name"),
        "source_url": row.get("source_url"),
        "detail_url": row.get("detail_url"),
        "confidence": row.get("confidence"),
    }


def source_record_from_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source_id": row.get("source_id"),
        "source_name": row.get("source_name"),
        "source_url": row.get("source_url"),
        "detail_url": row.get("detail_url"),
        "raw_host_text": row.get("raw_host_text"),
        "plants_affected": row.get("plants_affected") or [],
        "plant_groups_affected": row.get("plant_groups_affected") or [],
        "confidence": row.get("confidence"),
        "extracted_at": row.get("extracted_at"),
    }


def record_key_for_dedupe(record: Dict[str, Any]) -> str:
    return json.dumps(record, sort_keys=True, ensure_ascii=False)


def merge_rows_to_disease_seed(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_disease: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        disease_id = row["disease_id"]

        if disease_id not in by_disease:
            by_disease[disease_id] = {
                "disease_id": disease_id,
                "display_name": row.get("display_name"),
                "pathogen_type": row.get("pathogen_type"),
                "pathogen_names": [],
                "plants_affected": [],
                "plant_groups_affected": [],
                "raw_host_terms": [],
                "pathogen_records": [],
                "source_records": [],
                "source_name": row.get("source_name"),
                "source_url": row.get("source_url"),
                "confidence": row.get("confidence") or 0.8,
                "last_verified_at": now_iso(),
            }

        item = by_disease[disease_id]

        if row.get("pathogen_name"):
            item["pathogen_names"].append(row["pathogen_name"])

        if not item.get("pathogen_type") and row.get("pathogen_type"):
            item["pathogen_type"] = row["pathogen_type"]

        item["plants_affected"].extend(row.get("plants_affected") or [])
        item["plant_groups_affected"].extend(row.get("plant_groups_affected") or [])
        item["raw_host_terms"].extend(row.get("raw_host_terms") or [])

        item["pathogen_records"].append(pathogen_record_from_row(row))
        item["source_records"].append(source_record_from_row(row))

        try:
            item["confidence"] = max(
                float(item.get("confidence") or 0),
                float(row.get("confidence") or 0),
            )
        except (TypeError, ValueError):
            pass

    result: List[Dict[str, Any]] = []

    for disease_id, item in by_disease.items():
        item["pathogen_names"] = dedupe_keep_order(item["pathogen_names"])
        item["plants_affected"] = dedupe_atoms(item["plants_affected"])
        item["plant_groups_affected"] = dedupe_atoms(item["plant_groups_affected"])
        item["raw_host_terms"] = dedupe_keep_order(item["raw_host_terms"])

        # Deduplicate nested records.
        pathogen_seen = set()
        pathogen_records = []

        for record in item["pathogen_records"]:
            key = record_key_for_dedupe(record)
            if key not in pathogen_seen:
                pathogen_seen.add(key)
                pathogen_records.append(record)

        source_seen = set()
        source_records = []

        for record in item["source_records"]:
            key = record_key_for_dedupe(record)
            if key not in source_seen:
                source_seen.add(key)
                source_records.append(record)

        item["pathogen_records"] = pathogen_records
        item["source_records"] = source_records

        result.append(item)

    return sorted(result, key=lambda item: item["disease_id"])


def seed_to_bank(seed: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    bank: Dict[str, Dict[str, Any]] = {}

    for item in seed:
        disease_id = item["disease_id"]

        bank[disease_id] = {
            "disease_id": disease_id,
            "display_name": item.get("display_name"),
            "pathogen_names": item.get("pathogen_names") or [],
            "pathogen_type": item.get("pathogen_type"),
            "plants_affected": item.get("plants_affected") or [],
            "plant_groups_affected": item.get("plant_groups_affected") or [],
            "affected_parts": item.get("affected_parts") or [],
            "symptoms": item.get("symptoms") or [],
            "favorable_conditions": item.get("favorable_conditions") or [],
            "spread_method": item.get("spread_method") or [],
            "prevention": item.get("prevention") or [],
            "treatment": item.get("treatment") or [],
            "raw_host_terms": item.get("raw_host_terms") or [],
            "pathogen_records": item.get("pathogen_records") or [],
            "source_records": item.get("source_records") or [],
            "source_name": item.get("source_name"),
            "source_url": item.get("source_url"),
            "confidence": item.get("confidence") or 0.8,
            "last_verified_at": item.get("last_verified_at") or now_iso(),
        }

    return dict(sorted(bank.items(), key=lambda pair: pair[0]))


# =========================================================
# SOURCE CONFIG
# =========================================================


def load_sources(path: Path) -> List[Dict[str, Any]]:
    sources = load_json(path, default=[])

    if not isinstance(sources, list):
        raise RuntimeError(f"Expected source list JSON: {path}")

    return [source for source in sources if isinstance(source, dict)]


def extract_from_source(source: Dict[str, Any], dry_run: bool = False) -> List[Dict[str, Any]]:
    source_id = source.get("source_id") or "uc_ipm_vegetables_diseases"
    source_name = source.get("source_name") or "UC IPM"
    source_url = source.get("source_url")
    source_type = source.get("source_type") or "uc_ipm_disease_index"
    local_html = source.get("local_html")
    confidence = float(source.get("confidence") or 0.88)

    if source_type != "uc_ipm_disease_index":
        print(f"[WARN] Unsupported source_type: {source_type}")
        return []

    print(f"[INFO] Source: {source_id}")

    if dry_run:
        print("[DRY-RUN] Not reading/fetching source.")
        return []

    if local_html:
        html_path = Path(local_html)

        if not html_path.is_absolute():
            html_path = (PATHS.project_root / html_path).resolve()

        print(f"[INFO] Reading local HTML: {html_path}")
        html = read_html_from_file(html_path)
    else:
        if not source_url:
            raise RuntimeError(f"Source missing source_url/local_html: {source}")

        print(f"[INFO] Fetching URL: {source_url}")
        html = fetch_html(source_url)

    return extract_table_rows_from_uc_ipm(
        html=html,
        source_url=source_url,
        source_name=source_name,
        source_id=source_id,
        confidence=confidence,
    )


# =========================================================
# REPORTING
# =========================================================


def print_summary(rows: List[Dict[str, Any]], seed: List[Dict[str, Any]], bank: Dict[str, Any]) -> None:
    plants = set()

    for item in seed:
        plants.update(item.get("plants_affected") or [])

    groups = set()

    for item in seed:
        groups.update(item.get("plant_groups_affected") or [])

    print("")
    print("========== Disease Bank Extraction Summary ==========")
    print(f"Raw table rows extracted : {len(rows)}")
    print(f"Unique diseases          : {len(seed)}")
    print(f"Unique affected plants   : {len(plants)}")
    print(f"Plant groups affected    : {len(groups)}")
    print(f"Disease bank entries     : {len(bank)}")
    print("=====================================================")

    print("")
    print("Sample diseases:")
    for item in seed[:20]:
        plants_text = ", ".join(item.get("plants_affected") or [])
        groups_text = ", ".join(item.get("plant_groups_affected") or [])
        print(f" - {item['disease_id']}: plants=[{plants_text}] groups=[{groups_text}]")

    print("")


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract all disease-to-plant mappings from UC IPM disease table.")

    parser.add_argument(
        "--sources",
        default=str(PATHS.disease_sources),
        help="Disease source config JSON.",
    )

    parser.add_argument(
        "--raw-output",
        default=str(PATHS.data_bank_raw_sources / "uc_ipm_disease_rows.json"),
        help="Output raw extracted disease rows.",
    )

    parser.add_argument(
        "--seed-output",
        default=str(PATHS.data_bank_manual_sources / "disease_seed.json"),
        help="Output generated disease seed JSON.",
    )

    parser.add_argument(
        "--bank-output",
        default=str(PATHS.disease_bank),
        help="Output normalized disease bank JSON.",
    )

    parser.add_argument(
        "--local-html",
        default=None,
        help="Optional local HTML file to parse instead of sources config URL.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing output files.",
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

    raw_output = Path(args.raw_output)
    seed_output = Path(args.seed_output)
    bank_output = Path(args.bank_output)

    all_rows: List[Dict[str, Any]] = []

    if args.local_html:
        local_html = Path(args.local_html)

        if not local_html.is_absolute():
            local_html = (PATHS.project_root / local_html).resolve()

        source = {
            "source_id": "uc_ipm_vegetables_diseases_local",
            "source_name": "UC IPM - Diseases of vegetables and melons",
            "source_url": "https://ipm.ucanr.edu/PMG/diseases/diseases.vegies.html",
            "source_type": "uc_ipm_disease_index",
            "local_html": str(local_html),
            "confidence": 0.88,
        }

        all_rows.extend(extract_from_source(source, dry_run=args.dry_run))
    else:
        sources_path = Path(args.sources)

        if not sources_path.exists():
            raise RuntimeError(
                f"Missing disease source config: {sources_path}. " f"Create data_bank/manual_sources/disease_sources.json " f"or pass --local-html."
            )

        sources = load_sources(sources_path)

        for source in sources:
            all_rows.extend(extract_from_source(source, dry_run=args.dry_run))

    if args.dry_run:
        print("[DRY-RUN] No files written.")
        return

    disease_seed = merge_rows_to_disease_seed(all_rows)
    disease_bank = seed_to_bank(disease_seed)

    save_json(raw_output, all_rows)
    save_json(seed_output, disease_seed)
    save_json(bank_output, disease_bank)

    print_summary(all_rows, disease_seed, disease_bank)

    print(f"[OK] Raw disease rows written : {raw_output}")
    print(f"[OK] Disease seed written     : {seed_output}")
    print(f"[OK] Disease bank written     : {bank_output}")


if __name__ == "__main__":
    main()
