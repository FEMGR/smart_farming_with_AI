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


#app/utils/species_matching.py
from rapidfuzz import fuzz


# Data cleaning & reformating
def normalize_input(value):
    if not value:
        return ""
    return str(value).lower().strip()


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
        "edible": c.get("edible"),  # 👈 Added
        "growth_rate": c.get("growth_rate"),  # 👈 Added
        "source": source
    }


def compute_match_score(query: str, candidate: dict, plant_type: str = None) -> int:
    query = normalize_input(query)
    commonName = normalize_input(candidate.get("common_name"))
    scientificName = normalize_input(candidate.get("scientific_name"))

    # 1. Base Fuzzy Matching
    commonNameScore = fuzz.partial_ratio(query, commonName)
    scientificNameScore = fuzz.partial_ratio(query, scientificName)
    base_score = max(commonNameScore, scientificNameScore)

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

    # 3. Final Score (0-100)
    final_score = base_score + bonus
    return max(0, min(100, int(final_score)))



# rank everything (used for suggestions)
def rank_species_matches(query: str, candidates: list, plant_type: str = None):
    scored = []

    for c in candidates:
        score = compute_match_score(query, c, plant_type=plant_type)

        scored.append({
            "score": score,
            "id": c.get("id"),
            "common_name": c.get("common_name"),
            "scientific_name": c.get("scientific_name"),
            "source": c.get("source", "unknown")
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    #DEBUG
    print(f"\n[DEBUG] Ranking for query: '{query}'")
    for s in scored[:5]:
        print(f"  → {s['common_name']} ({s['scientific_name']}) | score={s['score']} | {s['source']}")

    return scored


# pick best (used for auto-selection)
def select_best_match(query: str, candidates: list, threshold: int = 70, plant_type: str = None):
    ranked = rank_species_matches(query, candidates, plant_type=plant_type)

    if not ranked:
        return None

    best = ranked[0]
    score = best.get("score", 0)

    print(f"[DEBUG] Best match: {best['common_name']} (score={score})")

    if score >= threshold:
        return best

    if score >= 50 and len(query) > 5:
        print("[DEBUG] Using fallback match")
        return best

    print("[DEBUG] No confident match")
    return None
