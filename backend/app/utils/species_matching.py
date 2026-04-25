

#app/utils/species_matching.py
from rapidfuzz import fuzz

#Data cleaning & reformating
def normalize_input(value):
    if not value:
        return ""
    return str(value).lower().strip()

def normalize_candidate(c: dict, source: str):
    sci = c.get("scientific_name")

    if isinstance(sci, list):
        sci = sci[0] if sci else None
    return {
        "id": c.get("id"),
        "common_name": c.get("common_name"),
        "scientific_name": c.get("scientific_name"),
        "source": source
    }

def compute_match_score(query: str, candidate: dict) -> int:
    query = normalize_input(query)
    commonName = normalize_input(candidate.get("common_name"))
    scientificName = normalize_input(candidate.get("scientific_name"))
    #finding the best match :
    commonNameScore = fuzz.partial_ratio(query, commonName)
    scientificNameScore = fuzz.partial_ratio(query, scientificName)

    return max(commonNameScore, scientificNameScore)


# rank everything (used for suggestions)
def rank_species_matches(query: str, candidates: list):
    scored = []

    for c in candidates:
        score = compute_match_score(query, c)

        scored.append({
            "score": score,
            "id": c.get("id"),
            "common_name": c.get("common_name"),
            "scientific_name": c.get("scientific_name"),
            "source": c.get("source", "unknown")  # 👈 fix here
        })

    # sort descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    #DEBUG
    print(f"\n[DEBUG] Ranking for query: '{query}'")
    for s in scored[:5]:
        print(f"  → {s['common_name']} ({s['scientific_name']}) | score={s['score']} | {s['source']}")

    return scored


# pick best (used for auto-selection)
def select_best_match(query: str, candidates: list, threshold: int = 70):
    ranked = rank_species_matches(query, candidates)

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
