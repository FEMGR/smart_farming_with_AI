"""
Plant schemas.

Schemas define how data is received and returned by the API. What kind of data is allowed to enter or leave the system.
Defines what data looks like when entering or leaving the API.
Pydantic also checks and validates the data automatically.
validates input
structures output
controls request/response format
prevents bad data
documents API automatically
"""

from pydantic import BaseModel


# ===============================
# BASE SCHEMA
# ===============================

class PlantBase(BaseModel):
    name: str
    species: str
    location: str


# ===============================
# CREATE SCHEMA
# ===============================

class PlantCreate(PlantBase):
    pass


# ===============================
# UPDATE SCHEMA
# ===============================

class PlantUpdate(PlantBase):
    """
    Used when updating plant.
    """
    pass


# ===============================
# RESPONSE SCHEMA
# ===============================

class PlantResponse(PlantBase):
    id: int

    class Config:
        orm_mode = True
