# scripts/enriched_generate_growth_facts.py

"""
Generate merged plant growth facts for Prolog.

Sources:
1. Iowa State University Extension
   - germination days
   - light/dark germination requirement
   - inferred sowing depth

2. Wisconsin Horticulture Extension
   - minimum soil temperature
   - optimum soil temperature
   - viable germination temperature range

3. RHS Germination Guide
   - genus-level germination notes
   - stratification requirement
   - special treatments
   - light/surface sowing notes

Also reads:
    logic_companion_planting/base/plant_taxonomy_fact.pl

Output:
    logic_companion_planting/data/growth_facts.pl

Run:
    python scripts/generate_growth_facts.py

Install:
    pip install requests beautifulsoup4 pypdf
"""

from __future__ import annotations

import io
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

try:
    from pypdf import PdfReader
except ModuleNotFoundError:
    from PyPDF2 import PdfReader


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TAXONOMY_FILE = PROJECT_ROOT / "logic_companion_planting" / "base" / "plant_taxonomy.pl"

OUTPUT_FILE = PROJECT_ROOT / "logic_companion_planting" / "data" / "growth_facts_02.pl"


# =========================================================
# SOURCE URLS
# =========================================================

IOWA_URL = "https://yardandgarden.extension.iastate.edu/how-to/" "germination-requirements-annuals-and-vegetables"

WISCONSIN_URL = "https://hort.extension.wisc.edu/articles/" "when-is-the-right-time-to-plant-vegetable-seeds-check-soil-temperature/"

RHS_HTML_GUIDE_URL = "https://www.rhs.org.uk/membership/rhs-members-seed-scheme/germination-guide"

RHS_PDF_GUIDE_URL = "https://www.rhs.org.uk/membership/pdfs/seed-scheme/" "harvested-seed-germination-requirements.pdf"


# =========================================================
# REQUEST CONFIG
# =========================================================

HEADERS = {"User-Agent": ("Mozilla/5.0 SmartUrbanFarmingResearchBot/1.0 " "(educational plant-growth fact extraction)")}

TIMEOUT = 40
SOURCE_DELAY_SECONDS = 1.0


# =========================================================
# DATA MODELS
# =========================================================


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

    scientific_name: Optional[str] = None
    genus: Optional[str] = None
    family: Optional[str] = None

    fact_scope: str = "common_crop"


@dataclass
class RHSGenusFact:
    rhs_name: str
    rhs_genus: str

    germination_days_min: Optional[int] = None
    germination_days_max: Optional[int] = None
    germination_light: Optional[str] = None

    stratification_required: bool = False
    stratification_days_min: Optional[int] = None
    stratification_days_max: Optional[int] = None

    treatments: set[str] = field(default_factory=set)

    source_name: str = "RHS Germination Guide"
    source_url: str = ""
    confidence: str = "medium"


# =========================================================
# GENERAL HELPERS
# =========================================================


def fetch_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


def fetch_text(url: str) -> str:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text("\n", strip=True)
    return normalize_text(text)


def fetch_bytes(url: str) -> bytes:
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.content


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
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

    # Remove footnotes.
    name = name.replace("*", "")
    name = name.replace("†", "")

    # Normalize punctuation.
    name = name.replace("&", " and ")
    name = name.replace("/", " ")
    name = name.replace("-", " ")

    # Remove unsafe characters.
    name = re.sub(r"[^A-Za-z0-9\s]", "", name)

    name = re.sub(r"\s+", " ", name).strip().lower()

    return name.replace(" ", "_")


def prolog_quote(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def prolog_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, str):
        return value

    return str(value)


def fact_line(predicate: str, plant: str, value) -> str:
    return f"{predicate}({plant}, {prolog_value(value)})."


def add_unique_treatment(fact: PlantGrowthFact, treatment: str) -> None:
    if treatment not in fact.special_treatment:
        fact.special_treatment.append(treatment)


# =========================================================
# TAXONOMY PARSER
# =========================================================


