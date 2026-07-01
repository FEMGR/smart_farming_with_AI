"""
source_parse_patch_v3.py

Cleaner source parsing helpers for the plant data bank.

Main purpose:
- Parse PFAF pages section-by-section.
- Avoid whole-page guessing.
- Extract useful facts from:
    Summary
    Physical Characteristics
    Edible Uses
    Medicinal Uses
    Other Uses
    Cultivation details
    Plant Propagation
- Extract biodiversity / companion planting hints from PFAF.
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


def page_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(" ")
    return clean_text(text) or ""


def title_text(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title")
    return clean_text(title.get_text(" ")) if title else None


def strip_noise(text: str) -> str:
    """
    Remove obvious page-level noise.
    """
    if not text:
        return ""

    noise_patterns = [
        r"Translate this page:.*?Summary",
        r"http[s]?://\S+",
        r"Skip to Main Content.*?Search results for:",
        r"The PFAF Bookshop.*?Shop Now",
        r"Readers comment.*",
        r"Cookie preferences.*",
    ]

    cleaned = text

    for pattern in noise_patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE | re.DOTALL)

    return clean_text(cleaned) or ""


# =========================================================
# PAGE RELEVANCE
# =========================================================


def is_search_page(text: str, title: str | None = None) -> bool:
    combined = f"{title or ''} {text[:1500]}".lower()

    return "search results for" in combined or "you searched for" in combined or "database search result" in combined


def source_relevance_score(text: str, plant: dict[str, Any]) -> float:
    """
    Score whether the page likely represents the target plant.
    """
    low = text.lower()
    score = 0.0

    scientific = (plant.get("scientific_name") or "").lower()
    common = (plant.get("common_name") or "").lower()

    if scientific and scientific in low:
        score += 0.60

    if common and common in low:
        score += 0.20

    if "edible uses" in low:
        score += 0.05

    if "plant propagation" in low or "propagation" in low:
        score += 0.05

    if "cultivation details" in low:
        score += 0.05

    if "other uses" in low:
        score += 0.05

    return min(score, 1.0)


# =========================================================
# SECTION PARSING
# =========================================================


def section_after_heading(
    text: str,
    heading: str,
    stop_headings: list[str] | None = None,
    max_chars: int = 5000,
) -> str | None:
    """
    Extract text after a heading until another likely heading.

    Works on flattened page text.
    """
    if not text:
        return None

    stop_headings = stop_headings or [
        "Summary",
        "Physical Characteristics",
        "Synonyms",
        "Plant Habitats",
        "Edible Uses",
        "Medicinal Uses",
        "Other Uses",
        "Special Uses",
        "Cultivation details",
        "Cultivation Details",
        "Plant Propagation",
        "Propagation",
        "Other Names",
        "Native Range",
        "Weed Potential",
        "Conservation Status",
        "Related Plants",
        "Expert comment",
        "Author",
        "Botanical References",
        "Links / References",
        "Readers comment",
    ]

    pattern = re.compile(rf"\b{re.escape(heading)}\b", flags=re.IGNORECASE)
    match = pattern.search(text)

    if not match:
        return None

    start = match.end()
    end = min(len(text), start + max_chars)

    for stop in stop_headings:
        if stop.lower() == heading.lower():
            continue

        stop_pattern = re.compile(rf"\b{re.escape(stop)}\b", flags=re.IGNORECASE)
        stop_match = stop_pattern.search(text[start:end])

        if stop_match:
            end = start + stop_match.start()
            break

    return clean_text(text[start:end])


def get_pfaf_sections(text: str) -> dict[str, str | None]:
    """
    Extract all major PFAF plant page sections.
    """
    return {
        "summary": section_after_heading(
            text,
            "Summary",
            stop_headings=[
                "Physical Characteristics",
                "Synonyms",
                "Plant Habitats",
                "Edible Uses",
            ],
        ),
        "physical_characteristics": section_after_heading(
            text,
            "Physical Characteristics",
            stop_headings=[
                "Synonyms",
                "Plant Habitats",
                "Edible Uses",
                "Medicinal Uses",
            ],
        ),
        "edible_uses": section_after_heading(
            text,
            "Edible Uses",
            stop_headings=[
                "Medicinal Uses",
                "Other Uses",
                "Cultivation details",
                "Cultivation Details",
                "Plant Propagation",
            ],
        ),
        "medicinal_uses": section_after_heading(
            text,
            "Medicinal Uses",
            stop_headings=[
                "Other Uses",
                "Cultivation details",
                "Cultivation Details",
                "Plant Propagation",
            ],
        ),
        "other_uses": section_after_heading(
            text,
            "Other Uses",
            stop_headings=[
                "Special Uses",
                "Cultivation details",
                "Cultivation Details",
                "Plant Propagation",
                "Other Names",
                "Native Range",
            ],
        ),
        "cultivation": section_after_heading(
            text,
            "Cultivation details",
            stop_headings=[
                "Plant Propagation",
                "Propagation",
                "Other Names",
                "Native Range",
                "Weed Potential",
                "Conservation Status",
                "Related Plants",
            ],
        ),
        "propagation": section_after_heading(
            text,
            "Plant Propagation",
            stop_headings=[
                "Other Names",
                "Native Range",
                "Weed Potential",
                "Conservation Status",
                "Related Plants",
            ],
        ),
        "known_hazards": section_after_heading(
            text,
            "Known Hazards",
            stop_headings=[
                "Habitats",
                "Range",
                "Edibility Rating",
                "Other Uses",
                "Medicinal Rating",
                "Care",
            ],
        ),
    }


# =========================================================
# EDIBLE / USE EXTRACTION
# =========================================================


def extract_edible_parts_from_section(section: str | None) -> list[str]:
    """
    Only infer edible parts from the Edible Uses section.

    Do not scan whole page text, because biodiversity sections contain
    phrases like "Wildlife - Food (Fruit, Seeds, Leaf litter...)".
    """
    if not section:
        return []

    low = section.lower()
    parts: list[str] = []

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


def extract_use_categories_from_sections(
    edible_section: str | None,
    medicinal_section: str | None,
    other_uses_section: str | None,
    common_name: str | None = None,
) -> list[str]:
    edible = (edible_section or "").lower()
    medicinal = (medicinal_section or "").lower()
    other = (other_uses_section or "").lower()
    common = (common_name or "").lower()

    categories: list[str] = []

    if any(
        word in edible
        for word in [
            "condiment",
            "flavouring",
            "flavoring",
            "tea",
            "herb",
            "aromatic",
        ]
    ):
        categories.append("culinary_herb")

    if any(word in common for word in ["basil", "sage", "mint", "thyme", "oregano", "parsley"]):
        categories.append("culinary_herb")

    if medicinal:
        categories.append("medicinal_plant")

    if "essential oil" in other or "essential oil" in edible:
        categories.append("essential_oil_plant")

    if "repellent" in other or "insect repellent" in other:
        categories.append("repellent_plant")

    if "edible flower" in edible or "flowers - raw" in edible or "flowers - cooked" in edible:
        categories.append("edible_flower")

    # Only mark fruit crop if fruit is a human edible use, not wildlife text.
    if re.search(r"\bfruits?\b", edible) and "leaves" not in edible:
        categories.append("fruit_crop")

    if any(word in edible for word in ["root", "tuber", "rhizome", "corm"]):
        categories.append("root_tuber_crop")

    return sorted(set(categories))


# =========================================================
# GROWTH / CARE EXTRACTION
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

    if "moist soil" in low or "moisture: m" in low:
        growth["water_need"] = "moderate"
        growth["water_notes"] = "Prefers moist soil."

    if "dry soil" in low:
        growth["soil_type"].append("dry_tolerant")

    ph_match = re.search(r"ph in the range\s+([0-9.]+)\s+to\s+([0-9.]+)", low)
    if ph_match:
        growth["soil_ph_min"] = float(ph_match.group(1))
        growth["soil_ph_max"] = float(ph_match.group(2))

    if "fast-growing" in low or "fast rate" in low:
        growth["growth_speed"] = "fast"

    if cultivation_section:
        growth["soil_notes"] = clean_text(cultivation_section)

    if "sunny" in low or "cannot grow in the shade" in low:
        growth["light_notes"] = "Prefers a sunny position and does not grow well in shade."

    growth["sunlight"] = sorted(set(growth["sunlight"]))
    growth["soil_type"] = sorted(set(growth["soil_type"]))

    return growth


def extract_life_cycle_from_pfaf(
    physical_section: str | None,
    cultivation_section: str | None,
) -> dict[str, Any]:
    """
    PFAF may say a plant is perennial botanically but grown as annual
    in temperate zones. Keep both botanical and crop-management view.
    """
    text = f"{physical_section or ''} {cultivation_section or ''}"
    low = text.lower()

    result = {
        "life_cycle": None,
        "botanical_life_cycle": None,
        "crop_life_cycle": None,
        "life_cycle_context": None,
    }

    if "perennial" in low:
        result["botanical_life_cycle"] = "perennial"

    if "annual" in low:
        # Do not immediately override botanical perennial.
        result["crop_life_cycle"] = "annual"

    if "perennial plant in the tropics" in low and "annual in temperate" in low:
        result["botanical_life_cycle"] = "tender_perennial"
        result["crop_life_cycle"] = "annual"
        result["life_cycle"] = "annual"
        result["life_cycle_context"] = {
            "tropical": "short_lived_perennial",
            "temperate": "half_hardy_annual",
            "notes": ("PFAF describes the plant as perennial in the tropics, " "but frost tender and grown as a half-hardy annual in temperate zones."),
        }
        return result

    if "frost tender" in low and result["botanical_life_cycle"] == "perennial":
        result["botanical_life_cycle"] = "tender_perennial"

    # DSS default: crop_life_cycle is more useful if present.
    result["life_cycle"] = result["crop_life_cycle"] or result["botanical_life_cycle"]

    return result


# =========================================================
# PROPAGATION EXTRACTION
# =========================================================


def extract_propagation_methods_from_section(section: str | None) -> list[str]:
    if not section:
        return []

    low = section.lower()
    methods: list[str] = []

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

    # PFAF often says "germination is usually free and quick" but no exact days.
    day_match = re.search(r"germinat\w*\D+(\d+)\s*(?:-|to)\s*(\d+)\s*days?", low)
    if day_match:
        result["germination_days_min"] = int(day_match.group(1))
        result["germination_days_max"] = int(day_match.group(2))

    return result


# =========================================================
# BIODIVERSITY / COMPANION EXTRACTION
# =========================================================


def normalize_plant_atom(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def extract_companion_plants_from_text(text: str) -> list[dict[str, Any]]:
    low = text.lower()
    companions: list[dict[str, Any]] = []

    # Example from PFAF basil:
    # "Sweet basil is a good companion plant for tomatoes..."
    match = re.search(r"good companion plant for ([a-z ,and]+?)(?: but|\.|,|\[)", low)
    if match:
        names_text = match.group(1)
        names_text = names_text.replace("and", ",")
        for raw_name in names_text.split(","):
            name = normalize_plant_atom(raw_name)
            if name:
                companions.append(
                    {
                        "plant": name,
                        "relationship": "good_companion",
                        "source_name": "Plants For A Future",
                        "confidence": 0.75,
                        "notes": "Extracted from PFAF companion plant wording.",
                    }
                )

    return companions


def extract_conflicts_from_text(text: str) -> list[dict[str, Any]]:
    low = text.lower()
    conflicts: list[dict[str, Any]] = []

    # Example:
    # "it grows badly with rue and sage"
    match = re.search(r"grows badly with ([a-z ,and]+?)(?:\.|,|\[)", low)
    if match:
        names_text = match.group(1)
        names_text = names_text.replace("and", ",")
        for raw_name in names_text.split(","):
            name = normalize_plant_atom(raw_name)
            if name:
                conflicts.append(
                    {
                        "plant": name,
                        "relationship": "grows_badly_with",
                        "source_name": "Plants For A Future",
                        "confidence": 0.75,
                        "notes": "Extracted from PFAF 'grows badly with' wording.",
                    }
                )

    # Example:
    # "When grown near raspberries it can retard their fruiting"
    near_match = re.search(r"near ([a-z ,and]+?) it can retard", low)
    if near_match:
        names_text = near_match.group(1)
        names_text = names_text.replace("and", ",")
        for raw_name in names_text.split(","):
            name = normalize_plant_atom(raw_name)
            if name:
                conflicts.append(
                    {
                        "plant": name,
                        "relationship": "may_retard_fruiting",
                        "source_name": "Plants For A Future",
                        "confidence": 0.65,
                        "notes": "Extracted from PFAF wording about retarding fruiting.",
                    }
                )

    return conflicts


def extract_biodiversity_from_pfaf(
    other_uses_section: str | None,
    cultivation_section: str | None,
    summary_section: str | None = None,
) -> dict[str, Any]:
    text = f"{summary_section or ''} {other_uses_section or ''} {cultivation_section or ''}"
    low = text.lower()

    biodiversity: dict[str, Any] = {
        "companions": [],
        "conflicts": [],
        "repels_pests": [],
        "attracts_beneficial_insects": [],
        "pest_confuser": False,
        "pollinator_support": False,
        "biodiversity_notes": [],
    }

    biodiversity["companions"].extend(extract_companion_plants_from_text(low))
    biodiversity["conflicts"].extend(extract_conflicts_from_text(low))

    if "companion plant" in low:
        biodiversity["biodiversity_notes"].append("PFAF describes this plant as useful in companion planting.")

    if "attract pollinators" in low or "attractive to pollinators" in low:
        biodiversity["pollinator_support"] = True
        biodiversity["attracts_beneficial_insects"].append(
            {
                "insect_group": "pollinators",
                "examples": ["bees", "butterflies"],
                "source_name": "Plants For A Future",
                "confidence": 0.75,
                "notes": "PFAF states the plant attracts pollinators.",
            }
        )

    if "bees" in low and "pollinated by bees" in low:
        biodiversity["pollinator_support"] = True
        biodiversity["attracts_beneficial_insects"].append(
            {
                "insect_group": "bees",
                "examples": ["bees"],
                "source_name": "Plants For A Future",
                "confidence": 0.65,
                "notes": "PFAF states the species is pollinated by bees.",
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

    if "insect repellent" in low or "deter pests_ver01" in low:
        biodiversity["repels_pests"].append(
            {
                "target": "insect_pests",
                "mechanism": "aromatic_foliage",
                "source_name": "Plants For A Future",
                "confidence": 0.70,
                "notes": "PFAF mentions insect repellent or pest deterrent use.",
            }
        )

    if "keep all manner of insect pests_ver01 away" in low:
        biodiversity["repels_pests"].append(
            {
                "target": "insect_pests",
                "mechanism": "aromatic_foliage",
                "source_name": "Plants For A Future",
                "confidence": 0.75,
                "notes": "PFAF says the plant can keep insect pests_ver01 away from nearby plants.",
            }
        )

    if "pest confuser" in low or "mask the scent" in low or "confusing pests_ver01" in low:
        biodiversity["pest_confuser"] = True
        biodiversity["biodiversity_notes"].append("PFAF suggests aromatic leaves may mask plant scent and confuse pests_ver01.")

    # Deduplicate list of dicts.
    biodiversity["companions"] = dedupe_dict_list(
        biodiversity["companions"],
        keys=["plant", "relationship"],
    )
    biodiversity["conflicts"] = dedupe_dict_list(
        biodiversity["conflicts"],
        keys=["plant", "relationship"],
    )
    biodiversity["repels_pests"] = dedupe_dict_list(
        biodiversity["repels_pests"],
        keys=["target", "mechanism"],
    )
    biodiversity["attracts_beneficial_insects"] = dedupe_dict_list(
        biodiversity["attracts_beneficial_insects"],
        keys=["insect_group"],
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
