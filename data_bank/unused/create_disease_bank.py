#!/usr/bin/env python3
"""
create_disease_bank.py

Purpose:
- Create a normalized central disease bank.
- Input: data_bank/manual_sources/disease_seed.json
- Output: data_bank/normalized/disease_bank.json

Design:
- Disease bank stores disease details once.
- Plant profiles should only store disease IDs.
- Optional --fetch-pages can fetch source_url pages and extract simple symptom/management text.

Recommended:
    python scripts/create_disease_bank.py

Optional web extraction:
    python scripts/create_disease_bank.py --fetch-pages

The web extraction is heuristic. It helps, but you should still review disease_bank.json.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from project_paths import PATHS

# =========================================================
# HELPERS
# =========================================================


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)

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


def to_snake(value: Any) -> Optional[str]:
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


def normalize_atom_list(value: Any) -> List[str]:
    result = []

    for item in clean_list(value):
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
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


# =========================================================
# OPTIONAL PAGE FETCHING / HEURISTIC EXTRACTION
# =========================================================


def fetch_page_text(url: str, timeout: int = 20) -> Optional[str]:
    """
    Fetch page text from source_url.

    Requires:
        pip install requests beautifulsoup4

    This is intentionally simple and defensive.
    """

    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("[WARN] requests/beautifulsoup4 not installed. Skipping page fetch.")
        return None

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "SmartFarmingDataBankBot/1.0"},
        )
        response.raise_for_status()
    except Exception as exc:
        print(f"[WARN] Could not fetch {url}: {exc}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text("\n")
    lines = [clean_text(line) for line in text.splitlines()]
    lines = [line for line in lines if line]

    return "\n".join(lines)


def extract_section_lines(page_text: str, heading_keywords: List[str], max_lines: int = 12) -> List[str]:
    """
    Heuristic section extractor.

    Looks for headings like:
        Symptoms
        Damage
        Management
        Prevention
        Control
        Conditions

    Then captures nearby lines until another likely heading.
    """

    if not page_text:
        return []

    lines = [line.strip() for line in page_text.splitlines() if line.strip()]
    results: List[str] = []

    heading_patterns = [kw.lower() for kw in heading_keywords]

    stop_headings = {
        "references",
        "resources",
        "publication",
        "contact",
        "more information",
        "credits",
        "authors",
        "citation",
    }

    for i, line in enumerate(lines):
        low = line.lower().strip(":")

        is_heading = any(low == pattern or low.startswith(pattern + ":") for pattern in heading_patterns)

        if not is_heading:
            continue

        captured = []

        for next_line in lines[i + 1 : i + 1 + max_lines]:
            next_low = next_line.lower().strip(":")

            if next_low in stop_headings:
                break

            # Stop if the next line looks like a different short heading.
            if len(next_line.split()) <= 5 and next_line.endswith(":"):
                break

            if len(next_line) >= 20:
                captured.append(next_line)

        results.extend(captured)

    return dedupe_keep_order(results)


def extract_from_source_page(url: Optional[str]) -> Dict[str, List[str]]:
    if not url:
        return {}

    page_text = fetch_page_text(url)

    if not page_text:
        return {}

    symptoms = extract_section_lines(
        page_text,
        ["symptoms", "symptom", "damage", "signs", "identification"],
    )

    favorable_conditions = extract_section_lines(
        page_text,
        ["conditions", "favorable conditions", "environment", "disease development"],
    )

    prevention = extract_section_lines(
        page_text,
        ["prevention", "cultural control", "cultural management", "avoidance"],
    )

    treatment = extract_section_lines(
        page_text,
        ["management", "control", "treatment"],
    )

    return {
        "symptoms": symptoms[:8],
        "favorable_conditions": favorable_conditions[:8],
        "prevention": prevention[:8],
        "treatment": treatment[:8],
    }


# =========================================================
# NORMALIZATION
# =========================================================


def normalize_disease_record(raw: Dict[str, Any], fetch_pages: bool = False) -> Optional[Dict[str, Any]]:
    disease_id = to_snake(raw.get("disease_id") or raw.get("display_name") or raw.get("name"))

    if not disease_id:
        return None

    display_name = clean_text(raw.get("display_name") or raw.get("name") or disease_id.replace("_", " ").title())
    source_url = clean_text(raw.get("source_url"))

    fetched: Dict[str, List[str]] = {}

    if fetch_pages and source_url:
        print(f"[INFO] Fetching source page for {disease_id}: {source_url}")
        fetched = extract_from_source_page(source_url)

    record = {
        "disease_id": disease_id,
        "display_name": display_name,
        "pathogen_name": clean_text(raw.get("pathogen_name")),
        "pathogen_type": to_snake(raw.get("pathogen_type")),
        "plants_affected": normalize_atom_list(raw.get("plants_affected")),
        "plant_groups_affected": normalize_atom_list(raw.get("plant_groups_affected")),
        "affected_parts": normalize_atom_list(raw.get("affected_parts")),
        "symptoms": dedupe_keep_order(clean_list(raw.get("symptoms")) + fetched.get("symptoms", [])),
        "favorable_conditions": dedupe_keep_order(clean_list(raw.get("favorable_conditions")) + fetched.get("favorable_conditions", [])),
        "spread_method": normalize_atom_list(raw.get("spread_method")),
        "prevention": dedupe_keep_order(clean_list(raw.get("prevention")) + fetched.get("prevention", [])),
        "treatment": dedupe_keep_order(clean_list(raw.get("treatment")) + fetched.get("treatment", [])),
        "source_name": clean_text(raw.get("source_name")) or "manual_seed",
        "source_url": source_url,
        "confidence": float(raw.get("confidence") or 0.7),
        "last_verified_at": clean_text(raw.get("last_verified_at")) or now_iso(),
    }

    return record


def merge_disease_record(existing: Optional[Dict[str, Any]], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """
    Missing-only merge.
    Existing values win, lists are merged.
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

    try:
        if float(incoming.get("confidence") or 0) > float(existing.get("confidence") or 0):
            merged["confidence"] = incoming.get("confidence")
            merged["source_name"] = incoming.get("source_name")
            merged["source_url"] = incoming.get("source_url")
    except (TypeError, ValueError):
        pass

    merged["last_verified_at"] = now_iso()

    return merged


