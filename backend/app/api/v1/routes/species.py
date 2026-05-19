"""
Route layer for FastAPI (Species).

Key Point:
Handles API endpoints related to plant species search and suggestions.

Responsibilities:
- Accept user input for species queries
- Validate and sanitize query parameters
- Call service layer to retrieve species suggestions
- Return structured species data to client

Architecture Role:
- Entry point for species-related API requests
- Bridges client requests with species service logic

Layer Interaction:
- Communicates with: Services (perenual_service), Database (via dependency)
- Called by: Client applications (frontend, API consumers)

Data Flow:
User sends species query (e.g., search input)
        ↓
Query validated and cleaned
        ↓
Service layer retrieves matching species
        ↓
Results formatted using schema
        ↓
List of species suggestions returned to client
"""


#app/api/v1/routes/species.py

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.species_schema import SpeciesSuggestion
from app.services.perenual_service import suggest_species

router = APIRouter(
    prefix="/species",
    tags=["Species"]
)


# ===============================
# SUGGEST SPECIES
# ===============================
@router.get("/suggest", response_model=List[SpeciesSuggestion])
def suggest_species_route(
    query: str = Query(..., min_length=2, max_length=50),
    db: Session = Depends(get_db)
):
    query = query.strip()

    if not query:
        return []

    return suggest_species(db, query)