def load_taxonomy_facts() -> dict[str, dict[str, str]]:
    """
    Load taxonomy facts from Prolog.

    Reads:
        accepted_scientific_name(Plant, 'Scientific name').
        genus(Plant, genus).
        family(Plant, family).
    """

    taxonomy: dict[str, dict[str, str]] = {}

    if not TAXONOMY_FILE.exists():
        print(f"WARNING: taxonomy file not found: {TAXONOMY_FILE}")
        return taxonomy

    text = TAXONOMY_FILE.read_text(encoding="utf-8")

    sci_pattern = re.compile(r"accepted_scientific_name\(([^,]+),\s*'([^']+)'\)\.")

    genus_pattern = re.compile(r"genus\(([^,]+),\s*([^)]+)\)\.")

    family_pattern = re.compile(r"family\(([^,]+),\s*([^)]+)\)\.")

    for plant, scientific_name in sci_pattern.findall(text):
        plant = plant.strip()
        taxonomy.setdefault(plant, {})["scientific_name"] = scientific_name.strip()

    for plant, genus in genus_pattern.findall(text):
        plant = plant.strip()
        taxonomy.setdefault(plant, {})["genus"] = genus.strip().lower()

    for plant, family in family_pattern.findall(text):
        plant = plant.strip()
        taxonomy.setdefault(plant, {})["family"] = family.strip().lower()

    return taxonomy


def apply_taxonomy_to_growth_facts(
    facts: dict[str, PlantGrowthFact],
    taxonomy: dict[str, dict[str, str]],
) -> dict[str, PlantGrowthFact]:
    """
    Add scientific_name, genus, and family to growth facts.
    """

    missing_taxonomy = []

    for plant, fact in facts.items():
        taxon = taxonomy.get(plant)

        if not taxon:
            missing_taxonomy.append(plant)
            continue

        fact.scientific_name = taxon.get("scientific_name")
        fact.genus = taxon.get("genus")
        fact.family = taxon.get("family")

    if missing_taxonomy:
        print(f"Growth facts without taxonomy match: {len(missing_taxonomy)}")
        print("Examples:", ", ".join(missing_taxonomy[:15]))

    return facts


# =========================================================
# IOWA PARSER
# =========================================================


def map_iowa_light_requirement(code: str) -> tuple[str, Optional[float], list[str]]:
    """
    Iowa definitions:
        L   = light required; press into medium, do not cover
        D   = darkness required; cover with medium
        L-D = lightly cover seed

    Sowing depth is inferred:
        L   -> 0.0 cm
        D   -> approx 0.95 cm, from 1/4 to 1/2 inch guidance
        L-D -> approx 0.3 cm
    """

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

    return (
        "unknown",
        None,
        ["unknown_light_requirement"],
    )


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
        minimum_soil_temp_c=source_fact.minimum_soil_temp_c,
        optimum_soil_temp_c=source_fact.optimum_soil_temp_c,
        viable_temp_min_c=source_fact.viable_temp_min_c,
        viable_temp_max_c=source_fact.viable_temp_max_c,
        fact_scope=source_fact.fact_scope,
    )

    facts[alias] = copied


def parse_iowa_facts() -> dict[str, PlantGrowthFact]:
    """
    Parse Iowa State Extension germination facts.

    Expected visible row pattern:
        Tomato 70-75 D 6-12 5-7

    Final weeks column may be absent for direct-sown vegetables.
    """

    text = fetch_text(IOWA_URL)

    facts: dict[str, PlantGrowthFact] = {}

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

    ignored = {
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

    # Helps fix cases where page text includes leftover header text.
    known_name_cleanup = re.compile(
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
        flags=re.IGNORECASE,
    )

    for match in row_pattern.finditer(text):
        raw_name = match.group("name").strip()

        cleanup_match = known_name_cleanup.match(raw_name)

        if cleanup_match:
            raw_name = cleanup_match.group(1)

        plant_atom = normalize_plant_name(raw_name)

        if not plant_atom:
            continue

        if plant_atom in ignored:
            continue

        if len(plant_atom) > 60:
            continue

        days_min, days_max = parse_int_range(match.group("days"))

        light, sowing_depth_cm, treatments = map_iowa_light_requirement(match.group("light"))

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
            fact_scope="common_crop",
        )

        fact.source_names.add("Iowa State University Extension")
        fact.source_urls.add(IOWA_URL)

        facts[plant_atom] = fact

        # Aliases matching your KB style.
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

        if plant_atom == "beets":
            add_alias(facts, fact, "beet")

    return facts


