"""
Utility layer for species matching and ranking.

Key Point:
Handles fuzzy matching and intelligent selection of plant species
from multiple data sources (cache + external API).

Responsibilities:
- Normalize and clean user input and candidate data
- Compute similarity scores between query and species candidates
- Apply domain-specific logic (e.g., plant type constraints)
- Rank species matches based on relevance
- Select the best match using scoring thresholds

Architecture Role:
- Helper/utility layer for species identification logic
- Enhances accuracy of plant-species mapping

Layer Interaction:
- Communicates with: External API data (Perenual), Cached species data
- Called by: Services (e.g., plant_service, perenual_service)

Data Flow:
User query received (e.g., plant name)
        ↓
Input and candidate data normalized
        ↓
Fuzzy matching scores computed
        ↓
Domain rules applied (e.g., fruit vs flower)
        ↓
Candidates ranked by score
        ↓
Best match selected or fallback returned
"""

# app/utils/species_matching.py
import re

from rapidfuzz import fuzz
from app.core.logger import setup_logger

logger = setup_logger()


# Data cleaning & reformating
def normalize_input(value):
    if not value:
        return ""
    return str(value).lower().strip()


def _tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^a-z0-9]+", normalize_input(value)) if token]


def _exact_match(query: str, value: str) -> bool:
    return normalize_input(query) == normalize_input(value)


def _single_token_query(query: str) -> bool:
    return len(_tokens(query)) == 1


def _has_cultivar_marker(value: str) -> bool:
    value = str(value or "")
    return "'" in value or '"' in value or re.search(r"\bcv\.", value, re.IGNORECASE) is not None


def _matches_any_name(value: str, names: list[str] | None) -> bool:
    normalized_value = normalize_input(value)
    return any(normalized_value == normalize_input(name) for name in names or [])


