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

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.schemas.location_schema import LocationResponse

# ===============================
# CREATE
# ===============================
class PlantCreate(BaseModel):
    name: str
    species: Optional[str] = None

    location_id: Optional[int] = None
    group_id: Optional[int] = None

    environment_type: Optional[str] = "outdoor"
    planting_date: Optional[date] = None

    source: Optional[str] = "manual"
    use_sensor: Optional[bool] = False

    # common watering interval
    watering_interval_days: Optional[int] = 3


# ===============================
# UPDATE
# ===============================
class PlantUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    location_id: Optional[int] = None
    group_id: Optional[int] = None
    environment_type: Optional[str] = None
    planting_date: Optional[date] = None
    is_synced: Optional[bool] = None
    use_sensor: Optional[bool] = None
    watering_interval_days: Optional[int] = None
    last_watered: Optional[date] = None


# ===============================
# RESPONSE
# ===============================
class PlantResponse(BaseModel):
    id: int
    name: str
    species: Optional[str]
    user_id: int
    location_id: Optional[int]
    group_id: Optional[int]
    environment_type: str
    planting_date: Optional[date]
    is_synced: bool
    source: str
    use_sensor: bool
    created_at: datetime
    last_watered: Optional[date]
    watering_interval_days: int
    location: Optional[LocationResponse] = None
    model_config = ConfigDict(from_attributes=True)
