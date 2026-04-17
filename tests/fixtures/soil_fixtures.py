#tests/fixtures/soil_fixtures.py


import pytest
from app.models.soil_condition import SoilCondition


@pytest.fixture
def dry_soil(db, sensor_plant):
    soil = SoilCondition(
        plant_id=sensor_plant.id,
        moisture=20
    )
    db.add(soil)
    db.commit()
    return soil


@pytest.fixture
def wet_soil(db, sensor_plant):
    soil = SoilCondition(
        plant_id=sensor_plant.id,
        moisture=60
    )
    db.add(soil)
    db.commit()
    return soil
