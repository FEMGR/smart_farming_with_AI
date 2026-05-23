"""
Schema definitions for Location.

Key Point:
Defines validation and data structure for location-related operations.

Responsibilities:
- Validate incoming location data
- Structure location data returned to clients

Architecture Role:
- Acts as a contract between client and location API endpoints

Layer Interaction:
- Used by: Routes, Services
"""

# app.schemas.location_schema.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ===============================
# CREATE
# ===============================
class LocationCreate(BaseModel):
    name: str  # e.g. "Backyard", "Balcony"
    description: Optional[str] = None
    environment_type: Optional[str] = None  # indoor / outdoor / greenhouse
    width_m: Optional[float] = None
    length_m: Optional[float] = None


# ===============================
# UPDATE
# ===============================
class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    environment_type: Optional[str] = None
    width_m: Optional[float] = None
    length_m: Optional[float] = None


# ===============================
# RESPONSE
# ===============================
class LocationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    environment_type: Optional[str]
    width_m: Optional[float]
    length_m: Optional[float]
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
