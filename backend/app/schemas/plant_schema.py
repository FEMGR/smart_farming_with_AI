"""
Schema definitions for Plant.

Key Point:
Defines validation and data structure for plant-related operations.

Responsibilities:
- Validate plant input data
- Structure plant response data

Architecture Role:
- Acts as a contract between client and plant API endpoints

Layer Interaction:
- Used by: Routes, Services
"""

# app.schemas.plant_schema.py

from pydantic import BaseModel, ConfigDict, computed_field, model_validator
from typing import Optional
from datetime import date, datetime

from app.schemas.location_schema import LocationResponse
from app.schemas.species_schema import SpeciesResponse
from app.utils.plant_logic import get_effective_watering
from typing import Literal
from app.core.constants import PLANT_TYPES

# Convert the list to a Type that Pydantic understands
PlantType = Literal[tuple(PLANT_TYPES)]


# ===============================
# CREATE
# ===============================
class PlantCreate(BaseModel):
    name: str
    plant_type: PlantType = "vegetable"
    species_name: Optional[str] = None
    location_id: Optional[int] = None
    group_id: Optional[int] = None

    environment_type: Optional[str] = "outdoor"
    planting_date: Optional[date] = None

    data_source: Optional[str] = "manual"
    use_sensor: Optional[bool] = False

    # Optional override
    watering_interval_days: Optional[int] = None


# ===============================
# UPDATE
# ===============================
class PlantUpdate(BaseModel):
    name: Optional[str] = None
    # This forces the user to pick one of these specific words
    plant_type: PlantType = "vegetable"
    location_id: Optional[int] = None
    group_id: Optional[int] = None

    environment_type: Optional[str] = None
    planting_date: Optional[date] = None

    use_sensor: Optional[bool] = None
    watering_interval_days: Optional[int] = None
    last_watered: Optional[date] = None


# ===============================
# RESPONSE
# ===============================
class PlantResponse(BaseModel):
    id: int
    name: str
    plant_type: Optional[str] = "fruit"
    species_id: Optional[int]
    # Linked species (from cache)
    species: Optional[SpeciesResponse] = None

    user_id: int

    location_id: Optional[int]
    location: Optional[LocationResponse] = None
    environment_type: Optional[str] = "outdoor"

    group_id: Optional[int]
    planting_date: Optional[date]

    data_source: str
    use_sensor: bool

    created_at: datetime
    last_watered: Optional[date]

    # Raw DB value (user override)
    watering_interval_days: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

    # ===============================
    # COMPUTED FIELD
    # ===============================
    @computed_field
    @property
    # If user override exists, use it; otherwise, use the species value
    def effective_watering_interval(self) -> int:
        return get_effective_watering(self)

    @model_validator(mode="before")
    @classmethod
    def get_environment_from_location(cls, data):
        # If the plant has a location, use the location's type
        if hasattr(data, "location") and data.location:
            data.environment_type = data.location.environment_type
        return data
