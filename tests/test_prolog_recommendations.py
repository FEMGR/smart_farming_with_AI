from app.services.plant_service import get_companion_recommendations
from app.models.plant import Plant
from sqlalchemy.orm import Session

# --- Mocking Database and Plant Objects ---


class MockSpecies:
    def __init__(self, scientific_name, common_name=None):
        self.scientific_name = scientific_name
        self.common_name = common_name


class MockPlant:
    def __init__(self, name, plant_type, species_scientific_name):
        self.name = name
        self.plant_type = plant_type
        self.species = MockSpecies(species_scientific_name)

# Mock a query object that returns our list of plants


class MockQuery:
    def __init__(self, plants):
        self._plants = plants

    def options(self, *args):
        return self  # Allow chaining .options()

    def filter(self, *args):
        return self  # Allow chaining .filter()

    def all(self):
        return self._plants


# Mock a database session that returns our mock plants when queried for Plant


class MockSession:
    def query(self, model):
        if model == Plant:
            mock_plants_data = [
                {
                    'name': 'tomato',
                    'type': 'vegetable',
                    'species_name': 'solanum lycopersicum'
                },
                {
                    'name': 'ginger',
                    'type': 'spice',
                    'species_name': 'zingiber officinale'
                },
                {
                    'name': 'cucumber',
                    'type': 'vegetable',
                    'species_name': 'cucumis sativus'
                },
                {
                    'name': 'dandelion',
                    'type': 'flower',
                    'species_name': 'taraxacum officinale'
                },
                {
                    'name': 'rye',
                    'type': 'grain',
                    'species_name': 'secale cereale'
                },
                {
                    'name': 'grape',
                    'type': 'fruit',
                    'species_name': 'vitis vinifera'
                },
                {
                    'name': 'hydrangea',
                    'type': 'flower',
                    'species_name': 'hydrangea spp.'
                },
                {
                    'name': 'artichoke',
                    'type': 'vegetable',
                    'species_name': 'cynara scolymus'
                },
                {
                    'name': 'dahlia',
                    'type': 'flower',
                    'species_name': 'dahlia spp.'
                },
                {
                    'name': 'nasturtium',
                    'type': 'flower',
                    'species_name': 'tropaeolum majus'
                },
                {
                    'name': 'cabbage',
                    'type': 'vegetable',
                    'species_name': 'brassica oleracea var. capitata'
                },
                {
                    'name': 'broccoli',
                    'type': 'vegetable',
                    'species_name': 'brassica oleracea var. italica'
                },
            ]
            mock_plant_objects = [
                MockPlant(p['name'], p['type'], p['species_name'])
                for p in mock_plants_data
            ]
            return MockQuery(mock_plant_objects)
        return MockQuery([])   # Return empty for other models


# Instantiate our mock database session and a dummy user ID
mock_db_session = MockSession()

test_user_id = 1

# --- Call the combined recommendation function ---
combined_recommendations = get_companion_recommendations(
    mock_db_session, test_user_id
)

print(combined_recommendations)
