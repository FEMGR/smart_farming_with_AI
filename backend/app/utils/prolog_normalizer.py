"""
Convert DB plant name to Prolog-safe atom.
Example:
"Bell Pepper" → bell_pepper
"Solanum lycopersicum" → solanum_lycopersicum
"""

# app/utils/prolog_normalizer.py

import re
from typing import Dict
from pathlib import Path

# --- Configuration for Prolog Path ---
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]
PROLOG_DATA_PATH = PROJECT_ROOT / "logic_companion_planting" / "data"

# --- Static Normalization Map ---
NORMALIZATION_MAP = {
    "tomatoes": "tomato",
    "cucumbers": "cucumber",
    "bell_pepper": "pepper",
    "chili_pepper": "pepper",
    "aubergine": "eggplant",
    "ornamental_cabbage": "cabbage",
    "romanesco_broccoli": "broccoli",
    "tropaeolum_group": "nasturtium",
    "taraxacum_officinale": "dandelion",
    "canada_wild_rye": "rye",
    "wild_ginger": "ginger",
    "decorative_dahlia": "dahlia",
    "tree_form_pee_gee_hydrangea": "hydrangea",
    "oregon_grape_holly": "grape",
    "lobelia_cardinali_fried_green_tomato": "tomato",
    "ipomoea_batata": "sweet_potato",
    "ipomoea_batatas": "sweet_potato",
    "florida_lettuce": "lettuce",
    "lactuca_floridana": "lettuce",
}

# --- Dynamic maps loaded from the local Prolog facts ---
CANONICAL_PLANT_ATOMS: set[str] = set()
ALIAS_TO_COMMON_MAP: Dict[str, str] = {}
SCIENTIFIC_TO_COMMON_MAP: Dict[str, str] = {}
GENUS_TO_COMMON_MAP: Dict[str, str] = {}


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _load_prolog_fact_mappings():
    """Load canonical plant, alias, and scientific-name mappings from Prolog fact files."""
    if CANONICAL_PLANT_ATOMS:
        return

    plant_fact_path = PROLOG_DATA_PATH / "plant_fact.pl"
    alias_fact_path = PROLOG_DATA_PATH / "alias_fact.pl"

    try:
        plant_fact = plant_fact_path.read_text(encoding="utf-8")
    except OSError:
        plant_fact = ""

    for match in re.finditer(r"^\s*plant\(([^)]+)\)\.", plant_fact, re.MULTILINE):
        atom = clean_text(match.group(1).strip("' "))
        if atom:
            CANONICAL_PLANT_ATOMS.add(atom)

    for match in re.finditer(r"^\s*alias\(([^,]+),\s*([^)]+)\)\.", plant_fact, re.MULTILINE):
        alias = clean_text(match.group(1).strip("' "))
        canonical = clean_text(match.group(2).strip("' "))
        if alias and canonical:
            ALIAS_TO_COMMON_MAP[alias] = canonical

    for match in re.finditer(r"^\s*scientific_name\(([^,]+),\s*'([^']+)'\)\.", plant_fact, re.MULTILINE):
        canonical = clean_text(match.group(1).strip("' "))
        scientific = clean_text(match.group(2))
        if canonical and scientific:
            SCIENTIFIC_TO_COMMON_MAP[scientific] = canonical
            genus = scientific.split("_", 1)[0]
            GENUS_TO_COMMON_MAP.setdefault(genus, canonical)

    try:
        alias_fact = alias_fact_path.read_text(encoding="utf-8")
    except OSError:
        alias_fact = ""

    for match in re.finditer(r"^\s*alias\((.+?),\s*([^)]+)\)\.", alias_fact, re.MULTILINE):
        alias = clean_text(match.group(1).strip("' "))
        canonical = clean_text(match.group(2).strip("' "))
        if alias and canonical:
            ALIAS_TO_COMMON_MAP[alias] = canonical


def resolve_cleaned_candidate(cleaned: str) -> str | None:
    if not cleaned:
        return None

    if cleaned in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[cleaned]

    if cleaned in CANONICAL_PLANT_ATOMS:
        return cleaned

    if cleaned in ALIAS_TO_COMMON_MAP:
        return ALIAS_TO_COMMON_MAP[cleaned]

    if cleaned in SCIENTIFIC_TO_COMMON_MAP:
        return SCIENTIFIC_TO_COMMON_MAP[cleaned]

    genus = cleaned.split("_", 1)[0]
    if genus in GENUS_TO_COMMON_MAP:
        return GENUS_TO_COMMON_MAP[genus]

    padded = f"_{cleaned}_"
    for atom in sorted(CANONICAL_PLANT_ATOMS, key=len, reverse=True):
        if f"_{atom}_" in padded:
            return atom

    return None


def singularize(word: str) -> str:
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("es"):
        return word[:-2]
    if word.endswith("s") and len(word) > 3:
        return word[:-1]
    return word


def normalize_tokens(name: str) -> str:
    tokens = name.split("_")
    tokens = [singularize(t) for t in tokens]
    return "_".join(tokens)


def to_prolog_atom(plant: dict) -> str:
    candidates = []

    _load_prolog_fact_mappings()

    # Prefer the user's chosen plant name. Perenual species may resolve to a related
    # botanical species that is too specific for the Prolog knowledge base.
    if plant.get("name"):
        candidates.append(plant["name"])
    if plant.get("species") and plant["species"].get("common_name"):
        candidates.append(plant["species"]["common_name"])
    if plant.get("species") and plant["species"].get("scientific_name"):
        candidates.append(plant["species"]["scientific_name"])

    fallback = None

    for name in candidates:
        cleaned = clean_text(name)

        resolved = resolve_cleaned_candidate(cleaned)
        if resolved:
            return resolved

        normalized = normalize_tokens(cleaned)
        if not fallback:
            fallback = normalized

    return fallback or ""
