from app.models.plant import Plant
from app.services.plant_service import get_companion_recommendations

# --- Mocking Database and Plant Objects ---


class MockSpecies:
    def __init__(self, scientific_name, common_name=None, id=None):
        self.id = id if id is not None else 9999  # Assign a default ID if not provided
        self.scientific_name = scientific_name
        self.common_name = common_name


class MockGroup:
    def __init__(self, name, id=None):
        self.id = id if id is not None else 8888
        self.name = name


class MockPlant:
    def __init__(self, id, name, plant_type, species_scientific_name, group_id=None, group_name=None):
        self.id = id
        self.name = name
        self.plant_type = plant_type
        self.species = MockSpecies(species_scientific_name, id=id * 100)  # Pass ID to species mock
        self.group_id = group_id
        self.group = MockGroup(group_name, id=group_id) if group_name else None
        print(f"DEBUG: MockPlant created: id={self.id}, name={self.name}")


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
                {"id": 1, "name": "tomato", "type": "vegetable", "species_name": "solanum lycopersicum"},
                {"id": 2, "name": "ginger", "type": "spice", "species_name": "zingiber officinale"},
                {"id": 3, "name": "cucumber", "type": "vegetable", "species_name": "cucumis sativus"},
                {"id": 4, "name": "dandelion", "type": "flower", "species_name": "taraxacum officinale"},
                {"id": 5, "name": "rye", "type": "grain", "species_name": "secale cereale"},
                {"id": 6, "name": "grape", "type": "fruit", "species_name": "vitis vinifera"},
                {"id": 7, "name": "hydrangea", "type": "flower", "species_name": "hydrangea spp."},
                {"id": 8, "name": "artichoke", "type": "vegetable", "species_name": "cynara scolymus"},
                {"id": 9, "name": "dahlia", "type": "flower", "species_name": "dahlia spp."},
                {"id": 10, "name": "nasturtium", "type": "flower", "species_name": "tropaeolum majus"},
                {"id": 11, "name": "cabbage", "type": "vegetable", "species_name": "brassica oleracea var. capitata"},
                {"id": 12, "name": "broccoli", "type": "vegetable", "species_name": "brassica oleracea var. italica"},
            ]
            mock_plant_objects = [MockPlant(p["id"], p["name"], p["type"], p["species_name"]) for p in mock_plants_data]
            return MockQuery(mock_plant_objects)
        return MockQuery([])  # Return empty for other models


# Instantiate our mock database session and a dummy user ID
mock_db_session = MockSession()

test_user_id = 1

# --- Call the combined recommendation function ---
combined_recommendations = get_companion_recommendations(mock_db_session, test_user_id)

print(combined_recommendations)
