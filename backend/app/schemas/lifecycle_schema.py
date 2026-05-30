# app/schemas/lifecycle_schema.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict


class PlantEventCreate(BaseModel):
    plant_id: Optional[int] = None
    batch_id: Optional[int] = None
    event_type: str
    event_date: date
    notes: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class PlantEventResponse(PlantEventCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GrowthSnapshotCreate(BaseModel):
    plant_id: int
    batch_id: Optional[int] = None
    recorded_date: date

    stage: Optional[str] = None
    height_cm: Optional[Decimal] = None
    width_cm: Optional[Decimal] = None
    leaf_count: Optional[int] = None

    health_status: Optional[str] = None
    vigor_score: Optional[int] = None

    image_path: Optional[str] = None
    notes: Optional[str] = None


class GrowthSnapshotResponse(GrowthSnapshotCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
