from app.utils.species_matching import (
    _canonical_scientific_key,
    _scientific_names_compatible,
    normalize_candidate,
    select_best_match,
)


def test_scientific_key_removes_rank_markers_with_periods():
    assert _canonical_scientific_key("Brassica oleracea var. gemmifera") == "brassica oleracea gemmifera"
    assert _canonical_scientific_key("Solanum melongena cv. Aswad") == "solanum melongena aswad"


def test_scientific_compatibility_does_not_use_partial_word_prefixes():
    assert _scientific_names_compatible("Solanum lycopersicum", "Solanum lycopersicum var. cerasiforme")
    assert not _scientific_names_compatible("Solanum", "Solanumx example")


def test_normalize_candidate_preserves_is_edible_alias():
    candidate = normalize_candidate(
        {
            "id": 1,
            "common_name": "tomato",
            "scientific_name": ["Solanum lycopersicum"],
            "is_edible": True,
        },
        "api",
    )

    assert candidate["scientific_name"] == "Solanum lycopersicum"
    assert candidate["edible"] is True
    assert candidate["is_edible"] is True


def test_select_best_match_ranks_raw_candidates_with_plant_type():
    selected = select_best_match(
        "tomato",
        [
            {
                "id": 1,
                "common_name": "tree tomato",
                "scientific_name": "Cyphomandra betacea",
                "type": "tree",
            },
            {
                "id": 2,
                "common_name": "tomato",
                "scientific_name": "Solanum lycopersicum",
                "is_veg": True,
            },
        ],
        plant_type="vegetable",
    )

    assert selected["id"] == 2
