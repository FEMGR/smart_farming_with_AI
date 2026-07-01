"""
source_parse_patch_v4.py

PFAF parser helpers.

Major fix:
- Do NOT parse PFAF by whole-page flattened text first.
- Extract exact PFAF span IDs:
    ContentPlaceHolder1_txtSummary
    ContentPlaceHolder1_lblPhystatment
    ContentPlaceHolder1_txtEdibleUses
    ContentPlaceHolder1_txtMediUses
    ContentPlaceHolder1_txtOtherUses
    ContentPlaceHolder1_txtCultivationDetails
    ContentPlaceHolder1_txtPropagation
    ContentPlaceHolder1_lblKnownHazards

This prevents tomato from wrongly getting:
- edible leaf
- edible root
- edible flower
- root_tuber_crop

because those words appear in medicinal/cultivation/summary text, not the actual edible parts field.
"""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup


# =========================================================
# BASIC CLEANING
# =========================================================


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.replace("\xa0", " ")
    value = value.replace("â€”", "—")
    value = value.replace("â€“", "–")
    value = value.replace("â€˜", "'")
    value = value.replace("â€™", "'")
    value = value.replace("â€œ", '"')
    value = value.replace("â€", '"')
    value = re.sub(r"\s+", " ", value).strip()

    return value or None


