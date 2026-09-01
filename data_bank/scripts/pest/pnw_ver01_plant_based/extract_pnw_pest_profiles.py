#!/usr/bin/env python3
"""
extract_pnw_pest_profiles.py

Reads pnw_seed_pest_ver01.json, fetches pest detail pages, and creates
normalized pest profiles.

Input:
- data_bank/raw_sources/pnw/pnw_seed_pest_ver01.json

Outputs:
- data_bank/raw_sources/pnw/pest_pages/*.html
- data_bank/normalized/pests_ver01/*.json

Purpose:
- Convert PNW pest pages into reusable pest data bank profiles.
- Preserve host plants from the seed file.
- Extract sections such as:
  - includes
  - pest description and crop damage
  - biology and life history
  - pest monitoring
  - biological control
  - cultural control
  - home chemical control
  - commercial chemical control

Important:
- Chemical control text is stored as source data only.
- Do not use it as automatic recommendation logic without separate safety review.

Run from:
    data_bank/

Example:
    python3 scripts/pest/extract_pnw_pest_profiles.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

SOURCE_NAME = "PNW Insect Management Handbook"
DEFAULT_SEED_PATH = "data_bank/raw_sources/pnw/pnw_seed_pest_ver01.json"


SECTION_ALIASES = {
    "includes": "includes",
    "pest description and crop damage": "description_damage",
    "pest description, crop damage and life history": "description_damage",
    "pest description, crop damage, and life history": "description_damage",
    "biology and life history": "biology_life_history",
    "pest monitoring": "monitoring",
    "management-biological control": "management_biological",
    "management-cultural control": "management_cultural",
    "management-chemical control: home use": "management_chemical_home",
    "management-chemical control: commercial use": "management_chemical_commercial",
}


def normalize_text(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def to_atom(value: str) -> str:
    value = normalize_text(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def safe_filename_from_url(url: str) -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    slug = url.rstrip("/").split("/")[-1]
    slug = to_atom(slug) or "page"
    return f"{slug}_{digest}.html"


def load_seed(seed_path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(seed_path.read_text(encoding="utf-8"))

    if isinstance(payload, list):
        return payload

    pests = payload.get("pests_ver01")
    if not isinstance(pests, list):
        raise ValueError(f"Invalid seed file format: {seed_path}")

    return pests


def fetch_html(
    url: str,
    cache_dir: Path,
    sleep_seconds: float = 1.0,
    timeout: int = 30,
    refresh: bool = False,
) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / safe_filename_from_url(url)

    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding="utf-8", errors="ignore")

    headers = {"User-Agent": ("SmartFarmingDataBot/1.0 " "(educational research crawler; cached and polite)")}

    print(f"[INFO] Fetching {url}")
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    html = response.text
    cache_path.write_text(html, encoding="utf-8")

    time.sleep(sleep_seconds)
    return html


def clean_page_text(soup: BeautifulSoup) -> str:
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def extract_title(soup: BeautifulSoup) -> Optional[str]:
    h1 = soup.find("h1")
    if h1:
        return normalize_text(h1.get_text(" ", strip=True))
    return None


def extract_scientific_names_from_includes(includes_text: str) -> List[str]:
    """
    Extract names inside parentheses from the 'Includes' section.

    Example:
        Western flower thrips (Frankliniella occidentalis)
        Corn thrips (Frankliniella williamsi)

    Returns:
        ["Frankliniella occidentalis", "Frankliniella williamsi"]
    """
    if not includes_text:
        return []

    candidates = re.findall(r"\(([A-Z][a-z]+(?:\s+[a-z.-]+){1,3})\)", includes_text)

    cleaned = []
    for candidate in candidates:
        candidate = normalize_text(candidate)
        if candidate not in cleaned:
            cleaned.append(candidate)

    return cleaned


def split_sections(text: str) -> Dict[str, str]:
    """
    Splits page text into known PNW pest detail sections.

    This parser is intentionally text-based because the PNW pages are
    content pages where headings sometimes appear as plain text lines.
    """
    lines = [normalize_text(line) for line in text.splitlines()]
    lines = [line for line in lines if line]

    # Remove navigation content before the actual H1 area if possible.
    # The actual title usually appears after the breadcrumb search form.
    start_index = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            start_index = i
            break

    lines = lines[start_index:]

    sections: Dict[str, List[str]] = defaultdict(list)
    current_key: Optional[str] = None

    for line in lines:
        low = line.lower()

        if low == "download entire section":
            break

        if low.startswith("management-chemical control: home use"):
            current_key = "management_chemical_home"
            remainder = line[len("Management-chemical control: HOME USE") :].strip()
            if remainder:
                sections[current_key].append(remainder)
            continue

        if low.startswith("management-chemical control: commercial use"):
            current_key = "management_chemical_commercial"
            remainder = line[len("Management-chemical control: COMMERCIAL USE") :].strip()
            if remainder:
                sections[current_key].append(remainder)
            continue

        matched = False
        for heading, key in SECTION_ALIASES.items():
            if low == heading:
                current_key = key
                matched = True
                break

            if low.startswith(heading + " "):
                current_key = key
                remainder = line[len(heading) :].strip()
                if remainder:
                    sections[current_key].append(remainder)
                matched = True
                break

        if matched:
            continue

        if current_key:
            sections[current_key].append(line)

    return {key: normalize_text(" ".join(value)) for key, value in sections.items() if normalize_text(" ".join(value))}


def extract_control_list(section_text: str) -> List[str]:
    """
    Extract a rough list from chemical sections.

    Since get_text() flattens bullet lists, this is conservative.
    It mostly keeps the full section if reliable splitting is not possible.
    """
    if not section_text:
        return []

    # Split before common bullet-like ingredient chunks.
    parts = re.split(r"\s+(?=[a-zA-Z][a-zA-Z-]+(?:\s+\([^)]+\))?\s*(?:-|at\s))", section_text)
    cleaned = [normalize_text(part) for part in parts if len(normalize_text(part)) > 2]

    if len(cleaned) <= 1:
        return [section_text]

    return cleaned


def classify_pest_type(pest_atom: str, pest_name: str) -> str:
    text = f"{pest_atom} {pest_name}".lower()

    if "slug" in text:
        return "mollusk"
    if "mite" in text:
        return "mite"
    if "symphylan" in text:
        return "symphylan"
    if "springtail" in text or "collembola" in text:
        return "springtail"
    if "worm" in text or "moth" in text or "butterfly" in text:
        return "insect"
    if "beetle" in text or "aphid" in text or "thrips" in text:
        return "insect"
    if "fly" in text or "maggot" in text or "bug" in text:
        return "insect"

    return "insect"


def extract_damage_keywords(description_damage: str) -> List[str]:
    """
    Conservative keyword extraction for later Prolog use.
    These are not full symptoms, just normalized tags.
    """
    text = description_damage.lower()

    keyword_map = {
        "stunting": "stunting",
        "stunted": "stunting",
        "leaf": "leaf_damage",
        "leaves": "leaf_damage",
        "root": "root_damage",
        "roots": "root_damage",
        "seedling": "seedling_damage",
        "seedlings": "seedling_damage",
        "fruit": "fruit_damage",
        "pod": "pod_damage",
        "stem": "stem_damage",
        "wilting": "wilting",
        "curl": "leaf_curling",
        "distortion": "distortion",
        "holes": "feeding_holes",
        "feeding": "feeding_damage",
        "yellow": "yellowing",
        "silver": "silvering",
        "webbing": "webbing",
        "mine": "leaf_mining",
        "mining": "leaf_mining",
        "defoliation": "defoliation",
    }

    tags = []
    for raw, tag in keyword_map.items():
        if raw in text and tag not in tags:
            tags.append(tag)

    return tags


def merge_profiles(seed: Dict[str, Any], page_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    pest_atom = seed["pest_atom"]
    pest_name = seed.get("pest_name") or pest_atom.replace("_", " ")

    combined_sections: Dict[str, List[str]] = defaultdict(list)
    scientific_names: List[str] = []
    detail_urls: List[str] = []
    page_titles: List[str] = []

    for profile in page_profiles:
        for key, value in profile.get("sections", {}).items():
            if value and value not in combined_sections[key]:
                combined_sections[key].append(value)

        for sci in profile.get("scientific_names", []):
            if sci not in scientific_names:
                scientific_names.append(sci)

        if profile.get("source_url") and profile["source_url"] not in detail_urls:
            detail_urls.append(profile["source_url"])

        if profile.get("page_title") and profile["page_title"] not in page_titles:
            page_titles.append(profile["page_title"])

    description_damage = " ".join(combined_sections.get("description_damage", []))
    damage_tags = extract_damage_keywords(description_damage)

    home_controls = []
    commercial_controls = []

    for section in combined_sections.get("management_chemical_home", []):
        home_controls.extend(extract_control_list(section))

    for section in combined_sections.get("management_chemical_commercial", []):
        commercial_controls.extend(extract_control_list(section))

    profile = {
        "pest_atom": pest_atom,
        "name": pest_name,
        "pest_type": classify_pest_type(pest_atom, pest_name),
        "scientific_names": scientific_names,
        "primary_scientific_name": scientific_names[0] if scientific_names else None,
        "host_plants": sorted(seed.get("host_plants", [])),
        "source_pages": seed.get("source_pages", []),
        "detail_urls": detail_urls,
        "page_titles": page_titles,
        "description_damage": " ".join(combined_sections.get("description_damage", [])),
        "biology_life_history": " ".join(combined_sections.get("biology_life_history", [])),
        "monitoring": " ".join(combined_sections.get("monitoring", [])),
        "management": {
            "biological": " ".join(combined_sections.get("management_biological", [])),
            "cultural": " ".join(combined_sections.get("management_cultural", [])),
            "chemical_home": home_controls,
            "chemical_commercial": commercial_controls,
        },
        "damage_tags": damage_tags,
        "raw_section_keys": sorted(combined_sections.keys()),
        "source_name": seed.get("source_name") or SOURCE_NAME,
        "source_section": seed.get("source_section"),
        "source_index_url": seed.get("source_index_url"),
        "latest_revision": seed.get("latest_revision"),
        "data_origin": "pnw_vegetable_pest_profile",
        "confidence": seed.get("confidence", 0.85),
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }

    # Keep profile size under control. The raw cached HTML still exists.
    for key in [
        "description_damage",
        "biology_life_history",
        "monitoring",
    ]:
        if profile[key] and len(profile[key]) > 5000:
            profile[key] = profile[key][:5000].rstrip() + " ..."

    return profile


def parse_detail_page(html: str, source_url: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    text = clean_page_text(soup)

    title = extract_title(soup)
    sections = split_sections(text)

    includes = sections.get("includes", "")
    scientific_names = extract_scientific_names_from_includes(includes)

    return {
        "source_url": source_url,
        "page_title": title,
        "sections": sections,
        "scientific_names": scientific_names,
    }


def extract_profiles(
    seeds: List[Dict[str, Any]],
    output_dir: Path,
    cache_dir: Path,
    sleep_seconds: float,
    refresh: bool,
    only: Optional[str],
    limit: Optional[int],
) -> List[Dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)

    selected_seeds = seeds

    if only:
        only_atom = to_atom(only)
        selected_seeds = [seed for seed in seeds if seed["pest_atom"] == only_atom]

    if limit is not None:
        selected_seeds = selected_seeds[:limit]

    all_profiles = []

    for index, seed in enumerate(selected_seeds, start=1):
        pest_atom = seed["pest_atom"]
        print(f"\n[INFO] ({index}/{len(selected_seeds)}) Processing {pest_atom}")

        urls = []
        for source_page in seed.get("source_pages", []):
            url = source_page.get("url")
            if url and url not in urls:
                urls.append(url)

        page_profiles = []

        for url in urls:
            try:
                html = fetch_html(
                    url,
                    cache_dir=cache_dir,
                    sleep_seconds=sleep_seconds,
                    refresh=refresh,
                )
                page_profiles.append(parse_detail_page(html, url))
            except Exception as exc:
                print(f"[WARN] Failed to fetch/parse {url}: {exc}")

        profile = merge_profiles(seed, page_profiles)
        out_path = output_dir / f"{pest_atom}.json"

        out_path.write_text(
            json.dumps(profile, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(f"[OK] Wrote {out_path}")
        all_profiles.append(profile)

    return all_profiles


def print_summary(profiles: List[Dict[str, Any]]) -> None:
    host_count = len({host for profile in profiles for host in profile.get("host_plants", [])})
    sci_count = len({sci for profile in profiles for sci in profile.get("scientific_names", [])})

    print("")
    print("========== PNW PEST PROFILE SUMMARY ==========")
    print(f"Profiles:          {len(profiles)}")
    print(f"Unique host plants:{host_count}")
    print(f"Scientific names:  {sci_count}")
    print("")
    print("Sample profiles:")
    for profile in profiles[:20]:
        print(f"  - {profile['pest_atom']} " f"({len(profile.get('host_plants', []))} hosts, " f"{len(profile.get('scientific_names', []))} scientific names)")
    print("==============================================")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default=DEFAULT_SEED_PATH)
    parser.add_argument(
        "--output-dir",
        default="data_bank/normalized/pests_ver01",
    )
    parser.add_argument(
        "--cache-dir",
        default="data_bank/raw_sources/pnw/pest_pages",
    )
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--only", help="Only process one pest atom, e.g. aphid")
    parser.add_argument("--limit", type=int, help="Only process first N pests_ver01")
    args = parser.parse_args()

    seeds = load_seed(Path(args.seed))

    profiles = extract_profiles(
        seeds=seeds,
        output_dir=Path(args.output_dir),
        cache_dir=Path(args.cache_dir),
        sleep_seconds=args.sleep,
        refresh=args.refresh,
        only=args.only,
        limit=args.limit,
    )

    print_summary(profiles)


if __name__ == "__main__":
    main()
