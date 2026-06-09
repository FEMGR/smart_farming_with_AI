from app.models.plant_species_cache import PlantSpeciesCache
from app.services.perenual_service import (
    _candidate_matches_preferred_identity,
    _resolved_species_matches_preferred_scientific_identity,
)
from app.services.plant_taxonomy_service import load_plant_taxonomy_cache, normalize_plant_input


def test_chamomile_identity_filter_allows_exact_common_and_known_synonym():
    load_plant_taxonomy_cache(force=True)
    identity = normalize_plant_input("chamomile")
    preferred_scientific_names = [
        identity.scientific_name,
        *(identity.alternate_scientific_names or []),
    ]

    assert _candidate_matches_preferred_identity(
        {"common_name": "chamomile", "scientific_name": "Chamaemelum nobile"},
        preferred_scientific_names,
        ["chamomile"],
    )
    assert _candidate_matches_preferred_identity(
        {"common_name": "German chamomile", "scientific_name": "Matricaria recutita"},
        preferred_scientific_names,
        ["chamomile"],
    )
    assert not _candidate_matches_preferred_identity(
        {"common_name": "golden chamomile", "scientific_name": "Anthemis tinctoria"},
        preferred_scientific_names,
        ["chamomile"],
    )


def test_tomato_identity_filter_rejects_tree_tomato():
    load_plant_taxonomy_cache(force=True)
    identity = normalize_plant_input("tomato")
    preferred_scientific_names = [
        identity.scientific_name,
        *(identity.alternate_scientific_names or []),
    ]

    assert not _candidate_matches_preferred_identity(
        {"common_name": "tree tomato", "scientific_name": "Cyphomandra betacea"},
        preferred_scientific_names,
        ["tomato"],
    )


def test_resolved_species_scientific_identity_rejects_tree_tomato():
    species = PlantSpeciesCache(
        external_species_id="2292",
        common_name="tree tomato",
        scientific_name="Cyphomandra betacea",
    )

    assert not _resolved_species_matches_preferred_scientific_identity(
        species,
        ["Solanum lycopersicum", "Lycopersicon esculentum"],
    )
