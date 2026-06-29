"""
scripts/generate_growth_facts.py

Generates Prolog facts from:
- Iowa State Extension germination requirements
- Wisconsin Extension soil temperature guide

Run:
    python scripts/generate_growth_facts.py

Install:
    pip install requests beautifulsoup4
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup


IOWA_URL = "https://yardandgarden.extension.iastate.edu/how-to/" "germination-requirements-annuals-and-vegetables"

WISCONSIN_URL = "https://hort.extension.wisc.edu/articles/" "when-is-the-right-time-to-plant-vegetable-seeds-check-soil-temperature/"

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = PROJECT_ROOT / "logic_companion_planting" / "data" / "generated_growth_facts.pl"

HEADERS = {"User-Agent": ("Mozilla/5.0 SmartUrbanFarmingResearchBot/1.0 " "(educational plant-growth fact extraction)")}

TIMEOUT = 30


@dataclass
class PlantGrowthFact:
    plant_name: str

    germination_days_min: Optional[int] = None
    germination_days_max: Optional[int] = None
    germination_light: Optional[str] = None

    stratification_required: bool = False
    stratification_days_min: int = 0
    stratification_days_max: int = 0

    sowing_depth_cm: Optional[float] = None
    special_treatment: list[str] = field(default_factory=list)

    source_names: set[str] = field(default_factory=set)
    source_urls: set[str] = field(default_factory=set)

    confidence: str = "medium"

    minimum_soil_temp_c: Optional[float] = None
    optimum_soil_temp_c: Optional[float] = None
    viable_temp_min_c: Optional[float] = None
    viable_temp_max_c: Optional[float] = None


def fetch_text(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text("\n", strip=True)

    # Normalize ugly web spacing.
    text = text.replace("\xa0", " ")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("°", "°")

    return text


def normalize_spaces(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def fahrenheit_to_celsius(value_f: float) -> float:
    return round((value_f - 32) * 5 / 9, 1)


def parse_int_range(text: str) -> tuple[int, int]:
    text = text.strip()

    if "-" in text:
        left, right = text.split("-", 1)
        return int(left), int(right)

    value = int(text)
    return value, value


def normalize_plant_name(raw_name: str) -> str:
    name = raw_name.strip()

    # Remove scientific names in parentheses.
    name = re.sub(r"\([^)]*\)", "", name)

    # Remove Iowa footnotes.
    name = name.replace("*", "")
    name = name.replace("†", "")

    # Normalize punctuation.
    name = name.replace("&", " and ")
    name = name.replace("/", " ")
    name = name.replace("-", " ")

    # Remove remaining unsafe characters.
    name = re.sub(r"[^A-Za-z0-9\s]", "", name)

    name = re.sub(r"\s+", " ", name).strip().lower()

    return name.replace(" ", "_")


def prolog_quote(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def map_light_requirement(code: str) -> tuple[str, Optional[float], list[str]]:
    code = code.strip().upper()

    if code == "L":
        return (
            "light_required",
            0.0,
            ["surface_sow", "press_seed_into_medium", "do_not_cover"],
        )

    if code == "D":
        return (
            "darkness_required",
            0.95,
            ["cover_seed", "inferred_depth_from_1_4_to_1_2_inch"],
        )

    if code == "L-D":
        return (
            "lightly_cover",
            0.3,
            ["lightly_cover_seed", "keep_close_to_surface"],
        )

    return "unknown", None, ["unknown_light_requirement"]


def add_alias(
    facts: dict[str, PlantGrowthFact],
    source_fact: PlantGrowthFact,
    alias: str,
) -> None:
    copied = PlantGrowthFact(
        plant_name=alias,
        germination_days_min=source_fact.germination_days_min,
        germination_days_max=source_fact.germination_days_max,
        germination_light=source_fact.germination_light,
        stratification_required=source_fact.stratification_required,
        stratification_days_min=source_fact.stratification_days_min,
        stratification_days_max=source_fact.stratification_days_max,
        sowing_depth_cm=source_fact.sowing_depth_cm,
        special_treatment=source_fact.special_treatment.copy(),
        source_names=source_fact.source_names.copy(),
        source_urls=source_fact.source_urls.copy(),
        confidence=source_fact.confidence,
    )

    facts[alias] = copied


def parse_iowa_facts() -> dict[str, PlantGrowthFact]:
    text = fetch_text(IOWA_URL)
    text = normalize_spaces(text)

    facts: dict[str, PlantGrowthFact] = {}

    # Iowa rows may appear as:
    # Tomato 70-75 D 6-12 5-7
    # Beans 70-80 D 8-10
    #
    # The final weeks column exists for transplant crops but not direct-sown crops.
    row_pattern = re.compile(
        r"(?P<name>[A-Z][A-Za-z0-9'’.\-\s&]+?(?:\([^)]*\))?\*{0,2})"
        r"\s*"
        r"(?P<temp>\d{2}(?:-\d{2})?)"
        r"\s+"
        r"(?P<light>L-D|L|D)"
        r"\s+"
        r"(?P<days>\d+(?:-\d+)?)"
        r"(?:\s+(?P<weeks>\d+(?:-\d+)?))?"
    )

    ignored_prefixes = {
        "plant",
        "species",
        "germination",
        "temperature",
        "light",
        "requirements",
        "days",
        "weeks",
        "sowing",
        "to",
        "planting",
    }

    for match in row_pattern.finditer(text):
        raw_name = match.group("name").strip()

        # Clean accidental header fragments.
        raw_name = re.sub(
            r".*?(Ageratum|Snapdragon|Wax Begonia|Annual Aster|Vinca|"
            r"Cockscomb|Bachelor|Cosmos|Lisianthus|Globe Amaranth|"
            r"Sunflower|Strawflower|Impatiens|Annual Statice|Melampodium|"
            r"Four-O|Flowering Tobacco|Geranium|Petunia|Moss Rose|"
            r"Black-Eyed Susan|Red Salvia|Mealycup Sage|Creeping Zinnia|"
            r"Coleus|Dahlberg Daisy|Nasturtium|Zinnia|Onion|Dill|Kale|"
            r"Cauliflower|Cabbage|Broccoli|Brussels Sprouts|Pepper|"
            r"Watermelon|Muskmelon|Cucumber|Squash and Pumpkin|Tomato|"
            r"Basil|Parsley|Eggplant|Celery|Beans|Beets|Carrots|"
            r"Sweet Corn|Kohlrabi|Lettuce|Peas|Radish)",
            r"\1",
            raw_name,
            flags=re.IGNORECASE,
        )

        plant_atom = normalize_plant_name(raw_name)

        if not plant_atom:
            continue

        if plant_atom in ignored_prefixes:
            continue

        # Avoid obvious bad captures.
        if len(plant_atom) > 60:
            continue

        days_min, days_max = parse_int_range(match.group("days"))
        light, sowing_depth_cm, treatments = map_light_requirement(match.group("light"))

        fact = PlantGrowthFact(
            plant_name=plant_atom,
            germination_days_min=days_min,
            germination_days_max=days_max,
            germination_light=light,
            stratification_required=False,
            stratification_days_min=0,
            stratification_days_max=0,
            sowing_depth_cm=sowing_depth_cm,
            special_treatment=treatments,
            confidence="high",
        )

        fact.source_names.add("Iowa State University Extension")
        fact.source_urls.add(IOWA_URL)

        facts[plant_atom] = fact

        # Helpful aliases for your KB.
        if plant_atom == "squash_and_pumpkin":
            add_alias(facts, fact, "squash")
            add_alias(facts, fact, "pumpkin")

        if plant_atom == "sweet_corn":
            add_alias(facts, fact, "corn")

        if plant_atom == "pepper":
            add_alias(facts, fact, "bell_pepper")
            add_alias(facts, fact, "chili_pepper")

        if plant_atom == "beans":
            add_alias(facts, fact, "bean")
            add_alias(facts, fact, "beans_bush")
            add_alias(facts, fact, "beans_pole")
            add_alias(facts, fact, "bean_bush")
            add_alias(facts, fact, "bean_pole")

        if plant_atom == "peas":
            add_alias(facts, fact, "pea")
            add_alias(facts, fact, "pea_english")

    return facts


def parse_wisconsin_temperature_facts(
    facts: dict[str, PlantGrowthFact],
) -> dict[str, PlantGrowthFact]:
    text = fetch_text(WISCONSIN_URL)
    text = normalize_spaces(text)

    # Wisconsin has rows like:
    # Tomato 70° F 85° F 50-95° F
    row_pattern = re.compile(
        r"(?P<name>[A-Z][A-Za-z\s]+?)"
        r"\s+"
        r"(?P<minimum>\d{2})°?\s*F"
        r"\s+"
        r"(?P<optimum>\d{2,3})°?\s*F"
        r"\s+"
        r"(?P<viable_min>\d{2})-(?P<viable_max>\d{2,3})°?\s*F"
    )

    for match in row_pattern.finditer(text):
        raw_name = match.group("name").strip()

        # Skip accidental heading text.
        raw_name = re.sub(
            r".*?(Beets|Carrots|Lettuce|Parsley|Radish|Spinach|Asparagus|Peas|Turnip|Cabbage|Cauliflower|"
            r"Corn|Swiss chard|Onion|Celery|Cucumber|Pepper|Cantaloupe|Squash|Tomato|Beans)$",
            r"\1",
            raw_name,
        )

        plant_atom = normalize_plant_name(raw_name)

        if not plant_atom or len(plant_atom) > 40:
            continue

        minimum_f = float(match.group("minimum"))
        optimum_f = float(match.group("optimum"))
        viable_min_f = float(match.group("viable_min"))
        viable_max_f = float(match.group("viable_max"))

        if plant_atom not in facts:
            facts[plant_atom] = PlantGrowthFact(
                plant_name=plant_atom,
                confidence="medium",
            )

        fact = facts[plant_atom]

        fact.minimum_soil_temp_c = fahrenheit_to_celsius(minimum_f)
        fact.optimum_soil_temp_c = fahrenheit_to_celsius(optimum_f)
        fact.viable_temp_min_c = fahrenheit_to_celsius(viable_min_f)
        fact.viable_temp_max_c = fahrenheit_to_celsius(viable_max_f)

        fact.source_names.add("Wisconsin Horticulture Extension")
        fact.source_urls.add(WISCONSIN_URL)

        if fact.germination_days_min is not None:
            fact.confidence = "high"

        # Useful aliases.
        if plant_atom == "corn":
            add_alias(facts, fact, "sweet_corn")

        if plant_atom == "pepper":
            add_alias(facts, fact, "bell_pepper")
            add_alias(facts, fact, "chili_pepper")

        if plant_atom == "beans":
            add_alias(facts, fact, "bean")
            add_alias(facts, fact, "beans_bush")
            add_alias(facts, fact, "beans_pole")
            add_alias(facts, fact, "bean_bush")
            add_alias(facts, fact, "bean_pole")

        if plant_atom == "peas":
            add_alias(facts, fact, "pea")
            add_alias(facts, fact, "pea_english")

    return facts


def prolog_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, str):
        return value

    return str(value)


def fact_line(predicate: str, plant: str, value) -> str:
    return f"{predicate}({plant}, {prolog_value(value)})."


def generate_prolog(facts: dict[str, PlantGrowthFact]) -> str:
    lines: list[str] = []

    lines.append("% =========================================================")
    lines.append("% GENERATED PLANT GROWTH FACTS")
    lines.append("% =========================================================")
    lines.append("% Generated by scripts/generate_growth_facts.py")
    lines.append("% Do not edit manually.")
    lines.append("%")
    lines.append(f"% Iowa source: {IOWA_URL}")
    lines.append(f"% Wisconsin source: {WISCONSIN_URL}")
    lines.append("% =========================================================")
    lines.append("")

    for plant in sorted(facts.keys()):
        fact = facts[plant]

        lines.append("")
        lines.append("% ---------------------------------------------------------")
        lines.append(f"% {plant}")
        lines.append("% ---------------------------------------------------------")

        if fact.germination_days_min is not None:
            lines.append(
                fact_line(
                    "germination_days_min",
                    plant,
                    fact.germination_days_min,
                )
            )

        if fact.germination_days_max is not None:
            lines.append(
                fact_line(
                    "germination_days_max",
                    plant,
                    fact.germination_days_max,
                )
            )

        if fact.germination_light is not None:
            lines.append(
                fact_line(
                    "germination_light",
                    plant,
                    fact.germination_light,
                )
            )

        lines.append(
            fact_line(
                "stratification_required",
                plant,
                fact.stratification_required,
            )
        )

        lines.append(
            fact_line(
                "stratification_days_min",
                plant,
                fact.stratification_days_min,
            )
        )

        lines.append(
            fact_line(
                "stratification_days_max",
                plant,
                fact.stratification_days_max,
            )
        )

        if fact.sowing_depth_cm is not None:
            lines.append(
                fact_line(
                    "sowing_depth_cm",
                    plant,
                    fact.sowing_depth_cm,
                )
            )

        for treatment in sorted(set(fact.special_treatment)):
            lines.append(
                fact_line(
                    "special_treatment",
                    plant,
                    treatment,
                )
            )

        for source_name in sorted(fact.source_names):
            lines.append(
                fact_line(
                    "source_name",
                    plant,
                    prolog_quote(source_name),
                )
            )

        for source_url in sorted(fact.source_urls):
            lines.append(
                fact_line(
                    "source_url",
                    plant,
                    prolog_quote(source_url),
                )
            )

        lines.append(
            fact_line(
                "confidence",
                plant,
                fact.confidence,
            )
        )

        if fact.minimum_soil_temp_c is not None:
            lines.append(
                fact_line(
                    "minimum_soil_temp_c",
                    plant,
                    fact.minimum_soil_temp_c,
                )
            )

        if fact.optimum_soil_temp_c is not None:
            lines.append(
                fact_line(
                    "optimum_soil_temp_c",
                    plant,
                    fact.optimum_soil_temp_c,
                )
            )

        if fact.viable_temp_min_c is not None:
            lines.append(
                fact_line(
                    "viable_temp_min_c",
                    plant,
                    fact.viable_temp_min_c,
                )
            )

        if fact.viable_temp_max_c is not None:
            lines.append(
                fact_line(
                    "viable_temp_max_c",
                    plant,
                    fact.viable_temp_max_c,
                )
            )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    print("Fetching Iowa State Extension germination facts...")
    facts = parse_iowa_facts()
    print(f"Iowa facts parsed: {len(facts)}")

    time.sleep(1)

    print("Fetching Wisconsin Extension soil temperature facts...")
    facts = parse_wisconsin_temperature_facts(facts)
    print(f"Total facts after Wisconsin enrichment: {len(facts)}")

    if not facts:
        print("WARNING: No facts were parsed. The source page structure may have changed.")
        print("Try printing the fetched text from fetch_text() for debugging.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(generate_prolog(facts), encoding="utf-8")

    print("Generated Prolog facts:")
    print(f"  {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
