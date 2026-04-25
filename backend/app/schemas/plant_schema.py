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

#app.schemas.plant_schema.py

from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional
from datetime import date, datetime

from app.schemas.location_schema import LocationResponse
from app.schemas.species_schema import SpeciesResponse
from app.utils.plant_logic import get_effective_watering


# ===============================
# CREATE
# ===============================
class PlantCreate(BaseModel):
    name: str
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
    species_id: Optional[int]
    # Linked species (from cache)
    species: Optional[SpeciesResponse] = None

    user_id: int

    location_id: Optional[int]
    location: Optional[LocationResponse] = None

    group_id: Optional[int]

    environment_type: str
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
    def effective_watering_interval(self) -> int:
        return get_effective_watering(self)
