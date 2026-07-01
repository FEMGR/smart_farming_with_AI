#!/usr/bin/env python3
"""
extract_pnw_pest_profiles.py

Reads pnw_seed_pest.json, fetches each PNW pest detail page,
and creates normalized pest profiles.

Input:
- data_bank/raw_sources/pnw/pnw_seed_pest.json

Outputs:
- data_bank/raw_sources/pnw/pest_pages/*.html
- data_bank/normalized/pests/*.json

The parser is designed for PNW detail pages like:
- Vegetable crop pests-Aphid
- Vegetable crop pests-Armyworm

Important structure:
- h1.page-header.styled-title
- div.field-name-field-body
- span.bold for section headings
- span.regular for common species names
- span.italic for scientific names
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag


DEFAULT_SEED_PATH = "data_bank/raw_sources/pnw/pnw_seed_pest.json"
SOURCE_NAME = "PNW Insect Management Handbook"


SECTION_NAME_MAP = {
    "includes": "includes",
    "biology and life history": "biology_life_history",
    "pest description and crop damage": "description_damage",
    "pest description, crop damage and life history": "description_damage",
    "pest description, crop damage, and life history": "description_damage",
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
    value = normalize_text(str(value)).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def safe_filename_from_url(url: str) -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    slug = to_atom(url.rstrip("/").split("/")[-1]) or "page"
    return f"{slug}_{digest}.html"


def load_seed(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(payload, list):
        return payload

    pests = payload.get("pests")
    if not isinstance(pests, list):
        raise ValueError(f"Invalid seed format: {path}")

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
        print(f"[CACHE] {url}")
        return cache_path.read_text(encoding="utf-8", errors="ignore")

    headers = {"User-Agent": ("SmartFarmingDataBot/1.0 " "(educational research crawler; cached and polite)")}

    print(f"[INFO] Fetching: {url}")
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    html = response.text
    cache_path.write_text(html, encoding="utf-8")

    time.sleep(sleep_seconds)
    return html


def extract_title(soup: BeautifulSoup) -> Optional[str]:
    h1 = soup.select_one("h1.page-header")
    if h1:
        return normalize_text(h1.get_text(" ", strip=True))

    h1 = soup.find("h1")
    if h1:
        return normalize_text(h1.get_text(" ", strip=True))

    if soup.title:
        return normalize_text(soup.title.get_text(" ", strip=True))

    return None


def extract_body_container(soup: BeautifulSoup) -> Optional[Tag]:
    """
    Main PNW detail body is inside:
        div.field-name-field-body div.field-item
    """
    body = soup.select_one(".field-name-field-body .field-item")
    if body:
        return body

    body = soup.select_one(".field-name-field-body")
    if body:
        return body

    return None


def normalize_section_heading(text: str) -> Optional[str]:
    key = normalize_text(text).lower()
    key = key.replace("–", "-").replace("—", "-")
    key = re.sub(r"\s+", " ", key)

    return SECTION_NAME_MAP.get(key)


def extract_includes_from_body(body: Tag) -> Tuple[str, List[Dict[str, Optional[str]]]]:
    """
    Extracts included pest species from span.regular and span.italic.

    Example:
        Green peach aphid (Myzus persicae)
        Melon aphid (Aphis gossypii)
    """
    included_species: List[Dict[str, Optional[str]]] = []

    # Find the paragraph after the "Includes" heading.
    paragraphs = body.find_all("p")
    includes_started = False

    for p in paragraphs:
        text = normalize_text(p.get_text(" ", strip=True))
        low = text.lower()

        if low == "includes":
            includes_started = True
            continue

        if includes_started:
            regulars = [normalize_text(span.get_text(" ", strip=True)) for span in p.select("span.regular")]
            italics = [normalize_text(span.get_text(" ", strip=True)) for span in p.select("span.italic")]

            max_len = max(len(regulars), len(italics))

            for index in range(max_len):
                common_name = regulars[index] if index < len(regulars) else None
                scientific_name = italics[index] if index < len(italics) else None

                if common_name or scientific_name:
                    included_species.append(
                        {
                            "common_name": common_name,
                            "scientific_name": scientific_name,
                            "scientific_atom": to_atom(scientific_name) if scientific_name else None,
                        }
                    )

            return text, included_species

    return "", included_species


def extract_sections_from_body(body: Tag) -> Dict[str, str]:
    """
    PNW pages place section headings inside span.bold within paragraphs:

        <p><span class="bold">Biology and life history</span> text...</p>

    This parser walks paragraphs and detects the bold span at the beginning.
    """
    sections: Dict[str, List[str]] = {}
    current_key: Optional[str] = None

    for p in body.find_all("p"):
        p_text = normalize_text(p.get_text(" ", strip=True))
        if not p_text:
            continue

        bold = p.find("span", class_="bold")
        section_key = None
        heading_text = None

        if bold:
            heading_text = normalize_text(bold.get_text(" ", strip=True))
            section_key = normalize_section_heading(heading_text)

        if section_key:
            current_key = section_key

            # Remove heading text from paragraph body.
            content = p_text
            if heading_text and content.lower().startswith(heading_text.lower()):
                content = normalize_text(content[len(heading_text) :])

            sections.setdefault(current_key, [])

            if content:
                sections[current_key].append(content)

            continue

        if current_key:
            sections.setdefault(current_key, []).append(p_text)

    return {key: normalize_text(" ".join(values)) for key, values in sections.items() if normalize_text(" ".join(values))}


def extract_meta_dates(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    def meta_content(selector: str) -> Optional[str]:
        tag = soup.select_one(selector)
        if tag and tag.get("content"):
            return tag["content"]
        return None

    return {
        "published_time": meta_content('meta[property="article:published_time"]'),
        "modified_time": meta_content('meta[property="article:modified_time"]'),
        "og_updated_time": meta_content('meta[property="og:updated_time"]'),
        "dcterms_date": meta_content('meta[name="dcterms.date"]'),
    }


def extract_image_info(soup: BeautifulSoup) -> List[Dict[str, Optional[str]]]:
    images = []

    for link in soup.select(".view-supplemental-images a[href]"):
        href = link.get("href")
        img = link.find("img")

        caption = None
        wrapper = link.find_parent()
        if wrapper:
            caption_tag = wrapper.select_one(".image-caption")
            if caption_tag:
                caption = normalize_text(caption_tag.get_text(" ", strip=True))

        images.append(
            {
                "url": href,
                "thumbnail_url": img.get("src") if img else None,
                "caption": caption,
            }
        )

    return images


def extract_scientific_names(included_species: List[Dict[str, Optional[str]]]) -> List[str]:
    names = []

    for item in included_species:
        sci = item.get("scientific_name")
        if sci and sci not in names:
            names.append(sci)

    return names


def extract_damage_tags(description_damage: str) -> List[str]:
    text = description_damage.lower()

    keyword_map = {
        "wilting": "wilting",
        "wilt": "wilting",
        "curl": "leaf_curling",
        "stunt": "stunting",
        "stunted": "stunting",
        "necrotic": "necrosis",
        "honeydew": "honeydew",
        "sooty mold": "sooty_mold",
        "leaf": "leaf_damage",
        "leaves": "leaf_damage",
        "stem": "stem_damage",
        "stems": "stem_damage",
        "root": "root_damage",
        "roots": "root_damage",
        "fruit": "fruit_damage",
        "feeding": "feeding_damage",
        "holes": "feeding_holes",
        "distort": "distortion",
        "yellow": "yellowing",
        "virus": "virus_vector",
        "disease": "disease_vector",
        "webbing": "webbing",
        "mine": "leaf_mining",
        "defoliation": "defoliation",
    }

    tags = []

    for keyword, tag in keyword_map.items():
        if keyword in text and tag not in tags:
            tags.append(tag)

    return tags


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

    return "insect"


def parse_pest_page(html: str, seed: Dict[str, Any]) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    body = extract_body_container(soup)

    if not body:
        raise RuntimeError("Could not find PNW field body container")

    page_title = extract_title(soup)
    includes_text, included_species = extract_includes_from_body(body)
    sections = extract_sections_from_body(body)
    meta_dates = extract_meta_dates(soup)
    images = extract_image_info(soup)

    pest_atom = seed["pest_atom"]
    pest_name = seed.get("pest_name") or pest_atom.replace("_", " ")

    scientific_names = extract_scientific_names(included_species)
    description_damage = sections.get("description_damage", "")

    profile = {
        "pest_atom": pest_atom,
        "name": pest_name,
        "pest_type": seed.get("pest_type") or classify_pest_type(pest_atom, pest_name),
        "page_title": page_title,
        "source_url": seed.get("source_url"),
        "source_name": seed.get("source_name") or SOURCE_NAME,
        "source_section": seed.get("source_section"),
        "source_index_url": seed.get("source_index_url"),
        "data_origin": "pnw_common_vegetable_pest_profile",
        "confidence": seed.get("confidence", 0.9),
        "included_species": included_species,
        "scientific_names": scientific_names,
        "primary_scientific_name": scientific_names[0] if scientific_names else None,
        # Common-page seed does not know hosts.
        # Fill this later from hosts-pests enrichment script if wanted.
        "host_plants": seed.get("host_plants", []),
        "includes_text": includes_text,
        "biology_life_history": sections.get("biology_life_history", ""),
        "description_damage": description_damage,
        "monitoring": sections.get("monitoring", ""),
        "management": {
            "biological": sections.get("management_biological", ""),
            "cultural": sections.get("management_cultural", ""),
            "chemical_home": sections.get("management_chemical_home", ""),
            "chemical_commercial": sections.get("management_chemical_commercial", ""),
        },
        "damage_tags": extract_damage_tags(description_damage),
        "raw_section_keys": sorted(sections.keys()),
        "images": images,
        "meta_dates": meta_dates,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }

    return profile


def write_profile(profile: Dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"{profile['pest_atom']}.json"

    path.write_text(
        json.dumps(profile, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return path


def extract_profiles(
    seeds: List[Dict[str, Any]],
    output_dir: Path,
    cache_dir: Path,
    sleep_seconds: float,
    refresh: bool,
    only: Optional[str],
    limit: Optional[int],
) -> List[Dict[str, Any]]:
    selected = seeds

    if only:
        only_atom = to_atom(only)
        selected = [seed for seed in selected if seed["pest_atom"] == only_atom]

    if limit is not None:
        selected = selected[:limit]

    profiles = []

    for index, seed in enumerate(selected, start=1):
        pest_atom = seed["pest_atom"]
        url = seed.get("source_url")

        print("")
        print(f"[INFO] ({index}/{len(selected)}) Processing {pest_atom}")

        if not url:
            print(f"[WARN] Missing source_url for {pest_atom}")
            continue

        try:
            html = fetch_html(
                url=url,
                cache_dir=cache_dir,
                sleep_seconds=sleep_seconds,
                refresh=refresh,
            )

            profile = parse_pest_page(html, seed)
            out_path = write_profile(profile, output_dir)

            print(f"[OK] Wrote: {out_path}")
            profiles.append(profile)

        except Exception as exc:
            print(f"[WARN] Failed {pest_atom}: {exc}")

    return profiles


def print_summary(profiles: List[Dict[str, Any]]) -> None:
    print("")
    print("========== PNW PEST PROFILE SUMMARY ==========")
    print(f"Profiles: {len(profiles)}")

    for profile in profiles[:30]:
        print(
            f"  - {profile['pest_atom']} "
            f"({len(profile.get('scientific_names', []))} scientific names, "
            f"{len(profile.get('damage_tags', []))} damage tags)"
        )

    print("==============================================")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default=DEFAULT_SEED_PATH)
    parser.add_argument(
        "--output-dir",
        default="data_bank/normalized/pests",
    )
    parser.add_argument(
        "--cache-dir",
        default="data_bank/raw_sources/pnw/pest_pages",
    )
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--limit", type=int)

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
