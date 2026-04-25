

#app/api/v1/routes/species.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.schemas.species_schema import SpeciesSuggestion
from app.services.plant_service import suggest_species

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


