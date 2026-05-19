from typing import Optional

# app/schemas/species_schema.py
from pydantic import BaseModel, ConfigDict


# ===============================
# SPECIES RESPONSE (FULL)
# ===============================
class SpeciesResponse(BaseModel):

    id: int

    scientific_name: Optional[str]

    common_name: Optional[str]

    plant_type: Optional[str]

    description: Optional[str]

    is_edible: Optional[bool]

    is_fruit: Optional[bool]

    is_veg: Optional[bool]

    medicinal: Optional[bool]

    growth_rate: Optional[str]

    life_cycle: Optional[str]

    care_level: Optional[str]

    watering: Optional[str]

    sunlight_requirement: Optional[str]

    watering_interval_days: Optional[int]

    recommended_soil: Optional[str]

    propagation_method: Optional[str]

    pest_susceptibility: Optional[str]

    indoor: Optional[bool]

    tropical: Optional[bool]

    default_image_url: Optional[str]

    thumbnail_url: Optional[str]

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

    edible: Optional[str] = "unknown"

    growth_rate: Optional[str] = "unknown"

    plant_type: Optional[str] = None

    thumbnail_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
