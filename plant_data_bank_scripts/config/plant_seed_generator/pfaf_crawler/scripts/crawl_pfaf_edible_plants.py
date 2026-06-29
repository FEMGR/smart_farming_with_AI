#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import parse_qs, quote_plus, unquote_plus, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://pfaf.org"
START_URL = "https://pfaf.org/user/edibleuses.aspx"

DEFAULT_OUTPUT_DIR = Path("output")
REQUEST_DELAY_SECONDS = 1.0
TIMEOUT_SECONDS = 30

HEADERS = {"User-Agent": ("SmartFarmingResearchBot/1.0 " "(educational data extraction; respectful delay)")}


@dataclass
class Category:
    name: str
    url: str
    expected_count: Optional[int] = None


@dataclass
class PlantRecord:
    scientific_name: str
    url: str
    categories: List[str]

    common_name: Optional[str] = None
    edibility_rating: Optional[int] = None
    medicinal_rating: Optional[int] = None

    source: str = "PFAF"
    source_page: str = START_URL


def fetch_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.text


def normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None

    text = str(value).replace("\xa0", " ").strip()
    text = re.sub(r"\s+", " ", text)

    if not text:
        return None

    if text.lower() in {"&nbsp;", "nbsp"}:
        return None

    return text


def parse_int_or_none(value: Any) -> Optional[int]:
    text = normalize_text(value)

    if not text:
        return None

    return int(text) if text.isdigit() else None


def extract_count_from_text(text: str) -> Optional[int]:
    match = re.search(r"\(\s*(\d+)\s*\)", text or "")
    if not match:
        return None
    return int(match.group(1))


def clean_category_name(text: str) -> str:
    text = normalize_text(text) or ""
    text = re.sub(r"\(\s*\d+\s*\)", "", text)
    return normalize_text(text) or ""


def is_edible_category_link(href: str) -> bool:
    href_lower = (href or "").lower()
    return "search_use.aspx" in href_lower and "glossary=" in href_lower


def is_plant_profile_link(href: str) -> bool:
    href_lower = (href or "").lower()
    return "plant.aspx" in href_lower and "latinname=" in href_lower


def extract_scientific_name_from_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    latin_values = query.get("LatinName") or query.get("latinname")
    if not latin_values:
        return None

    return normalize_text(unquote_plus(latin_values[0]))


def normalize_pfaf_plant_url(url: str) -> str:
    scientific_name = extract_scientific_name_from_url(url)

    if not scientific_name:
        return url

    return f"{BASE_URL}/user/Plant.aspx?LatinName={quote_plus(scientific_name)}"


def extract_categories(start_html: str, start_url: str) -> List[Category]:
    soup = BeautifulSoup(start_html, "lxml")
    categories: Dict[str, Category] = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if not is_edible_category_link(href):
            continue

        absolute_url = urljoin(start_url, href)
        label = normalize_text(a.get_text(" ", strip=True))

        if not label:
            parsed = urlparse(absolute_url)
            label = parse_qs(parsed.query).get("glossary", ["Unknown"])[0]
            label = unquote_plus(label)

        expected_count = extract_count_from_text(label)
        category_name = clean_category_name(label)

        if not category_name:
            continue

        categories[absolute_url] = Category(
            name=category_name,
            url=absolute_url,
            expected_count=expected_count,
        )

    return sorted(categories.values(), key=lambda c: c.name.lower())


def extract_plants_from_category(category: Category) -> List[PlantRecord]:
    html = fetch_html(category.url)
    soup = BeautifulSoup(html, "lxml")

    plants: Dict[str, PlantRecord] = {}

    table = soup.find("table", id="ContentPlaceHolder1_gvresults")

    if not table:
        print(f"  WARNING: Results table not found for {category.name}")
        return []

    rows = table.find_all("tr")

    for row in rows:
        cells = row.find_all("td")

        # Header row has <th>, data rows have 4 <td>.
        if len(cells) < 4:
            continue

        latin_cell = cells[0]
        common_cell = cells[1]
        edible_cell = cells[2]
        medicinal_cell = cells[3]

        link = latin_cell.find("a", href=True)

        if not link:
            continue

        href = link["href"]

        if not is_plant_profile_link(href):
            continue

        absolute_url = urljoin(category.url, href)
        plant_url = normalize_pfaf_plant_url(absolute_url)

        scientific_name = normalize_text(link.get_text(" ", strip=True))

        if not scientific_name:
            scientific_name = extract_scientific_name_from_url(plant_url)

        if not scientific_name:
            continue

        common_name = normalize_text(common_cell.get_text(" ", strip=True))
        edibility_rating = parse_int_or_none(edible_cell.get_text(" ", strip=True))
        medicinal_rating = parse_int_or_none(medicinal_cell.get_text(" ", strip=True))

        key = scientific_name.lower()

        plants[key] = PlantRecord(
            scientific_name=scientific_name,
            common_name=common_name,
            edibility_rating=edibility_rating,
            medicinal_rating=medicinal_rating,
            url=plant_url,
            categories=[category.name],
            source="PFAF",
            source_page=category.url,
        )

    return list(plants.values())


