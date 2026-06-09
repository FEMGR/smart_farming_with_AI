import pytest

from app.models.plant_species_cache import PlantSpeciesCache
from app.schemas.plant_schema import PlantCreate
from app.services import perenual_service, plant_service


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self.rows


class FakeDB:
    def __init__(self, rows=None):
        self.rows = rows or []

    def query(self, *args, **kwargs):
        return FakeQuery(self.rows)


class FakeWriteDB(FakeDB):
    def __init__(self):
        super().__init__([])
        self.added = []

    def add(self, item):
        self.added.append(item)

    def flush(self):
        for index, item in enumerate(self.added, start=1):
            if getattr(item, "id", None) is None:
                item.id = index

    def commit(self):
        pass

    def refresh(self, item):
        pass


def make_species(**overrides):
    values = {
        "external_species_id": "1824",
        "common_name": "chamomile",
        "scientific_name": "Chamaemelum nobile",
        "is_edible": False,
        "is_fruit": False,
        "is_veg": False,
        "growth_rate": None,
        "data": {"genus": "Chamaemelum", "family": "Asteraceae"},
    }
    values.update(overrides)
    return PlantSpeciesCache(**values)


def test_suggest_species_uses_db_before_json_cache_or_api(monkeypatch):
    def fail_json_cache(query):
        raise AssertionError("JSON cache should not be checked when DB has candidates")

    def fail_api(query):
        raise AssertionError("Perenual API should not be called when DB has candidates")

    monkeypatch.setattr(perenual_service, "get_cached_species_suggestions", fail_json_cache)
    monkeypatch.setattr(perenual_service, "search_plant_species_api", fail_api)

    ranked = perenual_service.suggest_species(FakeDB([make_species()]), "chamomile", plant_type="flower")

    assert ranked[0]["source"] == "db_cache"
    assert ranked[0]["common_name"] == "chamomile"


def test_suggest_species_uses_json_cache_before_api(monkeypatch):
    def fail_api(query):
        raise AssertionError("Perenual API should not be called when JSON cache has candidates")

    monkeypatch.setattr(
        perenual_service,
        "get_cached_species_suggestions",
        lambda query: [
            {
                "id": 5167,
                "common_name": "German chamomile",
                "scientific_name": "Matricaria recutita",
                "genus": "Matricaria",
                "family": "Asteraceae",
            }
        ],
    )
    monkeypatch.setattr(perenual_service, "search_plant_species_api", fail_api)

    ranked = perenual_service.suggest_species(FakeDB(), "matricaria", plant_type="flower")

    assert ranked[0]["source"] == "json_cache"
    assert ranked[0]["exact_genus_match"]


def test_suggest_species_uses_corrected_json_cache_before_api(monkeypatch):
    def fail_api(query):
        raise AssertionError("Perenual API should not be called when corrected JSON cache has candidates")

    def fake_cached_suggestions(query):
        if query == "chamomile":
            return [
                {
                    "id": 1824,
                    "common_name": "chamomile",
                    "scientific_name": "Chamaemelum nobile",
                    "genus": "Chamaemelum",
                    "family": "Asteraceae",
                }
            ]
        return None

    monkeypatch.setattr(perenual_service, "_correct_species_query", lambda query: ("chamomile", 88))
    monkeypatch.setattr(perenual_service, "get_cached_species_suggestions", fake_cached_suggestions)
    monkeypatch.setattr(perenual_service, "search_plant_species_api", fail_api)

    ranked = perenual_service.suggest_species(FakeDB(), "chemomile", plant_type="flower")

    assert ranked[0]["common_name"] == "chamomile"
    assert ranked[0]["corrected_query"] == "chamomile"
    assert ranked[0]["correction_score"] == 88
    assert ranked[0]["score"] >= 75


def test_correct_species_query_does_not_change_exact_known_name(monkeypatch):
    monkeypatch.setattr(perenual_service, "_candidate_search_terms_from_taxonomy", lambda: {"tomato"})
    monkeypatch.setattr(perenual_service, "_candidate_search_terms_from_suggestion_cache", lambda: {"tree tomato"})

    assert perenual_service.correct_species_query("tomato") is None
    assert perenual_service.correct_species_query("tomat") == "tomato"


def test_suggest_species_filters_cached_tree_tomato_when_tomato_identity_is_known(monkeypatch):
    monkeypatch.setattr(perenual_service, "get_cached_species_suggestions", lambda query: None)
    monkeypatch.setattr(perenual_service, "search_plant_species_api", lambda query: [])

    ranked = perenual_service.suggest_species(
        FakeDB(
            [
                make_species(
                    external_species_id="2292",
                    common_name="tree tomato",
                    scientific_name="Cyphomandra betacea",
                    data={"genus": "Cyphomandra", "family": "Solanaceae"},
                )
            ]
        ),
        "tomato",
        plant_type="vegetable",
        allow_external_api=False,
        preferred_scientific_names=["Solanum lycopersicum", "Lycopersicon esculentum"],
        preferred_common_names=["tomato"],
        preferred_genus="solanum",
        preferred_family="solanaceae",
    )

    assert ranked == []


def test_create_plant_with_species_uses_selected_species_identity(monkeypatch):
    species = make_species(
        id=77,
        external_species_id="5021",
        common_name="tomato",
        scientific_name="Lycopersicon esculentum",
        data={"genus": "Lycopersicon", "family": "Solanaceae"},
    )
    db = FakeWriteDB()

    monkeypatch.setattr(plant_service, "_validate_location", lambda *args, **kwargs: None)
    monkeypatch.setattr(plant_service, "_ensure_user_group", lambda *args, **kwargs: None)
    monkeypatch.setattr(plant_service, "_sync_plant_id_sequence", lambda *args, **kwargs: None)
    monkeypatch.setattr(plant_service, "save_plant_timeline_snapshot", lambda *args, **kwargs: None)
    monkeypatch.setattr(plant_service, "_attach_metadata", lambda plant: plant)
    monkeypatch.setattr(plant_service, "get_or_create_species_cache", lambda *args, **kwargs: species)

    plant = plant_service.create_plant_with_species(
        db,
        PlantCreate(name="some wrong user text", plant_type="vegetable"),
        user_id=1,
        external_species_id=5021,
    )

    assert plant.name == "tomato"
    assert plant.species_id == species.id
    assert plant.scientific_name == "Lycopersicon esculentum"
    assert plant.genus == "Lycopersicon"
    assert plant.family == "Solanaceae"
    assert plant.taxonomy_confidence == "perenual_selected"


@pytest.mark.parametrize(
    ("score", "selected"),
    [
        (74, False),
        (75, True),
    ],
)
def test_select_species_match_requires_75(score, selected):
    match = perenual_service._select_species_match(
        "mint",
        [{"score": score, "common_name": "mint", "scientific_name": "Mentha"}],
    )

    assert bool(match) is selected
