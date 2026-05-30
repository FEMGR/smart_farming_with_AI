"""
Schema definitions for production tracking.

Key Point:
Defines request and response contracts for harvest records and batch updates.
"""

# app/schemas/production_schema.py

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class HarvestRecordCreate(BaseModel):
    batch_id: Optional[int] = None
    plant_id: Optional[int] = None
    harvest_date: date
    quantity: Decimal
    unit: str = "kg"
    quality_grade: Optional[str] = None
    notes: Optional[str] = None


class HarvestRecordResponse(HarvestRecordCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionBatchUpdate(BaseModel):
    status: Optional[str] = None
    actual_harvest_date: Optional[date] = None
    actual_yield: Optional[Decimal] = None
