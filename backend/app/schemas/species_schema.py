

#app/schemas/species_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional


# ===============================
# SPECIES RESPONSE (FULL)
# ===============================
class SpeciesResponse(BaseModel):
    id: int
    scientific_name: Optional[str]
    common_name: Optional[str]

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