# =========================================================
# MAIN LOGIC
# =========================================================


def build_disease_bank(seed_path: Path, output_path: Path, fetch_pages: bool = False) -> Dict[str, Dict[str, Any]]:
    seed_data = load_json(seed_path, default=[])

    if not isinstance(seed_data, list):
        raise RuntimeError(f"Expected JSON list in seed file: {seed_path}")

    existing_bank = load_json(output_path, default={})

    if not isinstance(existing_bank, dict):
        raise RuntimeError(f"Expected JSON object in disease bank: {output_path}")

    bank: Dict[str, Dict[str, Any]] = dict(existing_bank)

    for raw in seed_data:
        if not isinstance(raw, dict):
            continue

        record = normalize_disease_record(raw, fetch_pages=fetch_pages)

        if not record:
            continue

        disease_id = record["disease_id"]
        bank[disease_id] = merge_disease_record(bank.get(disease_id), record)

    save_json(output_path, bank)

    return bank


def print_summary(bank: Dict[str, Dict[str, Any]], output_path: Path) -> None:
    print("")
    print("========== Disease Bank Summary ==========")
    print(f"Output file       : {output_path}")
    print(f"Total diseases    : {len(bank)}")

    with_plants = sum(1 for item in bank.values() if item.get("plants_affected"))
    with_groups = sum(1 for item in bank.values() if item.get("plant_groups_affected"))
    with_treatment = sum(1 for item in bank.values() if item.get("treatment"))
    with_symptoms = sum(1 for item in bank.values() if item.get("symptoms"))

    print(f"With plants       : {with_plants}")
    print(f"With groups       : {with_groups}")
    print(f"With symptoms     : {with_symptoms}")
    print(f"With treatment    : {with_treatment}")
    print("==========================================")
    print("")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create normalized disease bank from curated disease seed.")

    parser.add_argument(
        "--seed",
        default=str(PATHS.data_bank / "manual_sources" / "disease_seed.json"),
        help="Input disease seed JSON file.",
    )

    parser.add_argument(
        "--output",
        default=str(PATHS.data_bank_normalized / "disease_bank.json"),
        help="Output normalized disease bank JSON file.",
    )

    parser.add_argument(
        "--fetch-pages",
        action="store_true",
        help="Fetch source_url pages and heuristically extract symptoms/treatment text.",
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

    seed_path = Path(args.seed)
    output_path = Path(args.output)

    if not seed_path.exists():
        raise RuntimeError(f"Disease seed file does not exist: {seed_path}")

    bank = build_disease_bank(
        seed_path=seed_path,
        output_path=output_path,
        fetch_pages=args.fetch_pages,
    )

    print_summary(bank, output_path)

    print(f"[OK] Disease bank written: {output_path}")


if __name__ == "__main__":
    main()
