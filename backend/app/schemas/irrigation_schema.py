"""
Schema definition for irrigation responses.

Key Point:
Defines validation and data structure for irrigation-related endpoints.

Responsibilities:
- Standardize data returned to clients for irrigation status
- Validate and serialize irrigation response data

Architecture Role:
- Data contract layer between backend and client

Layer Interaction:
- Communicates with: Services (irrigation_service)
- Used by: Routes (irrigation endpoints)

Data Flow:
Irrigation logic executed in service layer
        ↓
Relevant plant data mapped to schema
        ↓
Schema validates and structures response
        ↓
Clean, minimal data returned to client
"""

# app/schemas/irrigation_schema.py

from pydantic import BaseModel
from datetime import date
from typing import Optional


class PlantNeedsWaterResponse(BaseModel):
    plant_id: int
    name: str
    last_watered: Optional[date]
    watering_interval_days: Optional[int]
    use_sensor: bool
    needs_water: bool