def _canonical_scientific_key(value: str | None) -> str:
    value = normalize_input(value)
    if not value:
        return ""

    value = value.replace("×", " x ")
    value = value.replace("'", " ")
    value = value.replace('"', " ")
    value = re.sub(r"\(([^)]*?)\s+group\)", r"\1", value)
    value = re.sub(r"\(([^)]*)\)", r"\1", value)
    value = re.sub(r"\b(var\.?|subsp\.?|ssp\.?|spp\.?|forma|f\.|cv\.)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _scientific_binomial(value: str | None) -> str:
    parts = _canonical_scientific_key(value).split()
    return " ".join(parts[:2]) if len(parts) >= 2 else ""


def _scientific_names_compatible(left: str | None, right: str | None) -> bool:
    left_key = _canonical_scientific_key(left)
    right_key = _canonical_scientific_key(right)
    if not left_key or not right_key:
        return False

    left_binomial = _scientific_binomial(left)
    right_binomial = _scientific_binomial(right)
    left_genus = left_key.split()[0] if left_key.split() else ""
    right_genus = right_key.split()[0] if right_key.split() else ""
    genus_level_match = bool(left_genus and right_genus and left_genus == right_genus) and (len(left_key.split()) == 1 or len(right_key.split()) == 1)
    return bool(
        left_key == right_key
        or left_key.startswith(right_key)
        or right_key.startswith(left_key)
        or (left_binomial and left_binomial == right_binomial)
        or genus_level_match
    )


def _matches_any_scientific_name(value: str, names: list[str] | None) -> bool:
    return any(_scientific_names_compatible(value, name) for name in names or [])


def _infer_genus(scientific_name: str | None) -> str | None:
    tokens = _tokens(scientific_name or "")
    return tokens[0] if tokens else None


def normalize_candidate(c: dict, source: str):
    """
    Standardizes candidates from both Cache (Objects) and API (Dicts).
    """
    # Handle scientific_name if it comes as a list from API
    sci = c.get("scientific_name")
    if isinstance(sci, list):
        sci = sci[0] if sci else "Unknown"
    elif not sci:
        sci = "Unknown"

    return {
        "id": c.get("id"),
        "common_name": c.get("common_name", "Unknown"),
        "scientific_name": sci,
        "genus": c.get("genus") or _infer_genus(sci),
        "family": c.get("family"),
        "edible": c.get("edible"),  # 👈 Added
        "is_fruit": c.get("is_fruit"),
        "is_veg": c.get("is_veg"),
        "type": c.get("type"),
        "growth_rate": c.get("growth_rate"),  # 👈 Added
        "source": source,
    }


def compute_match_score(
    query: str,
    candidate: dict,
    plant_type: str = None,
    preferred_scientific_names: list[str] | None = None,
    preferred_common_names: list[str] | None = None,
    preferred_genus: str | None = None,
    preferred_family: str | None = None,
) -> int:
    query = normalize_input(query)
    commonName = normalize_input(candidate.get("common_name"))
    raw_scientific_name = candidate.get("scientific_name")
    scientificName = normalize_input(raw_scientific_name)
    genusName = normalize_input(candidate.get("genus"))
    familyName = normalize_input(candidate.get("family"))
    preferred_scientific_match = _matches_any_scientific_name(scientificName, preferred_scientific_names)
    preferred_common_match = _matches_any_name(commonName, preferred_common_names)
    preferred_genus_match = bool(preferred_genus and normalize_input(candidate.get("genus")) == normalize_input(preferred_genus))
    preferred_family_match = bool(preferred_family and normalize_input(candidate.get("family")) == normalize_input(preferred_family))

    # 1. Base matching. Exact names must beat substring matches like
    # "tree tomato" for query "tomato".
    if preferred_scientific_match:
        base_score = 100
    elif _scientific_names_compatible(query, scientificName):
        base_score = 100
    elif _exact_match(query, commonName):
        base_score = 100
    elif _exact_match(query, scientificName):
        base_score = 100
    elif _exact_match(query, genusName):
        base_score = 88
    elif _exact_match(query, familyName):
        base_score = 80
    elif _single_token_query(query):
        common_tokens = set(_tokens(commonName))
        scientific_tokens = set(_tokens(scientificName))
        genus_tokens = set(_tokens(genusName))
        family_tokens = set(_tokens(familyName))
        if query in common_tokens:
            base_score = 82
        elif query in scientific_tokens:
            base_score = 70
        elif query in genus_tokens:
            base_score = 70
        elif query in family_tokens:
            base_score = 65
        else:
            base_score = max(
                fuzz.ratio(query, commonName),
                fuzz.ratio(query, scientificName),
                fuzz.ratio(query, genusName),
                fuzz.ratio(query, familyName),
            )
    else:
        commonNameScore = max(fuzz.ratio(query, commonName), fuzz.token_sort_ratio(query, commonName))
        scientificNameScore = max(fuzz.ratio(query, scientificName), fuzz.token_sort_ratio(query, scientificName))
        genusNameScore = max(fuzz.ratio(query, genusName), fuzz.token_sort_ratio(query, genusName))
        familyNameScore = max(fuzz.ratio(query, familyName), fuzz.token_sort_ratio(query, familyName))
        base_score = max(commonNameScore, scientificNameScore, genusNameScore, familyNameScore)

    # 2. Logic Constraint
    bonus = 0
    if plant_type:
        p_type = plant_type.lower()
        # Perenual data often has 'type': 'tree' or 'Broadleaf evergreen'
        api_plant_type = str(candidate.get("type", "")).lower()

        #  Scenario A: User wants a crop
        if p_type == "fruit" and candidate.get("is_fruit"):
            bonus += 25
        elif p_type == "vegetable" and candidate.get("is_veg"):
            bonus += 25

        #  Scenario B: User wants a flower
        elif p_type == "flower":
            #  The "Maple Tree" Fix: Penalize if the user wants a flower but the API says it's a tree
            if "tree" in api_plant_type:
                bonus -= 40
            elif candidate.get("is_fruit") or candidate.get("is_veg"):
                bonus -= 15
            else:
                bonus += 15

    # Penalize if "false" is in the common name
    if "false" in commonName:
        bonus -= 80  # Significantly reduce score for "false" matches

    if preferred_common_match:
        bonus += 5
    if preferred_genus_match:
        bonus += 5
    if preferred_family_match:
        bonus += 5

    # If multiple cultivars share the same exact common name, prefer the base
    # species over named cultivars like Solanum melongena 'Aswad'.
    if _exact_match(query, commonName) and not preferred_scientific_match and _has_cultivar_marker(raw_scientific_name):
        bonus -= 20

    # 3. Final Score (0-100)
    final_score = base_score + bonus
    return max(0, min(100, int(final_score)))


# rank everything (used for suggestions)
def rank_species_matches(
    query: str,
    candidates: list,
    plant_type: str = None,
    preferred_scientific_names: list[str] | None = None,
    preferred_common_names: list[str] | None = None,
    preferred_genus: str | None = None,
    preferred_family: str | None = None,
):
    scored = []

    for c in candidates:
        score = compute_match_score(
            query,
            c,
            plant_type=plant_type,
            preferred_scientific_names=preferred_scientific_names,
            preferred_common_names=preferred_common_names,
            preferred_genus=preferred_genus,
            preferred_family=preferred_family,
        )
        common_name = c.get("common_name")
        scientific_name = c.get("scientific_name")
        genus_name = c.get("genus")
        family_name = c.get("family")
        preferred_scientific_match = _matches_any_scientific_name(scientific_name, preferred_scientific_names)
        preferred_common_match = _matches_any_name(common_name, preferred_common_names)
        preferred_genus_match = bool(preferred_genus and normalize_input(c.get("genus")) == normalize_input(preferred_genus))
        preferred_family_match = bool(preferred_family and normalize_input(c.get("family")) == normalize_input(preferred_family))

        scored.append(
            {
                "score": score,
                "id": c.get("id"),
                "common_name": common_name,
                "scientific_name": scientific_name,
                "genus": c.get("genus"),
                "family": c.get("family"),
                "source": c.get("source", "unknown"),
                "type": c.get("type"),
                "is_fruit": c.get("is_fruit"),
                "is_veg": c.get("is_veg"),
                "exact_common_match": _exact_match(query, common_name),
                "exact_scientific_match": _exact_match(query, scientific_name),
                "exact_genus_match": _exact_match(query, genus_name),
                "exact_family_match": _exact_match(query, family_name),
                "preferred_scientific_match": preferred_scientific_match,
                "preferred_common_match": preferred_common_match,
                "preferred_genus_match": preferred_genus_match,
                "preferred_family_match": preferred_family_match,
            }
        )

    exact_scientific_matches = [item for item in scored if item["exact_scientific_match"]]
    if exact_scientific_matches:
        scored = exact_scientific_matches

    scored.sort(
        key=lambda x: (
            x["exact_scientific_match"],
            x["preferred_scientific_match"],
            x["preferred_common_match"],
            x["preferred_genus_match"],
            x["preferred_family_match"],
            x["exact_common_match"],
            x["exact_genus_match"],
            x["exact_family_match"],
            x["score"],
        ),
        reverse=True,
    )

    # DEBUG
    logger.info(f"\n[DEBUG] Ranking for query: '{query}'")
    for s in scored[:5]:
        logger.info(f"  → {s['common_name']} ({s['scientific_name']}) | score={s['score']} | {s['source']}")

    return scored


# pick best (used for auto-selection)
def select_best_match(query: str, candidates: list, threshold: int = 70, plant_type: str = None):
    # The 'candidates' list is already expected to be ranked from suggest_species
    ranked = candidates

    if not ranked:
        return None

    best = ranked[0]
    score = best.get("score", 0)

    logger.info(f"[DEBUG] Best match: {best['common_name']} (score={score})")

    if score >= threshold:
        return best

    if score >= 50 and len(query) > 5:
        logger.info("[DEBUG] Using fallback match")
        return best

    logger.info("[DEBUG] No confident match")
    return None
