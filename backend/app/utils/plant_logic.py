"""
Utility layer for Plant-specific logic.

Key Point:
Provides derived calculations and helper logic for plant behavior.

Responsibilities:
- Compute effective watering interval
- Combine plant overrides with species defaults
- Provide reusable logic across services and features

Architecture Role:
- Supporting logic layer for services and decision-making
- Keeps business rules out of models and routes

Layer Interaction:
- Communicates with: Plant model, PlantSpeciesCache
- Called by: Services (irrigation, plant, notifications)

Data Flow:
Plant object received
        ↓
Check for user-defined overrides
        ↓
Fallback to species default if available
        ↓
Return final computed value
"""



#app/utils/plant_logic.py

from datetime import timedelta, date
from app.models import Plant, SoilCondition
from app.services.irrigation_service import MOISTURE_THRESHOLD

def get_effective_watering(plant) -> int:
    """
    Determine the final watering interval for a plant.

    Priority:
    1. User-defined override (plant.watering_interval_days)
    2. Species default (plant.species.watering_interval_days)
    3. System fallback (3 days)
    """

    if plant.watering_interval_days:
        return plant.watering_interval_days

    if plant.species and plant.species.watering_interval_days:
        return plant.species.watering_interval_days

    return 3

# ===============================
# CHECK IF PLANT NEEDS WATER
# ===============================
def _needs_watering_with_soil(plant: Plant, soil: SoilCondition | None) -> bool:
    # SENSOR MODE
    if plant.use_sensor and soil and soil.moisture is not None:
        return float(soil.moisture) < MOISTURE_THRESHOLD

    # SCHEDULE MODE
    if not plant.watering_interval_days:
        return False

    if not plant.last_watered:
        return True

    next_watering_date = plant.last_watered + timedelta(days=plant.watering_interval_days)

    return date.today() >= next_watering_date
