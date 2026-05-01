

#app/schemas/species_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

from sqlalchemy import true


# ===============================
# SPECIES RESPONSE (FULL)
# ===============================
class SpeciesResponse(BaseModel):
    id: int
    scientific_name: Optional[str]
    common_name: Optional[str]
    is_edible: Optional[bool] = True
    is_fruit: Optional[bool] = False
    is_veg: Optional[bool] = False
    growth_rate: Optional[str] = None
    life_cycle: Optional[str]
    sunlight_requirement: Optional[str]
    watering_interval_days: Optional[int]
    recommended_soil: Optional[str]
    propagation_method: Optional[str]
    pest_susceptibility: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ===============================
# SPECIES SUGGESTION (LIGHTWEIGHT)
# ===============================
class SpeciesSuggestion(BaseModel):
    id: int
    common_name: Optional[str]
    scientific_name: Optional[str]
    score: float
    source: str

    # Add Optional and a default of None
    edible: Optional[str] = "unknown"
    growth_rate: Optional[str] = "unknown"

    model_config = ConfigDict(from_attributes=True)