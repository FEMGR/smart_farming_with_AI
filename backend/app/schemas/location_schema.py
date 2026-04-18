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

#app.schemas.location_schema.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ===============================
# CREATE
# ===============================
class LocationCreate(BaseModel):
    name: str  # e.g. "Backyard", "Balcony"
    description: Optional[str] = None
    environment_type: Optional[str] = None  # indoor / outdoor / greenhouse


# ===============================
# UPDATE
# ===============================
class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    environment_type: Optional[str] = None


# ===============================
# RESPONSE
# ===============================
class LocationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    environment_type: Optional[str]
    user_id: int
    created_at: datetime

model_config = ConfigDict(from_attributes=True)
'''
    class Config:
        from_attributes = True
'''

