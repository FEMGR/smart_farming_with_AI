#!/usr/bin/env python3
"""
extract_disease_details.py

Purpose:
- Enrich data_bank/normalized/disease_bank.json with disease detail fields.
- Uses detail_url/source URLs already stored in disease_bank.json source_records.
- Extracts symptoms, affected parts, favorable conditions, spread, prevention, and treatment.

Input:
    data_bank/normalized/disease_bank.json

Output:
    updated data_bank/normalized/disease_bank.json

Design:
- Plant profiles stay lightweight.
- Disease details stay centralized in disease_bank.json.
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
    result: List[str] = []
    seen = set()

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


def load_detail_source_map(path: Path) -> Dict[str, List[Dict[str, Any]]]:
    data = load_json(path, default={})

    if not path.exists():
        return {}

    if not isinstance(data, dict):
        raise RuntimeError(f"Disease detail source map must be a JSON object: {path}")

    result: Dict[str, List[Dict[str, Any]]] = {}

    for disease_id, sources in data.items():
        disease_key = to_snake(disease_id)

        if not disease_key:
            continue

        if isinstance(sources, dict):
            sources = [sources]

        if not isinstance(sources, list):
            continue

        cleaned_sources = []

        for source in sources:
            if not isinstance(source, dict):
                continue

            url = clean_text(source.get("source_url"))

            if not url:
                continue

            cleaned_sources.append(source)

        result[disease_key] = cleaned_sources

    return result


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def fetch_html(url: str, timeout: int = 30, sleep_seconds: float = 0.7) -> Optional[str]:
    time.sleep(sleep_seconds)

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "SmartFarmingDiseaseDetailExtractor/1.0"},
        )
        response.raise_for_status()
        return response.text
    except Exception as exc:
        print(f"[WARN] Could not fetch {url}: {exc}")
        return None


def html_to_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


# =========================================================
# URL SELECTION
# =========================================================


def collect_candidate_urls(
    disease: Dict[str, Any],
    disease_id: str,
    detail_source_map: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> List[Dict[str, Any]]:
    """
    Prefer manually configured disease-centered detail pages.

    Falls back to URLs inside disease_bank.json only if they are not obvious
    index/table pages.
    """

    disease_key = to_snake(disease_id) or disease_id
    source_items: List[Dict[str, Any]] = []

    if detail_source_map and disease_key in detail_source_map:
        source_items.extend(detail_source_map[disease_key])

    for key in ["detail_url", "source_url"]:
        url = clean_text(disease.get(key))

        if url:
            source_items.append(
                {
                    "source_name": disease.get("source_name"),
                    "source_url": url,
                    "confidence": disease.get("confidence"),
                }
            )

    for record in disease.get("source_records") or []:
        if not isinstance(record, dict):
            continue

        for key in ["detail_url", "source_url"]:
            url = clean_text(record.get(key))

            if url:
                source_items.append(
                    {
                        "source_name": record.get("source_name"),
                        "source_url": url,
                        "confidence": record.get("confidence"),
                    }
                )

    bad_patterns = [
        "diseases.vegies.html",
        "/PMG/diseases/",
    ]

    cleaned: List[Dict[str, Any]] = []
    seen = set()

    for item in source_items:
        url = clean_text(item.get("source_url"))

        if not url:
            continue

        if any(pattern in url for pattern in bad_patterns):
            continue

        if url in seen:
            continue

        seen.add(url)
        cleaned.append(item)

    return cleaned


# =========================================================
# TEXT EXTRACTION
# =========================================================


def remove_noise(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "form"]):
        tag.decompose()


def get_main_content(soup: BeautifulSoup):
    return (
        soup.find("main")
        or soup.find("div", id="pagecontent")
        or soup.find("div", id="ipmcontent")
        or soup.find("div", class_=re.compile("content", re.I))
        or soup.body
        or soup
    )


def normalize_heading(text: Any) -> str:
    text = clean_text(text) or ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


SECTION_KEYWORDS = {
    "symptoms": [
        "symptoms",
        "symptom",
        "signs",
        "damage",
        "identification",
        "comments on the disease",
    ],
    "affected_parts": [
        "symptoms",
        "damage",
        "where found",
        "identification",
    ],
    "favorable_conditions": [
        "conditions",
        "disease development",
        "comments on the disease",
        "biology",
        "environment",
        "weather",
    ],
    "spread_method": [
        "spread",
        "transmission",
        "disease cycle",
        "biology",
        "comments on the disease",
    ],
    "prevention": [
        "prevention",
        "cultural control",
        "management",
        "comments on control",
        "integrated pest management",
    ],
    "treatment": [
        "management",
        "control",
        "comments on control",
        "biological control",
        "chemical control",
        "organic control",
        "treatment",
    ],
}


STOP_HEADINGS = {
    "references",
    "publication",
    "acknowledgements",
    "authors",
    "credits",
    "resources",
    "more information",
    "legal notices",
}


def heading_matches(heading: str, keywords: List[str]) -> bool:
    h = normalize_heading(heading)

    if not h:
        return False

    for kw in keywords:
        kw_norm = normalize_heading(kw)

        if h == kw_norm:
            return True

        if kw_norm in h:
            return True

    return False


def extract_text_after_heading(heading_tag, max_blocks: int = 8) -> List[str]:
    blocks: List[str] = []

    sibling = heading_tag.find_next_sibling()

    while sibling is not None and len(blocks) < max_blocks:
        if getattr(sibling, "name", None) in {"h1", "h2", "h3", "h4"}:
            next_heading = normalize_heading(sibling.get_text(" "))

            if next_heading in STOP_HEADINGS or next_heading:
                break

        if getattr(sibling, "name", None) in {"p", "li"}:
            text = clean_text(sibling.get_text(" "))
            if text and len(text) >= 25:
                blocks.append(text)

        elif getattr(sibling, "name", None) in {"ul", "ol"}:
            for li in sibling.find_all("li"):
                text = clean_text(li.get_text(" "))
                if text and len(text) >= 15:
                    blocks.append(text)

        sibling = sibling.find_next_sibling()

    return dedupe_keep_order(blocks)


def extract_sections_by_headings(soup: BeautifulSoup) -> Dict[str, List[str]]:
    result = {
        "symptoms": [],
        "affected_parts": [],
        "favorable_conditions": [],
        "spread_method": [],
        "prevention": [],
        "treatment": [],
    }

    main = get_main_content(soup)

    for heading in main.find_all(["h1", "h2", "h3", "h4", "strong", "b"]):
        heading_text = clean_text(heading.get_text(" "))

        if not heading_text:
            continue

        for field, keywords in SECTION_KEYWORDS.items():
            if heading_matches(heading_text, keywords):
                result[field].extend(extract_text_after_heading(heading))

    for key in result:
        result[key] = dedupe_keep_order(result[key])[:12]

    return result


def extract_all_paragraphs(soup: BeautifulSoup) -> List[str]:
    main = get_main_content(soup)
    texts: List[str] = []

    for tag in main.find_all(["p", "li"]):
        text = clean_text(tag.get_text(" "))

        if not text:
            continue

        if len(text) < 35:
            continue

        texts.append(text)

    return dedupe_keep_order(texts)


def keyword_filter(paragraphs: List[str], keywords: List[str], limit: int = 8) -> List[str]:
    result = []

    for text in paragraphs:
        low = text.lower()

        if any(keyword in low for keyword in keywords):
            result.append(text)

    return dedupe_keep_order(result)[:limit]


def extract_sections_by_keywords(soup: BeautifulSoup) -> Dict[str, List[str]]:
    paragraphs = extract_all_paragraphs(soup)

    return {
        "symptoms": keyword_filter(
            paragraphs,
            ["symptom", "lesion", "spot", "mold", "mildew", "wilt", "rot", "yellow", "brown", "stunt"],
        ),
        "favorable_conditions": keyword_filter(
            paragraphs,
            ["humidity", "humid", "wet", "moist", "rain", "temperature", "cool", "warm", "weather"],
        ),
        "spread_method": keyword_filter(
            paragraphs,
            ["spread", "spore", "wind", "splash", "seedborne", "soilborne", "transmit", "vector"],
        ),
        "prevention": keyword_filter(
            paragraphs,
            ["avoid", "prevent", "resistant", "rotation", "sanitation", "air circulation", "spacing"],
        ),
        "treatment": keyword_filter(
            paragraphs,
            ["control", "manage", "remove", "destroy", "fungicide", "spray", "treat", "organic"],
        ),
    }


AFFECTED_PART_KEYWORDS = {
    "leaf": ["leaf", "leaves", "foliage"],
    "stem": ["stem", "stems", "shoot"],
    "root": ["root", "roots"],
    "fruit": ["fruit", "fruits"],
    "flower": ["flower", "flowers", "blossom"],
    "seed": ["seed", "seeds"],
    "tuber": ["tuber", "tubers"],
    "bulb": ["bulb", "bulbs"],
    "crown": ["crown"],
}


def infer_affected_parts(texts: List[str]) -> List[str]:
    joined = " ".join(texts).lower()
    parts: List[str] = []

    for part, keywords in AFFECTED_PART_KEYWORDS.items():
        if any(keyword in joined for keyword in keywords):
            parts.append(part)

    return dedupe_atoms(parts)


def extract_disease_detail_fields(html: str) -> Dict[str, Any]:
    soup = html_to_soup(html)
    remove_noise(soup)

    by_heading = extract_sections_by_headings(soup)
    by_keywords = extract_sections_by_keywords(soup)

    symptoms = dedupe_keep_order(by_heading.get("symptoms", []) + by_keywords.get("symptoms", []))[:10]
    favorable_conditions = dedupe_keep_order(by_heading.get("favorable_conditions", []) + by_keywords.get("favorable_conditions", []))[:10]
    spread_method = dedupe_keep_order(by_heading.get("spread_method", []) + by_keywords.get("spread_method", []))[:10]
    prevention = dedupe_keep_order(by_heading.get("prevention", []) + by_keywords.get("prevention", []))[:10]
    treatment = dedupe_keep_order(by_heading.get("treatment", []) + by_keywords.get("treatment", []))[:10]

    affected_parts = infer_affected_parts(symptoms + by_heading.get("affected_parts", []))

    return {
        "symptoms": symptoms,
        "affected_parts": affected_parts,
        "favorable_conditions": favorable_conditions,
        "spread_method": spread_method,
        "prevention": prevention,
        "treatment": treatment,
    }


# =========================================================
# MERGE
# =========================================================


def merge_detail_fields(existing: Dict[str, Any], incoming: Dict[str, Any], source_url: str) -> Dict[str, Any]:
    updated = dict(existing)

    for key in [
        "symptoms",
        "affected_parts",
        "favorable_conditions",
        "spread_method",
        "prevention",
        "treatment",
    ]:
        if key == "affected_parts":
            updated[key] = dedupe_atoms(list(updated.get(key) or []) + list(incoming.get(key) or []))
        else:
            updated[key] = dedupe_keep_order(list(updated.get(key) or []) + list(incoming.get(key) or []))

    updated["details_last_extracted_at"] = now_iso()

    return updated


def has_any_details(disease: Dict[str, Any]) -> bool:
    for key in ["symptoms", "affected_parts", "favorable_conditions", "spread_method", "prevention", "treatment"]:
        if disease.get(key):
            return True
    return False


# =========================================================
# BULK PROCESS
# =========================================================


def enrich_disease_details(
    disease_bank_path: Path,
    detail_sources_path: Path,
    dry_run: bool = False,
    only: Optional[str] = None,
    limit: Optional[int] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    bank = load_json(disease_bank_path, default={})

    if not isinstance(bank, dict):
        raise RuntimeError(f"Disease bank must be JSON object: {disease_bank_path}")

    detail_source_map = load_detail_source_map(detail_sources_path)
    only_id = to_snake(only) if only else None

    processed = 0
    changed = 0
    skipped_no_url = 0
    skipped_existing = 0
    failed = 0
    details = []

    for disease_id, disease in list(bank.items()):
        if not isinstance(disease, dict):
            continue

        disease_id_norm = to_snake(disease.get("disease_id") or disease_id)

        if only_id and disease_id_norm != only_id:
            continue

        if limit is not None and processed >= limit:
            break

        if has_any_details(disease) and not overwrite:
            skipped_existing += 1
            continue

        source_items = collect_candidate_urls(
            disease=disease,
            disease_id=disease_id_norm,
            detail_source_map=detail_source_map,
        )

        if not source_items:
            skipped_no_url += 1
            continue

        processed += 1
        source_item = source_items[0]
        url = source_item["source_url"]

        print(f"[INFO] {disease_id_norm}: {url}")

        if dry_run:
            details.append({"id": disease_id_norm, "url": url, "changed": False})
            continue

        html = fetch_html(url)

        if not html:
            failed += 1
            continue

        extracted = extract_disease_detail_fields(html)

        if not any(extracted.values()):
            print(f"[WARN] No details extracted for {disease_id_norm}")
            details.append({"id": disease_id_norm, "url": url, "changed": False})
            continue

        updated = merge_detail_fields(disease, extracted, url)

        detail_sources = list(updated.get("detail_sources") or [])

        detail_sources.append(
            {
                "source_name": source_item.get("source_name"),
                "source_url": url,
                "confidence": source_item.get("confidence"),
                "extracted_at": now_iso(),
            }
        )

        seen_sources = set()
        deduped_sources = []

        for detail_source in detail_sources:
            source_key = detail_source.get("source_url")

            if source_key and source_key not in seen_sources:
                seen_sources.add(source_key)
                deduped_sources.append(detail_source)

        updated["detail_sources"] = deduped_sources
        bank[disease_id] = updated
        changed += 1

        details.append(
            {
                "id": disease_id_norm,
                "url": url,
                "changed": True,
                "fields": {key: len(value) if isinstance(value, list) else 0 for key, value in extracted.items()},
            }
        )

    if not dry_run and changed:
        save_json(disease_bank_path, bank)

    return {
        "processed": processed,
        "changed": changed,
        "skipped_no_url": skipped_no_url,
        "skipped_existing": skipped_existing,
        "failed": failed,
        "details": details,
    }


def print_summary(summary: Dict[str, Any], dry_run: bool) -> None:
    print("")
    print("========== Disease Detail Extraction Summary ==========")
    print(f"Dry run          : {dry_run}")
    print(f"Processed        : {summary['processed']}")
    print(f"Changed          : {summary['changed']}")
    print(f"Skipped no URL   : {summary['skipped_no_url']}")
    print(f"Skipped existing : {summary['skipped_existing']}")
    print(f"Failed           : {summary['failed']}")
    print("=======================================================")

    for item in summary["details"][:30]:
        print(f" - {item['id']}: changed={item['changed']} url={item['url']}")

    if len(summary["details"]) > 30:
        print(f" ... and {len(summary['details']) - 30} more")

    print("")


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract disease detail fields into disease_bank.json.")

    parser.add_argument(
        "--disease-bank",
        default=str(PATHS.disease_bank),
        help="Normalized disease bank JSON file.",
    )

    parser.add_argument(
        "--detail-sources",
        default=str(PATHS.disease_detail_sources),
        help="Manual disease detail source map JSON.",
    )

    parser.add_argument(
        "--only",
        default=None,
        help="Only enrich one disease ID, e.g. powdery_mildew.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of disease detail pages processed.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-extract details even if details already exist.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without modifying disease_bank.json.",
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

    disease_bank_path = Path(args.disease_bank)
    detail_sources_path = Path(args.detail_sources)

    if not disease_bank_path.exists():
        raise RuntimeError(f"Disease bank does not exist: {disease_bank_path}. " f"Run scripts/disease/extract_disease_bank.py first.")

    summary = enrich_disease_details(
        disease_bank_path=disease_bank_path,
        detail_sources_path=detail_sources_path,
        dry_run=args.dry_run,
        only=args.only,
        limit=args.limit,
        overwrite=args.overwrite,
    )

    print_summary(summary, dry_run=args.dry_run)

    if args.dry_run:
        print("[DRY-RUN] No disease bank changes were written.")
    else:
        print("[OK] Disease detail extraction finished.")


if __name__ == "__main__":
    main()
