#!/usr/bin/env python3
"""
extract_pest_details.py

Purpose:
- Enrich data_bank/normalized/pest_bank.json.bak with pest detail fields.
- Uses detail_url/source URLs already stored in pest_bank.json.bak source_records.
- Extracts damage, affected parts, favorable conditions, prevention, treatment,
  and beneficial predators.

Input:
    data_bank/normalized/pest_bank.json.bak

Output:
    updated data_bank/normalized/pest_bank.json.bak

Design:
- Plant profiles stay lightweight.
- Pest details stay centralized in pest_bank.json.bak.
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


def fetch_html(url: str, timeout: int = 30, sleep_seconds: float = 0.7) -> Optional[str]:
    time.sleep(sleep_seconds)

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "SmartFarmingPestDetailExtractor/1.0"},
        )
        response.raise_for_status()
        return response.text
    except Exception as exc:
        print(f"[WARN] Could not fetch {url}: {exc}")
        return None


# =========================================================
# URL SELECTION
# =========================================================


def collect_candidate_urls(pest: Dict[str, Any]) -> List[str]:
    urls: List[str] = []

    for key in ["detail_url", "source_url"]:
        url = clean_text(pest.get(key))

        if url:
            urls.append(url)

    for record in pest.get("source_records") or []:
        if not isinstance(record, dict):
            continue

        for key in ["detail_url", "source_url"]:
            url = clean_text(record.get(key))

            if url:
                urls.append(url)

    urls = dedupe_keep_order(urls)

    # Prefer detail pages over broad index pages.
    urls = sorted(
        urls,
        key=lambda url: (
            0 if "/insect/" in url or "/vegetable/" in url else 1,
            1 if url.endswith("hosts-pests_ver01") else 0,
            url,
        ),
    )

    return urls


# =========================================================
# HTML TEXT EXTRACTION
# =========================================================


def html_to_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def remove_noise(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "form"]):
        tag.decompose()


def get_main_content(soup: BeautifulSoup):
    return (
        soup.find("main")
        or soup.find("div", id="main-content")
        or soup.find("div", id="pagecontent")
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
    "damage": [
        "damage",
        "pest description and crop damage",
        "symptoms",
        "identification",
        "description",
    ],
    "affected_parts": [
        "damage",
        "pest description and crop damage",
        "identification",
    ],
    "favorable_conditions": [
        "biology",
        "life history",
        "conditions",
        "seasonal development",
        "weather",
    ],
    "prevention": [
        "cultural control",
        "prevention",
        "management",
        "monitoring",
        "integrated pest management",
    ],
    "treatment": [
        "management",
        "control",
        "biological control",
        "chemical control",
        "organic control",
        "home use",
    ],
    "beneficial_predators": [
        "biological control",
        "natural enemies",
        "predators",
        "parasites",
        "parasitoids",
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


def extract_text_after_heading(heading_tag, max_blocks: int = 10) -> List[str]:
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
        "damage": [],
        "affected_parts": [],
        "favorable_conditions": [],
        "prevention": [],
        "treatment": [],
        "beneficial_predators": [],
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
        "damage": keyword_filter(
            paragraphs,
            ["damage", "feed", "feeding", "chew", "suck", "stunt", "yellow", "curl", "mine", "defoliate"],
        ),
        "favorable_conditions": keyword_filter(
            paragraphs,
            ["overwinter", "generation", "life cycle", "egg", "larva", "nymph", "adult", "weather", "season"],
        ),
        "prevention": keyword_filter(
            paragraphs,
            ["monitor", "avoid", "prevent", "row cover", "rotation", "sanitation", "weed", "trap"],
        ),
        "treatment": keyword_filter(
            paragraphs,
            ["control", "spray", "insecticide", "soap", "oil", "bt", "spinosad", "remove", "manage"],
        ),
        "beneficial_predators": keyword_filter(
            paragraphs,
            ["natural enemies", "predator", "parasitoid", "lady beetle", "lacewing", "hover fly", "wasp"],
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


BENEFICIAL_PREDATOR_TERMS = {
    "ladybug": ["lady beetle", "ladybird", "lady bug", "ladybug"],
    "lacewing": ["lacewing"],
    "hoverfly": ["hover fly", "syrphid"],
    "parasitic_wasp": ["parasitic wasp", "parasitoid wasp", "parasitoid"],
    "predatory_mite": ["predatory mite"],
    "ground_beetle": ["ground beetle"],
    "minute_pirate_bug": ["minute pirate bug"],
    "damsel_bug": ["damsel bug"],
    "spider": ["spider"],
}


def infer_affected_parts(texts: List[str]) -> List[str]:
    joined = " ".join(texts).lower()
    parts: List[str] = []

    for part, keywords in AFFECTED_PART_KEYWORDS.items():
        if any(keyword in joined for keyword in keywords):
            parts.append(part)

    return dedupe_atoms(parts)


def infer_beneficial_predators(texts: List[str]) -> List[str]:
    joined = " ".join(texts).lower()
    predators: List[str] = []

    for predator, terms in BENEFICIAL_PREDATOR_TERMS.items():
        if any(term in joined for term in terms):
            predators.append(predator)

    return dedupe_atoms(predators)


def extract_pest_detail_fields(html: str) -> Dict[str, Any]:
    soup = html_to_soup(html)
    remove_noise(soup)

    by_heading = extract_sections_by_headings(soup)
    by_keywords = extract_sections_by_keywords(soup)

    damage = dedupe_keep_order(by_heading.get("damage", []) + by_keywords.get("damage", []))[:10]
    favorable_conditions = dedupe_keep_order(by_heading.get("favorable_conditions", []) + by_keywords.get("favorable_conditions", []))[:10]
    prevention = dedupe_keep_order(by_heading.get("prevention", []) + by_keywords.get("prevention", []))[:10]
    treatment = dedupe_keep_order(by_heading.get("treatment", []) + by_keywords.get("treatment", []))[:10]

    predator_texts = dedupe_keep_order(by_heading.get("beneficial_predators", []) + by_keywords.get("beneficial_predators", []))[:10]

    affected_parts = infer_affected_parts(damage + by_heading.get("affected_parts", []))
    beneficial_predators = infer_beneficial_predators(predator_texts)

    return {
        "damage": damage,
        "affected_parts": affected_parts,
        "favorable_conditions": favorable_conditions,
        "prevention": prevention,
        "treatment": treatment,
        "beneficial_predators": beneficial_predators,
        "beneficial_predator_notes": predator_texts,
    }


# =========================================================
# MERGE
# =========================================================


def merge_detail_fields(existing: Dict[str, Any], incoming: Dict[str, Any], source_url: str) -> Dict[str, Any]:
    updated = dict(existing)

    for key in [
        "damage",
        "favorable_conditions",
        "prevention",
        "treatment",
        "beneficial_predator_notes",
    ]:
        updated[key] = dedupe_keep_order(list(updated.get(key) or []) + list(incoming.get(key) or []))

    for key in [
        "affected_parts",
        "beneficial_predators",
    ]:
        updated[key] = dedupe_atoms(list(updated.get(key) or []) + list(incoming.get(key) or []))

    detail_sources = list(updated.get("detail_sources") or [])

    detail_sources.append(
        {
            "source_url": source_url,
            "extracted_at": now_iso(),
        }
    )

    seen = set()
    deduped = []

    for source in detail_sources:
        key = source.get("source_url")

        if key and key not in seen:
            seen.add(key)
            deduped.append(source)

    updated["detail_sources"] = deduped
    updated["details_last_extracted_at"] = now_iso()

    return updated


def has_any_details(pest: Dict[str, Any]) -> bool:
    for key in ["damage", "affected_parts", "favorable_conditions", "prevention", "treatment", "beneficial_predators"]:
        if pest.get(key):
            return True
    return False


# =========================================================
# BULK PROCESS
# =========================================================


def enrich_pest_details(
    pest_bank_path: Path,
    dry_run: bool = False,
    only: Optional[str] = None,
    limit: Optional[int] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    bank = load_json(pest_bank_path, default={})

    if not isinstance(bank, dict):
        raise RuntimeError(f"Pest bank must be JSON object: {pest_bank_path}")

    only_id = to_snake(only) if only else None

    processed = 0
    changed = 0
    skipped_no_url = 0
    skipped_existing = 0
    failed = 0
    details = []

    for pest_id, pest in list(bank.items()):
        if not isinstance(pest, dict):
            continue

        pest_id_norm = to_snake(pest.get("pest_id") or pest_id)

        if only_id and pest_id_norm != only_id:
            continue

        if limit is not None and processed >= limit:
            break

        if has_any_details(pest) and not overwrite:
            skipped_existing += 1
            continue

        urls = collect_candidate_urls(pest)

        if not urls:
            skipped_no_url += 1
            continue

        processed += 1
        url = urls[0]

        print(f"[INFO] {pest_id_norm}: {url}")

        if dry_run:
            details.append({"id": pest_id_norm, "url": url, "changed": False})
            continue

        html = fetch_html(url)

        if not html:
            failed += 1
            continue

        extracted = extract_pest_detail_fields(html)

        if not any(extracted.values()):
            print(f"[WARN] No details extracted for {pest_id_norm}")
            details.append({"id": pest_id_norm, "url": url, "changed": False})
            continue

        updated = merge_detail_fields(pest, extracted, url)
        bank[pest_id] = updated
        changed += 1

        details.append(
            {
                "id": pest_id_norm,
                "url": url,
                "changed": True,
                "fields": {key: len(value) if isinstance(value, list) else 0 for key, value in extracted.items()},
            }
        )

    if not dry_run and changed:
        save_json(pest_bank_path, bank)

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
    print("========== Pest Detail Extraction Summary ==========")
    print(f"Dry run          : {dry_run}")
    print(f"Processed        : {summary['processed']}")
    print(f"Changed          : {summary['changed']}")
    print(f"Skipped no URL   : {summary['skipped_no_url']}")
    print(f"Skipped existing : {summary['skipped_existing']}")
    print(f"Failed           : {summary['failed']}")
    print("====================================================")

    for item in summary["details"][:30]:
        print(f" - {item['id']}: changed={item['changed']} url={item['url']}")

    if len(summary["details"]) > 30:
        print(f" ... and {len(summary['details']) - 30} more")

    print("")


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract pest detail fields into pest_bank.json.bak.")

    parser.add_argument(
        "--pest-bank",
        default=str(PATHS.pest_bank),
        help="Normalized pest bank JSON file.",
    )

    parser.add_argument(
        "--only",
        default=None,
        help="Only enrich one pest ID, e.g. aphid.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of pest detail pages processed.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-extract details even if details already exist.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without modifying pest_bank.json.bak.",
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

    pest_bank_path = Path(args.pest_bank)

    if not pest_bank_path.exists():
        raise RuntimeError(f"Pest bank does not exist: {pest_bank_path}. " f"Run scripts/pest/extract_pest_bank.py first.")

    summary = enrich_pest_details(
        pest_bank_path=pest_bank_path,
        dry_run=args.dry_run,
        only=args.only,
        limit=args.limit,
        overwrite=args.overwrite,
    )

    print_summary(summary, dry_run=args.dry_run)

    if args.dry_run:
        print("[DRY-RUN] No pest bank changes were written.")
    else:
        print("[OK] Pest detail extraction finished.")


if __name__ == "__main__":
    main()