def title_text(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title")
    return clean_text(title.get_text(" ")) if title else None


def page_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()

    return clean_text(soup.get_text(" ")) or ""


def is_search_page(text: str, title: str | None = None) -> bool:
    combined = f"{title or ''} {text[:1500]}".lower()

    return "search results for" in combined or "you searched for" in combined or "database search result" in combined


def source_relevance_score(text: str, plant: dict[str, Any]) -> float:
    low = text.lower()

    scientific = (plant.get("scientific_name") or "").lower()
    common = (plant.get("common_name") or "").lower()

    score = 0.0

    if scientific and scientific in low:
        score += 0.65

    if common and common in low:
        score += 0.15

    if "edible uses" in low:
        score += 0.05

    if "plant propagation" in low:
        score += 0.05

    if "cultivation details" in low:
        score += 0.05

    if "other uses" in low:
        score += 0.05

    return min(score, 1.0)


# =========================================================
# PFAF EXACT FIELD PARSING
# =========================================================

PFAF_IDS = {
    "display_latin_name": "ContentPlaceHolder1_lbldisplatinname",
    "common_name": "ContentPlaceHolder1_lblCommanName",
    "family": "ContentPlaceHolder1_lblFamily",
    "usda_hardiness": "ContentPlaceHolder1_lblUSDAhardiness",
    "known_hazards": "ContentPlaceHolder1_lblKnownHazards",
    "habitats": "ContentPlaceHolder1_txtHabitats",
    "range": "ContentPlaceHolder1_lblRange",
    "summary": "ContentPlaceHolder1_txtSummary",
    "physical_characteristics": "ContentPlaceHolder1_lblPhystatment",
    "synonyms": "ContentPlaceHolder1_lblSynonyms",
    "plant_habitats": "ContentPlaceHolder1_lblhabitats",
    "edible_uses": "ContentPlaceHolder1_txtEdibleUses",
    "medicinal_uses": "ContentPlaceHolder1_txtMediUses",
    "other_uses": "ContentPlaceHolder1_txtOtherUses",
    "special_uses": "ContentPlaceHolder1_txtSpecialUses",
    "cultivation": "ContentPlaceHolder1_txtCultivationDetails",
    "propagation": "ContentPlaceHolder1_txtPropagation",
    "other_names": "ContentPlaceHolder1_lblOtherNameText",
    "native_range": "ContentPlaceHolder1_lblFoundInText",
    "conservation_status": "ContentPlaceHolder1_lblConservationStatus",
}


def extract_span_text_by_id(soup: BeautifulSoup, element_id: str) -> str | None:
    element = soup.find(id=element_id)

    if not element:
        return None

    return clean_text(element.get_text(" "))


def extract_pfaf_sections_from_html(html: str) -> dict[str, str | None]:
    soup = BeautifulSoup(html, "html.parser")

    sections: dict[str, str | None] = {}

    for key, element_id in PFAF_IDS.items():
        sections[key] = extract_span_text_by_id(soup, element_id)

    return sections


def is_real_pfaf_plant_page(sections: dict[str, str | None]) -> bool:
    return bool(
        sections.get("display_latin_name")
        and (sections.get("edible_uses") or sections.get("cultivation") or sections.get("propagation") or sections.get("physical_characteristics"))
    )


# =========================================================
# NAME / IDENTITY HELPERS
# =========================================================


def is_generic_scientific_name(name: str | None) -> bool:
    if not name:
        return True

    low = name.lower().strip()

    generic_markers = [
        " spp",
        " sp.",
        " sp ",
        "species",
        "unknown",
        "various",
    ]

    return any(marker in low for marker in generic_markers)


def normalize_plant_atom(name: str) -> str:
    name = name.strip().lower()

    # Remove phrase noise before slugifying.
    noise_phrases = [
        "growing near",
        "near",
        "with",
        "and",
    ]

    for phrase in noise_phrases:
        if name.startswith(phrase + " "):
            name = name[len(phrase) :].strip()

    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")

    singular_map = {
        "tomatoes": "tomato",
        "raspberries": "raspberry",
        "gooseberries": "gooseberry",
        "potatoes": "potato",
        "brassicas": "brassica",
        "cabbages": "cabbage",
        "stinging_nettles": "stinging_nettle",
        "kohl_rabi": "kohlrabi",
    }

    return singular_map.get(name, name)


# =========================================================
# IDENTITY / SYNONYM EXTRACTION
# =========================================================


def split_common_names(raw: str | None) -> list[str]:
    """
    Converts:
        "Gotu Kola, Spadeleaf"

    Into:
        ["Gotu Kola", "Spadeleaf"]
    """
    text = clean_text(raw)

    if not text:
        return []

    names: list[str] = []

    for part in text.split(","):
        cleaned = clean_text(part)

        if cleaned:
            names.append(cleaned)

    return sorted(set(names), key=str.lower)


def parse_pfaf_synonyms(raw: str | None) -> list[str]:
    """
    Converts PFAF synonym text like:

        "Hydrocotyle asiatica. L. H. cordifolia. H. repanda."

    Into:

        [
          "Hydrocotyle asiatica",
          "Hydrocotyle cordifolia",
          "Hydrocotyle repanda"
        ]

    Notes:
    - PFAF sometimes includes author abbreviations like "L."
    - PFAF sometimes abbreviates the genus like "H. cordifolia"
    """
    text = clean_text(raw)

    if not text:
        return []

    # Remove common standalone botanical author abbreviations.
    # Example:
    # "Hydrocotyle asiatica. L. H. cordifolia."
    text = re.sub(r"\bL\.\s*", "", text)

    parts = [clean_text(part) for part in text.split(".")]
    parts = [part for part in parts if part]

    synonyms: list[str] = []
    last_genus: str | None = None

    for part in parts:
        tokens = part.split()

        if not tokens:
            continue

        first = tokens[0]

        # Full genus form:
        # Hydrocotyle asiatica
        if len(tokens) >= 2 and re.match(r"^[A-Z][a-z]+$", first):
            last_genus = first
            synonyms.append(" ".join(tokens))
            continue

        # Abbreviated genus form:
        # H. cordifolia
        if len(tokens) >= 2 and re.match(r"^[A-Z]\.$", first) and last_genus and last_genus.startswith(first[0]):
            expanded = f"{last_genus} {' '.join(tokens[1:])}"
            synonyms.append(expanded)
            continue

    return sorted(set(synonyms), key=str.lower)


def extract_identity_from_pfaf_sections(
    sections: dict[str, str | None],
    fallback_common_name: str | None = None,
    fallback_scientific_name: str | None = None,
) -> dict[str, Any]:
    """
    Builds a clean identity block from exact PFAF section IDs.
    """
    raw_common_name = sections.get("common_name")
    raw_synonyms = sections.get("synonyms")
    raw_other_names = sections.get("other_names")
    raw_display_latin = sections.get("display_latin_name")

    common_names = split_common_names(raw_common_name)
    other_names = split_common_names(raw_other_names)
    synonyms = parse_pfaf_synonyms(raw_synonyms)

    scientific_name = clean_text(fallback_scientific_name)

    if not scientific_name and raw_display_latin:
        # Example:
        # "Centella asiatica - (L.)Urb."
        scientific_name = clean_text(raw_display_latin.split(" - ")[0])

    genus = None
    if scientific_name:
        genus = scientific_name.split()[0]

    all_common_names = sorted(
        set(common_names + other_names),
        key=str.lower,
    )

    return {
        "common_name": (all_common_names[0] if all_common_names else clean_text(fallback_common_name)),
        "scientific_name": scientific_name,
        "genus": genus,
        "family": sections.get("family"),
        "synonyms": synonyms,
        "common_names": all_common_names,
    }


# =========================================================
# EDIBLE / USE EXTRACTION
# =========================================================


def extract_pfaf_labeled_values(section: str | None, label: str) -> list[str]:
    """
    Extract values after labels like:

    Edible Parts: Fruit Oil Seed
    Edible Uses: Drink Oil

    Stops at the next known label or a sentence start.
    """
    if not section:
        return []

    # Normalize spaces
    text = clean_text(section) or ""

    # Examples:
    # "Edible Parts: Fruit Oil Seed Edible Uses: Drink Oil Fruit - raw..."
    pattern = rf"{re.escape(label)}\s*:\s*(.*?)(?:Edible Uses\s*:|Medicinal Uses\s*:|Other Uses\s*:|[A-Z][a-z]+ - |\Z)"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return []

    raw = match.group(1)

    # Remove reference brackets and punctuation
    raw = re.sub(r"\[[^\]]+\]", " ", raw)
    raw = re.sub(r"[^A-Za-z ,/_-]", " ", raw)
    raw = clean_text(raw) or ""

    values = []

    allowed = {
        "fruit": "fruit",
        "oil": "oil",
        "seed": "seed",
        "leaves": "leaf",
        "leaf": "leaf",
        "flowers": "flower",
        "flower": "flower",
        "root": "root",
        "roots": "root",
        "stem": "stem",
        "stems": "stem",
        "shoot": "stem",
        "shoots": "stem",
        "bulb": "bulb",
        "bulbs": "bulb",
        "tuber": "tuber",
        "tubers": "tuber",
        "rhizome": "rhizome",
        "rhizomes": "rhizome",
        "drink": "drink",
        "tea": "tea",
        "condiment": "condiment",
    }

    # Also split by capital words because PFAF text often becomes "Fruit Oil Seed"
    words = raw.split()

    for word in words:
        key = word.strip().lower()

        if key in allowed:
            values.append(allowed[key])

    return sorted(set(values))


def extract_edible_parts_from_pfaf(edible_section: str | None) -> list[str]:
    """
    Primary method: use explicit PFAF 'Edible Parts:' field.

    This avoids tomato getting leaf/root from medicinal text.
    """
    explicit = extract_pfaf_labeled_values(edible_section, "Edible Parts")

    if explicit:
        # keep only actual parts, not use types
        return sorted(
            part
            for part in explicit
            if part
            in {
                "leaf",
                "flower",
                "seed",
                "fruit",
                "root",
                "tuber",
                "rhizome",
                "stem",
                "bulb",
                "pod",
                "sap",
                "oil",
            }
        )

    # fallback: only scan edible section, never whole page
    if not edible_section:
        return []

    low = edible_section.lower()
    parts = []

    rules = {
        "leaf": ["leaves", "leaf"],
        "flower": ["flowers", "flower", "flowering tops"],
        "seed": ["seeds", "seed"],
        "fruit": ["fruits", "fruit"],
        "root": ["roots", "root"],
        "tuber": ["tubers", "tuber"],
        "rhizome": ["rhizomes", "rhizome"],
        "stem": ["stems", "stem", "shoots", "shoot"],
        "bulb": ["bulbs", "bulb"],
        "pod": ["pods", "pod"],
        "sap": ["sap"],
    }

    for part, needles in rules.items():
        if any(re.search(rf"\b{re.escape(n)}\b", low) for n in needles):
            parts.append(part)

    return sorted(set(parts))


def extract_use_categories_from_pfaf(
    edible_section: str | None,
    medicinal_section: str | None,
    other_uses_section: str | None,
    common_name: str | None = None,
) -> list[str]:
    medicinal = (medicinal_section or "").lower()
    other = (other_uses_section or "").lower()
    common = (common_name or "").lower()

    categories = []

    edible_uses = extract_pfaf_labeled_values(edible_section, "Edible Uses")

    if "condiment" in edible_uses:
        categories.append("culinary_herb")

    if "tea" in edible_uses or "drink" in edible_uses:
        categories.append("beverage_plant")

    if "oil" in edible_uses or "oil" in extract_edible_parts_from_pfaf(edible_section):
        categories.append("oil_crop")

    if any(w in common for w in ["basil", "sage", "mint", "thyme", "oregano", "parsley"]):
        categories.append("culinary_herb")

    if medicinal:
        categories.append("medicinal_plant")

    if "companion" in other:
        categories.append("companion_plant")

    if "repellent" in other or "insecticide" in other:
        categories.append("repellent_plant")

    # Fruit crop only if explicit edible part is fruit.
    if "fruit" in extract_edible_parts_from_pfaf(edible_section):
        categories.append("fruit_crop")

    # Root/tuber crop only if explicit edible part says root/tuber/rhizome.
    edible_parts = extract_edible_parts_from_pfaf(edible_section)
    if any(part in edible_parts for part in ["root", "tuber", "rhizome"]):
        categories.append("root_tuber_crop")

    return sorted(set(categories))


# =========================================================
# GROWTH / LIFE CYCLE
# =========================================================


def extract_growth_from_pfaf(
    physical_section: str | None,
    cultivation_section: str | None,
) -> dict[str, Any]:
    text = f"{physical_section or ''} {cultivation_section or ''}"
    low = text.lower()

    growth: dict[str, Any] = {
        "sunlight": [],
        "soil_type": [],
        "soil_ph_min": None,
        "soil_ph_max": None,
        "water_need": None,
        "growth_speed": None,
        "soil_notes": None,
        "light_notes": None,
        "water_notes": None,
        "temperature_notes": None,
        "rainfall_notes": None,
    }

    if "cannot grow in the shade" in low or "full sun" in low or "sunny" in low:
        growth["sunlight"].append("full_sun")

    if "semi-shade" in low:
        growth["sunlight"].append("partial_shade")

    if "well-drained" in low or "well drained" in low:
        growth["soil_type"].append("well_drained")

    if "light" in low or "sandy" in low:
        growth["soil_type"].append("light_sandy")

    if "medium" in low or "loamy" in low:
        growth["soil_type"].append("medium_loamy")

    if "heavy" in low or "clay" in low:
        growth["soil_type"].append("heavy_clay")

    if "moist soil" in low:
        growth["water_need"] = "moderate"
        growth["water_notes"] = "Prefers moist soil."

    if "fast-growing" in low or "fast rate" in low:
        growth["growth_speed"] = "fast"

    ph_match = re.search(r"ph in the range\s+([0-9.]+)\s*-\s*([0-9.]+)", low)
    if not ph_match:
        ph_match = re.search(r"ph in the range\s+([0-9.]+)\s+to\s+([0-9.]+)", low)

    if ph_match:
        growth["soil_ph_min"] = float(ph_match.group(1))
        growth["soil_ph_max"] = float(ph_match.group(2))

    if cultivation_section:
        growth["soil_notes"] = clean_text(cultivation_section)

    if "sunny" in low or "cannot grow in the shade" in low:
        growth["light_notes"] = "Prefers a sunny position and does not grow well in shade."

    temp_match = re.search(r"temperatures are within the range\s+([0-9]+)\s*-\s*([0-9]+)", low)
    if temp_match:
        growth["temperature_notes"] = f"Best daytime temperature range mentioned: {temp_match.group(1)}-{temp_match.group(2)}°C."

    rainfall_match = re.search(r"rainfall in the range\s+([0-9,]+)\s*-\s*([0-9,]+)mm", low)
    if rainfall_match:
        growth["rainfall_notes"] = f"Mean annual rainfall range mentioned: {rainfall_match.group(1)}-{rainfall_match.group(2)} mm."

    growth["sunlight"] = sorted(set(growth["sunlight"]))
    growth["soil_type"] = sorted(set(growth["soil_type"]))

    return growth


def extract_life_cycle_from_pfaf(
    physical_section: str | None,
    cultivation_section: str | None,
    summary_section: str | None = None,
) -> dict[str, Any]:
    text = f"{summary_section or ''} {physical_section or ''} {cultivation_section or ''}"
    low = text.lower()

    result = {
        "life_cycle": None,
        "botanical_life_cycle": None,
        "crop_life_cycle": None,
        "life_cycle_context": None,
    }

    if re.search(r"\bis an annual\b|\bis a annual\b|\bannual growing\b", low):
        result["life_cycle"] = "annual"
        result["crop_life_cycle"] = "annual"

    if "perennial in its native habitat" in low and "grown as an annual" in low:
        result["botanical_life_cycle"] = "perennial"
        result["crop_life_cycle"] = "annual"
        result["life_cycle"] = "annual"
        result["life_cycle_context"] = {
            "native_habitat": "perennial",
            "cultivation": "annual",
            "notes": "PFAF says perennial in native habitat but grown as annual in cultivation/temperate climates.",
        }

    if "perennial plant in the tropics" in low and "annual in temperate" in low:
        result["botanical_life_cycle"] = "tender_perennial"
        result["crop_life_cycle"] = "annual"
        result["life_cycle"] = "annual"
        result["life_cycle_context"] = {
            "tropical": "short_lived_perennial",
            "temperate": "half_hardy_annual",
            "notes": "PFAF says perennial in the tropics but frost tender and grown as a half-hardy annual in temperate zones.",
        }

    if result["life_cycle"] is None and "perennial" in low:
        result["life_cycle"] = "perennial"
        result["botanical_life_cycle"] = "perennial"

    return result


# =========================================================
# PROPAGATION / GERMINATION
# =========================================================


def extract_propagation_methods_from_section(section: str | None) -> list[str]:
    if not section:
        return []

    low = section.lower()
    methods = []

    rules = {
        "seed": ["seed", "seeds", "sow", "sown"],
        "cutting": ["cutting", "cuttings"],
        "division": ["division", "divide"],
        "layering": ["layering"],
        "grafting": ["graft", "grafting"],
        "bulb": ["bulb", "bulbs"],
        "rhizome": ["rhizome", "rhizomes"],
        "tuber": ["tuber", "tubers"],
        "runner": ["runner", "runners"],
    }

    for method, needles in rules.items():
        if any(re.search(rf"\b{re.escape(n)}\b", low) for n in needles):
            methods.append(method)

    return sorted(set(methods))


def extract_germination_from_propagation(section: str | None) -> dict[str, Any]:
    result = {
        "propagation_methods": extract_propagation_methods_from_section(section),
        "propagation_notes": clean_text(section),
        "germination_days_min": None,
        "germination_days_max": None,
        "sowing_depth_cm": None,
    }

    if not section:
        return result

    low = section.lower()

    day_match = re.search(r"germinat\w*\D+(\d+)\s*(?:-|to)\s*(\d+)\s*days?", low)
    if day_match:
        result["germination_days_min"] = int(day_match.group(1))
        result["germination_days_max"] = int(day_match.group(2))

    # Example: "15mm deep"
    depth_mm = re.search(r"(\d+(?:\.\d+)?)\s*mm\s+deep", low)
    if depth_mm:
        result["sowing_depth_cm"] = round(float(depth_mm.group(1)) / 10.0, 2)

    return result


# =========================================================
# BIODIVERSITY / COMPANION EXTRACTION
# =========================================================


def split_plant_list(raw: str) -> list[str]:
    raw = raw.replace(" and ", ",")
    raw = raw.replace("&", ",")
    raw = re.sub(r"\[[^\]]+\]", "", raw)

    names = []

    for part in raw.split(","):
        name = normalize_plant_atom(part)

        if name:
            names.append(name)

    return names


def extract_companions_and_conflicts_from_pfaf_text(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    low = text.lower()

    companions: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []

    def add_companion(name: str, relationship: str, confidence: float = 0.75) -> None:
        plant = normalize_plant_atom(name)

        if not plant:
            return

        companions.append(
            {
                "plant": plant,
                "relationship": relationship,
                "source_name": "Plants For A Future",
                "confidence": confidence,
                "notes": f"Extracted from PFAF '{relationship}' wording.",
            }
        )

    def add_conflict(name: str, relationship: str, confidence: float = 0.75) -> None:
        plant = normalize_plant_atom(name)

        if not plant:
            return

        conflicts.append(
            {
                "plant": plant,
                "relationship": relationship,
                "source_name": "Plants For A Future",
                "confidence": confidence,
                "notes": f"Extracted from PFAF '{relationship}' wording.",
            }
        )

    # Example:
    # "Tomatoes grow well with asparagus, parsley, brassicas and stinging nettles"
    for match in re.finditer(r"grow[s]? well with ([a-z ,\-]+?)(?:\.|\[)", low):
        for name in split_plant_list(match.group(1)):
            add_companion(name, "grows_well_with")

    # Example:
    # "A good companion for growing near cabbages and tomatoes"
    for match in re.finditer(r"good companion for growing near ([a-z ,\-]+?)(?:,|\.|\[)", low):
        for name in split_plant_list(match.group(1)):
            add_companion(name, "good_companion")

    # Example:
    # "They are also a good companion for gooseberries"
    # Avoid capturing "growing near" here because it has its own pattern above.
    for match in re.finditer(r"good companion for (?!growing near)([a-z ,\-]+?)(?:,|\.|\[)", low):
        for name in split_plant_list(match.group(1)):
            add_companion(name, "good_companion")

    # Example:
    # "Sweet basil is a good companion plant for tomatoes"
    for match in re.finditer(r"good companion plant for ([a-z ,\-]+?)(?: but|\.|,|\[)", low):
        for name in split_plant_list(match.group(1)):
            add_companion(name, "good_companion")

    # Example:
    # "They dislike growing near fennel, kohl-rabi, potatoes and brassicas"
    for match in re.finditer(r"dislike[s]? growing near ([a-z ,\-]+?)(?:\.|\(|\[)", low):
        for name in split_plant_list(match.group(1)):
            add_conflict(name, "dislikes_growing_near")

    # Example:
    # "it grows badly with rue and sage"
    for match in re.finditer(r"grows badly with ([a-z ,\-]+?)(?:\.|,|\[)", low):
        for name in split_plant_list(match.group(1)):
            add_conflict(name, "grows_badly_with")

    # Example:
    # "When grown near raspberries it can retard their fruiting"
    for match in re.finditer(r"near ([a-z ,\-]+?) it can retard", low):
        for name in split_plant_list(match.group(1)):
            add_conflict(name, "may_retard_fruiting", confidence=0.65)

    return (
        dedupe_dict_list(companions, ["plant", "relationship"]),
        dedupe_dict_list(conflicts, ["plant", "relationship"]),
    )


def extract_biodiversity_from_pfaf(
    other_uses_section: str | None,
    cultivation_section: str | None,
    summary_section: str | None = None,
    physical_section: str | None = None,
) -> dict[str, Any]:
    text = f"{summary_section or ''} {physical_section or ''} {other_uses_section or ''} {cultivation_section or ''}"
    low = text.lower()

    companions, conflicts = extract_companions_and_conflicts_from_pfaf_text(text)

    biodiversity: dict[str, Any] = {
        "companions": companions,
        "conflicts": conflicts,
        "repels_pests": [],
        "attracts_beneficial_insects": [],
        "pest_confuser": False,
        "pollinator_support": False,
        "biodiversity_notes": [],
    }

    if "companion" in low:
        biodiversity["biodiversity_notes"].append("PFAF describes this plant as relevant to companion planting.")

    if "pollinated by insects" in low:
        biodiversity["pollinator_support"] = True
        biodiversity["attracts_beneficial_insects"].append(
            {
                "insect_group": "pollinators",
                "examples": ["insects"],
                "source_name": "Plants For A Future",
                "confidence": 0.60,
                "notes": "PFAF states flowers are pollinated by insects.",
            }
        )

    if "pollinated by bees" in low:
        biodiversity["pollinator_support"] = True
        biodiversity["attracts_beneficial_insects"].append(
            {
                "insect_group": "bees",
                "examples": ["bees"],
                "source_name": "Plants For A Future",
                "confidence": 0.65,
                "notes": "PFAF states flowers are pollinated by bees.",
            }
        )

    if "attract pollinators" in low or "attractive to pollinators" in low:
        biodiversity["pollinator_support"] = True
        biodiversity["attracts_beneficial_insects"].append(
            {
                "insect_group": "pollinators",
                "examples": ["bees", "butterflies"],
                "source_name": "Plants For A Future",
                "confidence": 0.75,
                "notes": "PFAF says this plant attracts pollinators.",
            }
        )

    if "free of insect pests_ver01" in low:
        biodiversity["repels_pests"].append(
            {
                "target": "insect_pests",
                "mechanism": "companion_effect",
                "source_name": "Plants For A Future",
                "confidence": 0.70,
                "notes": "PFAF says companion planting helps keep nearby plants free of insect pests_ver01.",
            }
        )

    if "repel insects from nearby plants" in low or "repels insects from nearby plants" in low:
        biodiversity["repels_pests"].append(
            {
                "target": "insect_pests",
                "mechanism": "aroma",
                "source_name": "Plants For A Future",
                "confidence": 0.70,
                "notes": "PFAF says strong aroma repels insects from nearby plants.",
            }
        )

    if "insecticide" in low:
        biodiversity["repels_pests"].append(
            {
                "target": "insects",
                "mechanism": "insecticidal_extract",
                "source_name": "Plants For A Future",
                "confidence": 0.65,
                "notes": "PFAF mentions insecticidal use.",
            }
        )

    if "effective against ants" in low:
        biodiversity["repels_pests"].append(
            {
                "target": "ants",
                "mechanism": "insecticidal_extract",
                "source_name": "Plants For A Future",
                "confidence": 0.70,
                "notes": "PFAF says it is especially effective against ants.",
            }
        )

    if "mosquito repellent" in low:
        biodiversity["repels_pests"].append(
            {
                "target": "mosquito",
                "mechanism": "essential_oil",
                "source_name": "Plants For A Future",
                "confidence": 0.70,
                "notes": "PFAF mentions mosquito repellent use.",
            }
        )

    if "repels flies" in low:
        biodiversity["repels_pests"].append(
            {
                "target": "flies",
                "mechanism": "aromatic_foliage",
                "source_name": "Plants For A Future",
                "confidence": 0.70,
                "notes": "PFAF mentions repelling flies.",
            }
        )

    if "pest confuser" in low or "mask the scent" in low or "confusing pests_ver01" in low:
        biodiversity["pest_confuser"] = True
        biodiversity["biodiversity_notes"].append("PFAF suggests aromatic leaves may mask plant scent and confuse pests_ver01.")

    biodiversity["repels_pests"] = dedupe_dict_list(
        biodiversity["repels_pests"],
        ["target", "mechanism"],
    )
    biodiversity["attracts_beneficial_insects"] = dedupe_dict_list(
        biodiversity["attracts_beneficial_insects"],
        ["insect_group"],
    )
    biodiversity["biodiversity_notes"] = sorted(set(biodiversity["biodiversity_notes"]))

    return biodiversity


def dedupe_dict_list(items: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    seen = set()
    result = []

    for item in items:
        marker = tuple(item.get(key) for key in keys)

        if marker in seen:
            continue

        seen.add(marker)
        result.append(item)

    return result
