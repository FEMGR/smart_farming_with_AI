"""
Convert DB plant name to Prolog-safe atom.
Example:
"Bell Pepper" → bell_pepper
"Solanum lycopersicum" → solanum_lycopersicum
"""

# app/utils/prolog_normalizer.py

import os
import re
import subprocess
from typing import Dict

# --- Configuration for Prolog Path ---
CURRENT_FILE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(  # smart-farming-system
    os.path.dirname(  # backend
        os.path.dirname(os.path.dirname(CURRENT_FILE))  # app  # services (this level is missing in original)
    )
)
PROLOG_MAIN_PATH = os.path.join(PROJECT_ROOT, "logic_companion_planting", "main.pl")

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
    "ipomoea_batata": "sweet_potato",  # Added specific mapping for sweet potato scientific name
    "ipomoea_batatas": "sweet_potato",  # Added specific mapping for sweet potato scientific name
}

# --- Dynamic Scientific Name to Common Name Map (loaded from Prolog) ---
SCIENTIFIC_TO_COMMON_MAP: Dict[str, str] = {}


def _load_scientific_name_mappings():
    """
    Loads scientific name to common name mappings from Prolog's plant_fact.pl.
    This function runs a Prolog query to get all scientific_name/2 facts.
    """
    if SCIENTIFIC_TO_COMMON_MAP:  # Load only once
        return

    # Prolog query to extract all scientific_name facts
    # Example output: [common1-'scientific1',common2-'scientific2']
    query = "findall(Common-Scientific, scientific_name(Common, Scientific), List), write(List), halt."

    try:
        result = subprocess.run(
            ["swipl", "-s", PROLOG_MAIN_PATH, "-g", query, "-t", "halt"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(PROLOG_MAIN_PATH),
            check=True,  # Raise an exception for non-zero exit codes
        )
        output = result.stdout.strip()

        # Parse the Prolog list output
        # Expected format: [common1-'scientific1',common2-'scientific2']
        if output.startswith("[") and output.endswith("]"):
            output = output[1:-1]  # Remove brackets
            if not output:
                return

            # Split by the comma that separates pairs in a list [A-B, C-D]
            # We look for a comma followed by something that looks like the start of a pair
            raw_pairs = re.split(r",(?=[a-z_']+-)", output)

            for raw_pair in raw_pairs:
                if "-" in raw_pair:
                    # Prolog findall(Common-Scientific) results in Common-Scientific format
                    common_raw, scientific_raw = raw_pair.split("-", 1)
                    common_name = common_raw.strip("' ")
                    scientific_name = scientific_raw.strip("' ")

                    cleaned_scientific = clean_text(scientific_name)
                    SCIENTIFIC_TO_COMMON_MAP[cleaned_scientific] = common_name

    except subprocess.CalledProcessError as e:
        print(f"Error loading scientific name mappings from Prolog: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred during Prolog mapping load: {e}")


# Load mappings when the module is imported
_load_scientific_name_mappings()


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


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

    # Prioritize common name from species if available
    if plant.get("species") and plant["species"].get("common_name"):
        candidates.append(plant["species"]["common_name"])
    # Then the general plant name
    if plant.get("name"):
        candidates.append(plant["name"])
    # Then scientific name from species
    if plant.get("species") and plant["species"].get("scientific_name"):
        candidates.append(plant["species"]["scientific_name"])

    fallback = None

    for name in candidates:
        cleaned = clean_text(name)

        # 1. Strong match in static NORMALIZATION_MAP
        if cleaned in NORMALIZATION_MAP:
            return NORMALIZATION_MAP[cleaned]

        # 2. Match against dynamically loaded scientific name mappings
        if cleaned in SCIENTIFIC_TO_COMMON_MAP:
            return SCIENTIFIC_TO_COMMON_MAP[cleaned]

        # 3. Otherwise store normalized version as fallback
        normalized = normalize_tokens(cleaned)
        if not fallback:
            fallback = normalized

    return fallback or ""