def merge_plant_records(
    existing: Dict[str, PlantRecord],
    new_records: List[PlantRecord],
) -> None:
    for record in new_records:
        key = record.scientific_name.lower()

        if key not in existing:
            existing[key] = record
            continue

        known = existing[key]

        known_categories: Set[str] = set(known.categories)
        known_categories.update(record.categories)
        known.categories = sorted(known_categories)

        if not known.common_name and record.common_name:
            known.common_name = record.common_name

        if known.edibility_rating is None and record.edibility_rating is not None:
            known.edibility_rating = record.edibility_rating

        if known.medicinal_rating is None and record.medicinal_rating is not None:
            known.medicinal_rating = record.medicinal_rating


def write_plants_csv(records: List[PlantRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "scientific_name",
                "common_name",
                "url",
                "categories",
                "category_count",
                "edibility_rating",
                "medicinal_rating",
                "source",
            ],
        )

        writer.writeheader()

        for record in records:
            writer.writerow(
                {
                    "scientific_name": record.scientific_name,
                    "common_name": record.common_name,
                    "url": record.url,
                    "categories": "; ".join(record.categories),
                    "category_count": len(record.categories),
                    "edibility_rating": record.edibility_rating,
                    "medicinal_rating": record.medicinal_rating,
                    "source": record.source,
                }
            )


def write_plants_json(records: List[PlantRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = [asdict(record) for record in records]

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_categories_csv(
    categories: List[Category],
    actual_counts: Dict[str, int],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "category",
                "url",
                "expected_count_from_pfaf_page",
                "actual_extracted_count",
            ],
        )

        writer.writeheader()

        for category in categories:
            writer.writerow(
                {
                    "category": category.name,
                    "url": category.url,
                    "expected_count_from_pfaf_page": category.expected_count,
                    "actual_extracted_count": actual_counts.get(category.name, 0),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract edible plant names and links from PFAF.")

    parser.add_argument(
        "--start-url",
        default=START_URL,
        help="PFAF edible uses URL.",
    )

    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory.",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=REQUEST_DELAY_SECONDS,
        help="Delay between category requests in seconds.",
    )

    args = parser.parse_args()
    output_dir = Path(args.output_dir)

    print(f"Running crawler file: {Path(__file__).resolve()}")
    print(f"Fetching start page: {args.start_url}")

    start_html = fetch_html(args.start_url)
    categories = extract_categories(start_html, args.start_url)

    if not categories:
        raise RuntimeError("No edible category links found. The page structure may have changed.")

    print(f"Found edible categories: {len(categories)}")

    all_plants: Dict[str, PlantRecord] = {}
    actual_counts: Dict[str, int] = {}
    raw_plant_appearances = 0

    for index, category in enumerate(categories, start=1):
        print(f"[{index}/{len(categories)}] Crawling category: " f"{category.name} | expected={category.expected_count} | {category.url}")

        try:
            records = extract_plants_from_category(category)
        except Exception as exc:
            print(f"  ERROR: Failed category {category.name}: {exc}")
            actual_counts[category.name] = 0
            continue

        actual_counts[category.name] = len(records)
        raw_plant_appearances += len(records)

        merge_plant_records(all_plants, records)

        print(f"  extracted={len(records)} | " f"unique_total={len(all_plants)}")

        time.sleep(args.delay)

    sorted_records = sorted(
        all_plants.values(),
        key=lambda record: record.scientific_name.lower(),
    )

    plants_csv = output_dir / "pfaf_edible_plants.csv"
    plants_json = output_dir / "pfaf_edible_plants.json"
    categories_csv = output_dir / "pfaf_edible_categories.csv"

    write_plants_csv(sorted_records, plants_csv)
    write_plants_json(sorted_records, plants_json)
    write_categories_csv(categories, actual_counts, categories_csv)

    print("\nDONE")
    print(f"Raw plant appearances across categories: {raw_plant_appearances}")
    print(f"Unique plants extracted: {len(sorted_records)}")
    print(f"Plants CSV: {plants_csv}")
    print(f"Plants JSON: {plants_json}")
    print(f"Categories CSV: {categories_csv}")


if __name__ == "__main__":
    main()
