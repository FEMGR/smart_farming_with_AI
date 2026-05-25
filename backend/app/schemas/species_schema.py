"""
Schema layer for FastAPI (Species).

Key Point:
Defines the data structures for representing plant species information, both in full detail and as lightweight suggestions.

Responsibilities:
- Structure the data for full species details (SpeciesResponse).
- Structure the data for species suggestions, including a relevance score (SpeciesSuggestion).
- Ensure data consistency and type validation for species-related API responses.

Architecture Role:
- Acts as the data contract between the API and its consumers for species data.
- Facilitates clear and consistent data exchange.

Layer Interaction:
- Communicates with: API routes (for input/output validation), Services (for data transformation).
- Called by: API routes when returning species data.

Data Flow:
Species data retrieved from database/external sources
        ↓
Transformed into SpeciesResponse or SpeciesSuggestion schema
        ↓
Returned as API response
"""

# app/schemas/species_schema.py


from typing import Optional
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
