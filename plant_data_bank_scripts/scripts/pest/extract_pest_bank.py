#!/usr/bin/env python3
"""
extract_pest_bank.py

Purpose:
- Extract plant-to-pest relationships from structured pest source pages.
- Create a central pest bank:

    data_bank/normalized/pest_bank.json.bak

Current supported source:
- PNW Insect Management Handbook:
    Hosts and Pests of Vegetable Crops

Output:
1. data_bank/raw_sources/pnw_vegetable_pest_rows.json
2. data_bank/normalized/pest_bank.json.bak

Design:
- Plant profiles should only store known_pest_ids.
- Pest details stay in pest_bank.json.bak / Prolog.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set
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


def display_from_atom(atom: str) -> str:
    return atom.replace("_", " ").title()


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


def fetch_html(url: str, timeout: int = 30, sleep_seconds: float = 0.7) -> str:
    time.sleep(sleep_seconds)

    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "SmartFarmingPestBankExtractor/1.0"},
    )
    response.raise_for_status()

    return response.text


# =========================================================
# NORMALIZATION
# =========================================================

PLANT_NAME_ALIASES = {
    "beans": "bean",
    "bean_snap": "bean",
    "snap_bean": "bean",
    "snap_beans": "bean",
    "beets": "beet",
    "broccoli_raab": "broccoli_rabe",
    "brussel_sprouts": "brussels_sprout",
    "brussels_sprouts": "brussels_sprout",
    "cabbages": "cabbage",
    "carrots": "carrot",
    "celeries": "celery",
    "corn_sweet": "corn",
    "sweet_corn": "corn",
    "cucumbers": "cucumber",
    "eggplants": "eggplant",
    "garlics": "garlic",
    "greens": "leafy_green",
    "lettuces": "lettuce",
    "melons": "melon",
    "muskmelon": "melon",
    "muskmelons": "melon",
    "mustard_greens": "mustard_green",
    "onions": "onion",
    "peas": "pea",
    "peppers": "pepper",
    "potatoes": "potato",
    "pumpkins": "pumpkin",
    "radishes": "radish",
    "spinaches": "spinach",
    "squashes": "squash",
    "tomatoes": "tomato",
    "turnips": "turnip",
    "watermelons": "watermelon",
}


PEST_NAME_ALIASES = {
    "aphids": "aphid",
    "armyworms": "armyworm",
    "beetles": "beetle",
    "caterpillars": "caterpillar",
    "cutworms": "cutworm",
    "earwigs": "earwig",
    "flea_beetles": "flea_beetle",
    "grasshoppers": "grasshopper",
    "leafhoppers": "leafhopper",
    "leafminers": "leafminer",
    "loopers": "looper",
    "maggots": "maggot",
    "mites": "mite",
    "nematodes": "nematode",
    "slugs": "slug",
    "snails": "snail",
    "spider_mites": "spider_mite",
    "thrips": "thrips",
    "whiteflies": "whitefly",
    "wireworms": "wireworm",
}


PEST_TYPE_HINTS = {
    "aphid": "insect",
    "armyworm": "insect",
    "beetle": "insect",
    "borer": "insect",
    "bug": "insect",
    "caterpillar": "insect",
    "cutworm": "insect",
    "earwig": "insect",
    "fly": "insect",
    "grasshopper": "insect",
    "leafhopper": "insect",
    "leafminer": "insect",
    "looper": "insect",
    "maggot": "insect",
    "moth": "insect",
    "thrips": "insect",
    "whitefly": "insect",
    "wireworm": "insect",
    "mite": "mite",
    "spider_mite": "mite",
    "slug": "mollusk",
    "snail": "mollusk",
    "nematode": "nematode",
}


HOST_GROUP_EXPANSIONS = {
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
    "brassicas": {
        "group": "brassica",
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
    "leafy_greens": {
        "group": "leafy_green",
        "plants": [
            "lettuce",
            "spinach",
            "mustard_green",
            "kale",
            "chard",
        ],
    },
}


def normalize_plant_atom(value: Any) -> Optional[str]:
    atom = to_snake(value)

    if not atom:
        return None

    return PLANT_NAME_ALIASES.get(atom, atom)


def normalize_pest_atom(value: Any) -> Optional[str]:
    atom = to_snake(value)

    if not atom:
        return None

    return PEST_NAME_ALIASES.get(atom, atom)


def guess_pest_type(pest_id: str) -> Optional[str]:
    for key, pest_type in PEST_TYPE_HINTS.items():
        if key in pest_id:
            return pest_type

    return None


def split_host_terms(host_text: str) -> List[str]:
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


def normalize_pest_name(raw_text: str) -> Optional[str]:
    """
    Normalize pest list text.

    Examples:
        "aphid" -> aphid
        "armyworm/cutworm" -> armyworm_cutworm
        "cabbage looper" -> cabbage_looper
    """

    text = clean_text(raw_text)

    if not text:
        return None

    # Strip common trailing punctuation.
    text = text.strip(" .,:;")

    # Remove leading bullets or symbols.
    text = re.sub(r"^[•\-\*\u2022]\s*", "", text)

    # Remove extra phrases if source includes links with headings.
    text = re.sub(r"\s+\(.*?management.*?\)$", "", text, flags=re.IGNORECASE)

    return normalize_pest_atom(text)


# =========================================================
# PNW EXTRACTION
# =========================================================


def is_probable_crop_heading(tag) -> bool:
    """
    PNW page is typically structured as crop headings followed by pest links/lists.

    This function tries to identify crop/host headings.
    """

    if tag.name not in {"h2", "h3", "h4"}:
        return False

    text = clean_text(tag.get_text(" "))

    if not text:
        return False

    lowered = text.lower()

    reject_words = {
        "introduction",
        "about",
        "authors",
        "references",
        "resources",
        "management",
        "pesticide",
        "home",
        "contents",
    }

    if any(word in lowered for word in reject_words):
        return False

    if len(text.split()) > 8:
        return False

    return True


def extract_pest_names_from_container(container, base_url: Optional[str]) -> List[Dict[str, Any]]:
    """
    Extract pest names from a nearby container.

    Supports:
    - links
    - list items
    - comma-separated text fallback
    """

    pest_items: List[Dict[str, Any]] = []

    # Prefer links because PNW pest names are often links.
    for link in container.find_all("a", href=True):
        label = clean_text(link.get_text(" "))

        if not label:
            continue

        pest_id = normalize_pest_name(label)

        if not pest_id:
            continue

        pest_items.append(
            {
                "pest_id": pest_id,
                "display_name": label,
                "detail_url": urljoin(base_url, link["href"]) if base_url else None,
            }
        )

    if pest_items:
        return pest_items

    # Fallback to list items.
    for li in container.find_all("li"):
        label = clean_text(li.get_text(" "))

        if not label:
            continue

        pest_id = normalize_pest_name(label)

        if not pest_id:
            continue

        pest_items.append(
            {
                "pest_id": pest_id,
                "display_name": label,
                "detail_url": None,
            }
        )

    if pest_items:
        return pest_items

    # Last fallback: split text by comma/newline.
    text = clean_text(container.get_text("\n"))

    if not text:
        return []

    pieces = []

    for line in text.split("\n"):
        for part in line.split(","):
            part = clean_text(part)
            if part:
                pieces.append(part)

    for piece in pieces:
        pest_id = normalize_pest_name(piece)

        if not pest_id:
            continue

        pest_items.append(
            {
                "pest_id": pest_id,
                "display_name": piece,
                "detail_url": None,
            }
        )

    return pest_items


def extract_pnw_hosts_pests(
    html: str,
    source_url: Optional[str],
    source_name: str,
    source_id: str,
    confidence: float,
) -> List[Dict[str, Any]]:
    """
    Extract rows from PNW Hosts and Pests page.

    The page is usually heading-per-host, then linked pest list.
    """

    soup = BeautifulSoup(html, "lxml")

    main = soup.find("main") or soup.find("div", id="main-content") or soup.find("div", class_=re.compile("content", re.I)) or soup.body or soup

    records: List[Dict[str, Any]] = []

    headings = [tag for tag in main.find_all(["h2", "h3", "h4"]) if is_probable_crop_heading(tag)]

    for heading in headings:
        host_text = clean_text(heading.get_text(" "))

        if not host_text:
            continue

        host_data = normalize_host(host_text)

        # Collect following siblings until next heading.
        containers = []
        sibling = heading.find_next_sibling()

        while sibling is not None:
            if getattr(sibling, "name", None) in {"h2", "h3", "h4"}:
                break

            if getattr(sibling, "name", None) in {"ul", "ol", "p", "div", "table"}:
                containers.append(sibling)

            sibling = sibling.find_next_sibling()

        pest_items: List[Dict[str, Any]] = []

        for container in containers:
            pest_items.extend(extract_pest_names_from_container(container, source_url))

        # Deduplicate pest items by pest_id + detail_url.
        seen = set()
        deduped_pests = []

        for item in pest_items:
            key = (item.get("pest_id"), item.get("detail_url"))

            if key not in seen:
                seen.add(key)
                deduped_pests.append(item)

        for pest in deduped_pests:
            pest_id = pest["pest_id"]

            if not pest_id:
                continue

            records.append(
                {
                    "pest_id": pest_id,
                    "display_name": pest.get("display_name") or display_from_atom(pest_id),
                    "pest_type": guess_pest_type(pest_id),
                    "plants_affected": host_data["plants_affected"],
                    "plant_groups_affected": host_data["plant_groups_affected"],
                    "raw_host_text": host_text,
                    "raw_host_terms": host_data["raw_host_terms"],
                    "source_name": source_name,
                    "source_id": source_id,
                    "source_url": source_url,
                    "detail_url": pest.get("detail_url"),
                    "confidence": confidence,
                    "extracted_at": now_iso(),
                }
            )

    return records


# =========================================================
# GENERIC TABLE EXTRACTION FALLBACK
# =========================================================


def extract_generic_host_pest_tables(
    html: str,
    source_url: Optional[str],
    source_name: str,
    source_id: str,
    confidence: float,
) -> List[Dict[str, Any]]:
    """
    Fallback extractor for table-based pages.

    Looks for columns like:
        host/crop/plant
        pest/common name/insect
    """

    soup = BeautifulSoup(html, "lxml")
    records: List[Dict[str, Any]] = []

    for table in soup.find_all("table"):
        header_cells = table.find_all("th")
        headers = [clean_text(th.get_text(" ")) or "" for th in header_cells]
        normalized_headers = [to_snake(h) or "" for h in headers]

        if not normalized_headers:
            first_row = table.find("tr")
            if first_row:
                cells = first_row.find_all(["td", "th"])
                headers = [clean_text(cell.get_text(" ")) or "" for cell in cells]
                normalized_headers = [to_snake(h) or "" for h in headers]

        host_idx = None
        pest_idx = None

        for i, header in enumerate(normalized_headers):
            if any(token in header for token in ["host", "crop", "plant", "vegetable"]):
                host_idx = i
            if any(token in header for token in ["pest", "insect", "mite", "common_name"]):
                pest_idx = i

        if host_idx is None or pest_idx is None:
            continue

        rows = table.find_all("tr")

        for row in rows[1:]:
            cells = row.find_all(["td", "th"])

            if len(cells) <= max(host_idx, pest_idx):
                continue

            host_text = clean_text(cells[host_idx].get_text(" "))
            pest_text = clean_text(cells[pest_idx].get_text(" "))

            if not host_text or not pest_text:
                continue

            host_data = normalize_host(host_text)
            pest_id = normalize_pest_name(pest_text)

            if not pest_id:
                continue

            detail_url = None
            link = cells[pest_idx].find("a", href=True)

            if link and source_url:
                detail_url = urljoin(source_url, link["href"])

            records.append(
                {
                    "pest_id": pest_id,
                    "display_name": pest_text,
                    "pest_type": guess_pest_type(pest_id),
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
            )

    return records


# =========================================================
# MERGING
# =========================================================


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


def merge_rows_to_pest_bank(rows: List[Dict[str, Any]], existing_bank: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
    bank: Dict[str, Dict[str, Any]] = {}

    if isinstance(existing_bank, dict):
        for key, value in existing_bank.items():
            if not isinstance(value, dict):
                continue

            pest_id = normalize_pest_atom(value.get("pest_id") or key)

            if not pest_id:
                continue

            item = dict(value)
            item["pest_id"] = pest_id
            bank[pest_id] = item

    for row in rows:
        pest_id = normalize_pest_atom(row.get("pest_id") or row.get("display_name"))

        if not pest_id:
            continue

        if pest_id not in bank:
            bank[pest_id] = {
                "pest_id": pest_id,
                "display_name": row.get("display_name") or display_from_atom(pest_id),
                "pest_type": row.get("pest_type") or guess_pest_type(pest_id),
                "plants_affected": [],
                "plant_groups_affected": [],
                "damage": [],
                "symptoms": [],
                "favorable_conditions": [],
                "prevention": [],
                "treatment": [],
                "beneficial_predators": [],
                "source_name": row.get("source_name"),
                "source_url": row.get("source_url"),
                "confidence": row.get("confidence") or 0.75,
                "source_records": [],
                "last_verified_at": now_iso(),
            }

        item = bank[pest_id]

        if not item.get("display_name") and row.get("display_name"):
            item["display_name"] = row["display_name"]

        if not item.get("pest_type") and row.get("pest_type"):
            item["pest_type"] = row["pest_type"]

        item["plants_affected"] = dedupe_atoms(list(item.get("plants_affected") or []) + list(row.get("plants_affected") or []))

        item["plant_groups_affected"] = dedupe_atoms(list(item.get("plant_groups_affected") or []) + list(row.get("plant_groups_affected") or []))

        source_records = list(item.get("source_records") or [])
        source_records.append(source_record_from_row(row))

        seen = set()
        deduped_sources = []

        for record in source_records:
            key = record_key_for_dedupe(record)

            if key not in seen:
                seen.add(key)
                deduped_sources.append(record)

        item["source_records"] = deduped_sources

        try:
            item["confidence"] = max(
                float(item.get("confidence") or 0),
                float(row.get("confidence") or 0),
            )
        except (TypeError, ValueError):
            pass

        item["last_verified_at"] = now_iso()

    return dict(sorted(bank.items(), key=lambda pair: pair[0]))


# =========================================================
# SOURCE HANDLING
# =========================================================


def load_sources(path: Path) -> List[Dict[str, Any]]:
    sources = load_json(path, default=[])

    if not isinstance(sources, list):
        raise RuntimeError(f"Expected source list JSON: {path}")

    return [source for source in sources if isinstance(source, dict)]


def extract_from_source(source: Dict[str, Any], dry_run: bool = False) -> List[Dict[str, Any]]:
    source_id = source.get("source_id") or "unknown_pest_source"
    source_name = source.get("source_name") or source_id
    source_url = source.get("source_url")
    source_type = source.get("source_type") or "pnw_hosts_pests"
    local_html = source.get("local_html")
    confidence = float(source.get("confidence") or 0.8)

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

    if source_type == "pnw_hosts_pests":
        rows = extract_pnw_hosts_pests(
            html=html,
            source_url=source_url,
            source_name=source_name,
            source_id=source_id,
            confidence=confidence,
        )

        if rows:
            return rows

        print("[WARN] PNW heading-based extraction found 0 rows. Trying table fallback.")

        return extract_generic_host_pest_tables(
            html=html,
            source_url=source_url,
            source_name=source_name,
            source_id=source_id,
            confidence=confidence,
        )

    if source_type == "generic_host_pest_table":
        return extract_generic_host_pest_tables(
            html=html,
            source_url=source_url,
            source_name=source_name,
            source_id=source_id,
            confidence=confidence,
        )

    print(f"[WARN] Unsupported source_type: {source_type}")
    return []


# =========================================================
# REPORTING
# =========================================================


def print_summary(rows: List[Dict[str, Any]], bank: Dict[str, Any]) -> None:
    plants: Set[str] = set()
    groups: Set[str] = set()

    for item in bank.values():
        plants.update(item.get("plants_affected") or [])
        groups.update(item.get("plant_groups_affected") or [])

    print("")
    print("========== Pest Bank Extraction Summary ==========")
    print(f"Raw pest rows extracted : {len(rows)}")
    print(f"Unique pests_ver01            : {len(bank)}")
    print(f"Unique affected plants  : {len(plants)}")
    print(f"Plant groups affected   : {len(groups)}")
    print("==================================================")

    print("")
    print("Affected plants:")
    for plant in sorted(plants):
        print(f" - {plant}")

    print("")
    print("Sample pests_ver01:")
    for pest_id, item in list(bank.items())[:40]:
        plants_text = ", ".join(item.get("plants_affected") or [])
        groups_text = ", ".join(item.get("plant_groups_affected") or [])
        print(f" - {pest_id}: plants=[{plants_text}] groups=[{groups_text}]")

    if len(bank) > 40:
        print(f" ... and {len(bank) - 40} more")

    print("")


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract pest-to-plant mappings into pest_bank.json.bak.")

    parser.add_argument(
        "--sources",
        default=str(PATHS.pest_sources),
        help="Pest source config JSON.",
    )

    parser.add_argument(
        "--raw-output",
        default=str(PATHS.data_bank_raw_sources / "pnw_vegetable_pest_rows.json"),
        help="Output raw pest rows.",
    )

    parser.add_argument(
        "--bank-output",
        default=str(PATHS.pest_bank),
        help="Output normalized pest bank JSON.",
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
    bank_output = Path(args.bank_output)

    all_rows: List[Dict[str, Any]] = []

    if args.local_html:
        local_html = Path(args.local_html)

        if not local_html.is_absolute():
            local_html = (PATHS.project_root / local_html).resolve()

        source = {
            "source_id": "pnw_vegetable_hosts_pests_local",
            "source_name": "PNW Insect Management Handbook - Hosts and Pests of Vegetable Crops",
            "source_url": "https://pnwhandbooks.org/insect/vegetable/vegetable-pests/hosts-pests",
            "source_type": "pnw_hosts_pests",
            "local_html": str(local_html),
            "confidence": 0.82,
        }

        all_rows.extend(extract_from_source(source, dry_run=args.dry_run))

    else:
        sources_path = Path(args.sources)

        if not sources_path.exists():
            raise RuntimeError(f"Missing pest source config: {sources_path}. " f"Create data_bank/manual_sources/pest_sources.json " f"or pass --local-html.")

        sources = load_sources(sources_path)

        for source in sources:
            all_rows.extend(extract_from_source(source, dry_run=args.dry_run))

    if args.dry_run:
        print("[DRY-RUN] No files written.")
        return

    existing_bank = load_json(bank_output, default={})

    if existing_bank and not isinstance(existing_bank, dict):
        raise RuntimeError(f"Existing pest bank must be a JSON object: {bank_output}")

    pest_bank = merge_rows_to_pest_bank(all_rows, existing_bank=existing_bank)

    save_json(raw_output, all_rows)
    save_json(bank_output, pest_bank)

    print_summary(all_rows, pest_bank)

    print(f"[OK] Raw pest rows written : {raw_output}")
    print(f"[OK] Pest bank written     : {bank_output}")


if __name__ == "__main__":
    main()
