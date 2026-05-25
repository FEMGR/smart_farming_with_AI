from app.models.plant import Plant
from app.services.plant_service import get_companion_recommendations

# --- Mocking Database and Plant Objects ---


class MockSpecies:
    def __init__(
        self,
        scientific_name,
        common_name=None,
        id=None,
        sunlight_requirement="full_sun",
        watering="medium",
        recommended_soil="well_drained",
        max_height_ft=5,
        max_width_ft=2,
    ):
        self.id = id if id is not None else 9999  # Assign a default ID if not provided
        self.scientific_name = scientific_name
        self.common_name = common_name
        self.sunlight_requirement = sunlight_requirement
        self.watering = watering
        self.recommended_soil = recommended_soil
        self.max_height_ft = max_height_ft
        self.max_width_ft = max_width_ft


class MockGroup:
    def __init__(self, name, id=None):
        self.id = id if id is not None else 8888
        self.name = name


class MockLocation:
    def __init__(self, width_m=None, length_m=None):
        self.width_m = width_m
        self.length_m = length_m


class MockPlant:
    def __init__(
        self,
        id,
        name,
        plant_type,
        species_scientific_name,
        group_id=None,
        group_name=None,
        watering_interval_days=3,
        location_id=1,
        bed_x=None,
        bed_y=None,
        location_width_m=None,
        location_length_m=None,
    ):
        self.id = id
        self.name = name
        self.plant_type = plant_type
        self.species = MockSpecies(species_scientific_name, id=id * 100)  # Pass ID to species mock
        self.species_id = self.species.id  # Add species_id directly to MockPlant
        self.group_id = group_id
        self.group = MockGroup(group_name, id=group_id) if group_name else None
        self.watering_interval_days = watering_interval_days
        self.location_id = location_id
        self.location = MockLocation(location_width_m, location_length_m)
        self.bed_x = bed_x
        self.bed_y = bed_y
        print(f"DEBUG: MockPlant created: id={self.id}, name={self.name}, species_id={self.species_id}")


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
                {"id": 1, "name": "tomato", "type": "vegetable", "species_name": "solanum lycopersicum", "x": 0, "y": 0},
                {"id": 2, "name": "ginger", "type": "spice", "species_name": "zingiber officinale", "x": 1, "y": 0},
                {"id": 3, "name": "cucumber", "type": "vegetable", "species_name": "cucumis sativus", "x": 0, "y": 1},
                {"id": 4, "name": "dandelion", "type": "flower", "species_name": "taraxacum officinale", "x": 2, "y": 2},
                {"id": 5, "name": "rye", "type": "grain", "species_name": "secale cereale", "x": 5, "y": 5},
                {"id": 6, "name": "grape", "type": "fruit", "species_name": "vitis vinifera", "x": 8, "y": 8},
                {"id": 7, "name": "hydrangea", "type": "flower", "species_name": "hydrangea spp.", "x": 9, "y": 9},
                {"id": 8, "name": "artichoke", "type": "vegetable", "species_name": "cynara scolymus", "x": 4, "y": 1},
                {"id": 9, "name": "dahlia", "type": "flower", "species_name": "dahlia spp.", "x": 1, "y": 4},
                {"id": 10, "name": "nasturtium", "type": "flower", "species_name": "tropaeolum majus", "x": 3, "y": 3},
                {"id": 11, "name": "cabbage", "type": "vegetable", "species_name": "brassica oleracea var. capitata", "x": 0, "y": 5},
                {"id": 12, "name": "broccoli", "type": "vegetable", "species_name": "brassica oleracea var. italica", "x": 1, "y": 5},
            ]
            mock_plant_objects = [
                MockPlant(p["id"], p["name"], p["type"], p["species_name"], bed_x=p["x"], bed_y=p["y"], location_width_m=10.0, location_length_m=10.0)
                for p in mock_plants_data
            ]
            return MockQuery(mock_plant_objects)
        return MockQuery([])  # Return empty for other models


# Instantiate our mock database session and a dummy user ID
mock_db_session = MockSession()

test_user_id = 1

# --- Call the combined recommendation function ---
combined_recommendations = get_companion_recommendations(mock_db_session, test_user_id)

print(combined_recommendations)