# =========================================================
# WISCONSIN PARSER
# =========================================================


def parse_wisconsin_temperature_facts(
    facts: dict[str, PlantGrowthFact],
) -> dict[str, PlantGrowthFact]:
    """
    Parse Wisconsin soil temperature table.

    Expected row:
        Tomato 70° F 85° F 50-95° F
    """

    text = fetch_text(WISCONSIN_URL)

    row_pattern = re.compile(
        r"(?P<name>[A-Z][A-Za-z\s]+?)"
        r"\s+"
        r"(?P<minimum>\d{2})°?\s*F"
        r"\s+"
        r"(?P<optimum>\d{2,3})°?\s*F"
        r"\s+"
        r"(?P<viable_min>\d{2})-(?P<viable_max>\d{2,3})°?\s*F"
    )

    known_name_cleanup = re.compile(
        r".*?(Beets|Carrots|Lettuce|Parsley|Radish|Spinach|"
        r"Asparagus|Peas|Turnip|Cabbage|Cauliflower|Corn|"
        r"Swiss chard|Onion|Celery|Cucumber|Pepper|Cantaloupe|"
        r"Squash|Tomato|Beans)$",
        flags=re.IGNORECASE,
    )

    for match in row_pattern.finditer(text):
        raw_name = match.group("name").strip()

        cleanup_match = known_name_cleanup.match(raw_name)

        if cleanup_match:
            raw_name = cleanup_match.group(1)

        plant_atom = normalize_plant_name(raw_name)

        if not plant_atom:
            continue

        if len(plant_atom) > 40:
            continue

        minimum_f = float(match.group("minimum"))
        optimum_f = float(match.group("optimum"))
        viable_min_f = float(match.group("viable_min"))
        viable_max_f = float(match.group("viable_max"))

        if plant_atom not in facts:
            facts[plant_atom] = PlantGrowthFact(
                plant_name=plant_atom,
                confidence="medium",
                fact_scope="common_crop",
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

        # Aliases.
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

        if plant_atom == "beets":
            add_alias(facts, fact, "beet")

    return facts


# =========================================================
# RHS PARSING HELPERS
# =========================================================


def rhs_key_from_name(raw_name: str) -> str:
    """
    RHS entries are botanical names.
    Use first word as genus.

    Example:
        Allium cepa -> allium
        Digitalis grandiflora -> digitalis
    """

    clean = re.sub(r"\([^)]*\)", "", raw_name).strip()
    clean = re.sub(r"[^A-Za-z\s-]", "", clean)
    parts = clean.split()

    if not parts:
        return ""

    return parts[0].lower()


def parse_rhs_days(note: str) -> tuple[Optional[int], Optional[int]]:
    lower = note.lower()

    explicit = re.search(r"(\d+)\s*-\s*(\d+)\s*days", lower)
    if explicit:
        return int(explicit.group(1)), int(explicit.group(2))

    single = re.search(r"(\d+)\s*days", lower)
    if single:
        value = int(single.group(1))
        return value, value

    if "few weeks" in lower:
        return 21, 42

    if "up to 1 year" in lower or "up to one year" in lower:
        return 30, 365

    if "up to 2 years" in lower or "up to two years" in lower:
        return 30, 730

    return None, None


def parse_stratification_days(note: str) -> tuple[int, int]:
    lower = note.lower()

    explicit = re.search(r"(\d+)\s*-\s*(\d+)\s*days", lower)
    if explicit:
        return int(explicit.group(1)), int(explicit.group(2))

    single = re.search(r"(\d+)\s*days", lower)
    if single:
        value = int(single.group(1))
        return value, value

    if "few weeks" in lower:
        return 21, 42

    if "warm stratification" in lower and "cold" in lower:
        return 60, 120

    if "cold moist stratification" in lower:
        return 30, 60

    if "cold, moist stratification" in lower:
        return 30, 60

    if "stratification" in lower:
        return 30, 60

    return 0, 0


def detect_rhs_light_requirement(note: str) -> Optional[str]:
    lower = note.lower()

    if "surface sow" in lower:
        return "light_required"

    if "requires light" in lower:
        return "light_required"

    if "need light" in lower:
        return "light_required"

    if "leave seeds uncovered" in lower:
        return "light_required"

    if "lightly cover" in lower:
        return "lightly_cover"

    if "cover seed" in lower or "cover seeds" in lower:
        return "darkness_required"

    return None


def detect_rhs_treatments(note: str) -> set[str]:
    lower = note.lower()
    treatments: set[str] = set()

    if "cold moist stratification" in lower or "cold, moist stratification" in lower:
        treatments.add("cold_moist_stratification")

    if "warm stratification" in lower:
        treatments.add("warm_stratification")

    if "warm stratification" in lower and "cold" in lower:
        treatments.add("warm_then_cold_stratification")

    if "outside over winter" in lower or "leave outside over winter" in lower:
        treatments.add("outdoor_winter_stratification")

    if "surface sow" in lower:
        treatments.add("surface_sow")

    if "requires light" in lower or "need light" in lower:
        treatments.add("requires_light_to_germinate")

    if "leave seeds uncovered" in lower:
        treatments.add("leave_seed_uncovered")

    if "lightly cover" in lower:
        treatments.add("lightly_cover_seed")

    if "slow and irregular" in lower:
        treatments.add("slow_irregular_germination")

    if "erratic" in lower:
        treatments.add("erratic_germination")

    if "up to 1 year" in lower or "up to one year" in lower:
        treatments.add("very_slow_germination_up_to_one_year")

    if "up to 2 years" in lower or "up to two years" in lower:
        treatments.add("very_slow_germination_up_to_two_years")

    if "scarification" in lower:
        treatments.add("scarification")

    if "soak" in lower:
        treatments.add("pre_soak_seed")

    return treatments


def merge_rhs_genus_fact(
    rhs_facts: dict[str, RHSGenusFact],
    genus: str,
    rhs_name: str,
    note_text: str,
    source_url: str,
) -> None:
    lower = note_text.lower()

    has_useful_growth_info = (
        "stratification" in lower
        or "surface sow" in lower
        or "lightly cover" in lower
        or "requires light" in lower
        or "need light" in lower
        or "leave seeds uncovered" in lower
        or "days" in lower
        or "slow" in lower
        or "erratic" in lower
        or "scarification" in lower
        or "soak" in lower
    )

    if not has_useful_growth_info:
        return

    germ_min, germ_max = parse_rhs_days(note_text)
    light = detect_rhs_light_requirement(note_text)
    treatments = detect_rhs_treatments(note_text)

    strat_required = "stratification" in lower
    strat_min = None
    strat_max = None

    if strat_required:
        strat_min, strat_max = parse_stratification_days(note_text)

    existing = rhs_facts.get(genus)

    if not existing:
        rhs_facts[genus] = RHSGenusFact(
            rhs_name=rhs_name,
            rhs_genus=genus,
            germination_days_min=germ_min,
            germination_days_max=germ_max,
            germination_light=light,
            stratification_required=strat_required,
            stratification_days_min=strat_min,
            stratification_days_max=strat_max,
            treatments=treatments,
            source_url=source_url,
            confidence="medium",
        )
        return

    # Merge, preferring existing but filling missing data.
    if existing.germination_days_min is None and germ_min is not None:
        existing.germination_days_min = germ_min

    if existing.germination_days_max is None and germ_max is not None:
        existing.germination_days_max = germ_max

    if existing.germination_light is None and light is not None:
        existing.germination_light = light

    if strat_required:
        existing.stratification_required = True

    if existing.stratification_days_min is None and strat_min is not None:
        existing.stratification_days_min = strat_min

    if existing.stratification_days_max is None and strat_max is not None:
        existing.stratification_days_max = strat_max

    existing.treatments.update(treatments)


# =========================================================
# RHS HTML PARSER
# =========================================================


def parse_rhs_html_facts() -> dict[str, RHSGenusFact]:
    """
    Parse RHS HTML germination guide.
    """

    html = fetch_html(RHS_HTML_GUIDE_URL)
    soup = BeautifulSoup(html, "html.parser")

    rhs_facts: dict[str, RHSGenusFact] = {}

    headings = soup.find_all(["h2", "h3", "h4", "h5"])

    for heading in headings:
        title = heading.get_text(" ", strip=True)
        genus = rhs_key_from_name(title)

        if not genus:
            continue

        notes: list[str] = []

        for sibling in heading.find_next_siblings():
            if sibling.name in ["h2", "h3", "h4", "h5"]:
                break

            text = sibling.get_text(" ", strip=True)

            if text:
                notes.append(text)

        note_text = normalize_text(" ".join(notes))

        if not note_text:
            continue

        merge_rhs_genus_fact(
            rhs_facts=rhs_facts,
            genus=genus,
            rhs_name=title,
            note_text=note_text,
            source_url=RHS_HTML_GUIDE_URL,
        )

    return rhs_facts


# =========================================================
# RHS PDF PARSER
# =========================================================


def extract_rhs_pdf_text() -> str:
    pdf_bytes = fetch_bytes(RHS_PDF_GUIDE_URL)
    reader = PdfReader(io.BytesIO(pdf_bytes))

    pages_text: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages_text.append(page_text)

    return normalize_text("\n".join(pages_text))


def parse_rhs_pdf_facts() -> dict[str, RHSGenusFact]:
    """
    Parse RHS harvested seed germination requirements PDF.

    PDF parsing is heuristic, so RHS should be treated as genus-level enrichment.
    """

    text = extract_rhs_pdf_text()
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    rhs_facts: dict[str, RHSGenusFact] = {}

    current_name: Optional[str] = None
    current_notes: list[str] = []

    entry_start_pattern = re.compile(r"^([A-Z][a-z]+)\b")

    def flush_current() -> None:
        if not current_name or not current_notes:
            return

        note_text = normalize_text(" ".join(current_notes))
        genus = rhs_key_from_name(current_name)

        if not genus:
            return

        merge_rhs_genus_fact(
            rhs_facts=rhs_facts,
            genus=genus,
            rhs_name=current_name,
            note_text=note_text,
            source_url=RHS_PDF_GUIDE_URL,
        )

    for line in lines:
        lower = line.lower()

        if lower.startswith("genus temperature"):
            continue

        start_match = entry_start_pattern.match(line)

        looks_like_entry = start_match is not None and (
            "ºc" in lower or "°c" in lower or "days" in lower or "stratification" in lower or "sow" in lower or "germination" in lower
        )

        if looks_like_entry:
            flush_current()

            current_name = start_match.group(1)
            current_notes = [line]
        else:
            if current_name:
                current_notes.append(line)

    flush_current()

    return rhs_facts


# =========================================================
# RHS MERGE
# =========================================================


def merge_rhs_facts_by_genus(
    facts: dict[str, PlantGrowthFact],
    rhs_facts: dict[str, RHSGenusFact],
) -> dict[str, PlantGrowthFact]:
    """
    Merge RHS genus-level facts into existing plant facts.

    Rules:
    - Do not overwrite Iowa germination days unless missing.
    - Do not overwrite Iowa light requirement unless missing.
    - Add RHS stratification facts because Iowa/Wisconsin usually do not cover it.
    - Mark RHS match as genus-level treatment.
    """

    matched_count = 0

    for plant, fact in facts.items():
        if not fact.genus:
            continue

        rhs = rhs_facts.get(fact.genus.lower())

        if not rhs:
            continue

        matched_count += 1

        # Fill missing germination days only.
        if fact.germination_days_min is None and rhs.germination_days_min is not None:
            fact.germination_days_min = rhs.germination_days_min

        if fact.germination_days_max is None and rhs.germination_days_max is not None:
            fact.germination_days_max = rhs.germination_days_max

        # Fill missing light requirement only.
        if fact.germination_light is None and rhs.germination_light is not None:
            fact.germination_light = rhs.germination_light

        # Add RHS stratification.
        if rhs.stratification_required:
            fact.stratification_required = True
            fact.stratification_days_min = rhs.stratification_days_min or 30
            fact.stratification_days_max = rhs.stratification_days_max or 60

        for treatment in rhs.treatments:
            add_unique_treatment(fact, treatment)

        add_unique_treatment(fact, f"rhs_genus_match_{fact.genus}")

        fact.source_names.add(f"RHS Germination Guide genus {rhs.rhs_name}")
        fact.source_urls.add(rhs.source_url)

        # If Iowa/Wisconsin already gave high confidence, keep it.
        # Otherwise RHS genus match is medium.
        if fact.confidence != "high":
            fact.confidence = rhs.confidence

        fact.fact_scope = "species_plus_genus_enrichment"

    print(f"RHS genus matches merged into growth facts: {matched_count}")

    return facts


# =========================================================
# PROLOG GENERATION
# =========================================================


def generate_prolog(facts: dict[str, PlantGrowthFact]) -> str:
    lines: list[str] = []

    lines.append("% =========================================================")
    lines.append("% GENERATED PLANT GROWTH FACTS")
    lines.append("% =========================================================")
    lines.append("% Generated by scripts/generate_growth_facts.py")
    lines.append("% Do not edit manually.")
    lines.append("%")
    lines.append("% Sources:")
    lines.append(f"% - Iowa State University Extension: {IOWA_URL}")
    lines.append(f"% - Wisconsin Horticulture Extension: {WISCONSIN_URL}")
    lines.append(f"% - RHS HTML Germination Guide: {RHS_HTML_GUIDE_URL}")
    lines.append(f"% - RHS PDF Germination Guide: {RHS_PDF_GUIDE_URL}")
    lines.append("%")
    lines.append("% Notes:")
    lines.append("% - Iowa/Wisconsin facts are crop/common-name level.")
    lines.append("% - RHS facts are merged by genus using plant_taxonomy_fact.pl.")
    lines.append("% - RHS should be treated as genus-level enrichment.")
    lines.append("% =========================================================")
    lines.append("")

    for plant in sorted(facts.keys()):
        fact = facts[plant]

        lines.append("")
        lines.append("% ---------------------------------------------------------")
        lines.append(f"% {plant}")
        lines.append("% ---------------------------------------------------------")

        # Taxonomy
        if fact.scientific_name:
            lines.append(
                fact_line(
                    "accepted_scientific_name",
                    plant,
                    prolog_quote(fact.scientific_name),
                )
            )

        if fact.genus:
            lines.append(
                fact_line(
                    "genus",
                    plant,
                    fact.genus,
                )
            )

        if fact.family:
            lines.append(
                fact_line(
                    "family",
                    plant,
                    fact.family,
                )
            )

        lines.append(
            fact_line(
                "fact_scope",
                plant,
                fact.fact_scope,
            )
        )

        # Germination facts
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

        # Temperature facts
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

        # Treatments
        for treatment in sorted(set(fact.special_treatment)):
            lines.append(
                fact_line(
                    "special_treatment",
                    plant,
                    treatment,
                )
            )

        # Sources
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

    lines.append("")
    return "\n".join(lines)


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    print("Loading taxonomy facts...")
    taxonomy = load_taxonomy_facts()
    print(f"Taxonomy entries loaded: {len(taxonomy)}")

    print("Fetching Iowa State Extension germination facts...")
    facts = parse_iowa_facts()
    print(f"Iowa facts parsed: {len(facts)}")

    time.sleep(SOURCE_DELAY_SECONDS)

    print("Fetching Wisconsin Extension soil temperature facts...")
    facts = parse_wisconsin_temperature_facts(facts)
    print(f"Total facts after Wisconsin enrichment: {len(facts)}")

    print("Applying taxonomy to growth facts...")
    facts = apply_taxonomy_to_growth_facts(facts, taxonomy)

    time.sleep(SOURCE_DELAY_SECONDS)

    print("Fetching RHS HTML germination facts...")
    rhs_html_facts = parse_rhs_html_facts()
    print(f"RHS HTML genus facts found: {len(rhs_html_facts)}")

    time.sleep(SOURCE_DELAY_SECONDS)

    print("Fetching RHS PDF germination facts...")
    rhs_pdf_facts = parse_rhs_pdf_facts()
    print(f"RHS PDF genus facts found: {len(rhs_pdf_facts)}")

    rhs_facts: dict[str, RHSGenusFact] = {}
    rhs_facts.update(rhs_pdf_facts)
    rhs_facts.update(rhs_html_facts)

    print(f"Total RHS genus facts: {len(rhs_facts)}")

    print("Merging RHS facts by genus...")
    facts = merge_rhs_facts_by_genus(facts, rhs_facts)

    if not facts:
        print("WARNING: No facts were parsed. Source page structures may have changed.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    prolog_output = generate_prolog(facts)
    OUTPUT_FILE.write_text(prolog_output, encoding="utf-8")

    print("Generated merged growth facts:")
    print(f"  {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
