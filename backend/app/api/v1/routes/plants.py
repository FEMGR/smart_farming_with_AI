"""
Route layer for FastAPI (Plants).

Key Point:
Handles API endpoints for plant management.

Responsibilities:
- Receive plant-related HTTP requests
- Validate input using schemas
- Call plant service layer
- Return plant data responses

Architecture Role:
- Entry point for plant-related operations
- Keeps routes clean by delegating logic to services

Layer Interaction:
- Communicates with: Services (plant_service), Schemas, Dependencies

Data Flow:
Client Request (plant operation)
        ↓
Route receives request
        ↓
Schema validates input
        ↓
Plant service processes logic
        ↓
Database updated via models
        ↓
Response returned to client
"""

#app.api.routes.plants.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_current_user_id
from app.database.db import get_db
from app.schemas.plant_schema import PlantCreate, PlantUpdate, PlantResponse
from app.services import plant_service
from app.core.exceptions import NotFoundError, PermissionDeniedError


router = APIRouter(
    prefix="/plants",
    tags=["Plants"]
)


# ===============================
# CREATE PLANT
# ===============================
@router.post("/", response_model=PlantResponse)
def create_plant(
    plant: PlantCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    try:
        return plant_service.create_plant(db, plant, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

# ===============================
# CREATE PLANT WITH SUGGESTION
# ===============================
@router.post("/with-species", response_model=PlantResponse)
def create_plant_with_species(
    plant: PlantCreate,
    species_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    try:
        return plant_service.create_plant_with_species(
            db, plant, user_id, species_id
        )

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ===============================
# GET ALL PLANTS
# ===============================
@router.get("/", response_model=List[PlantResponse])
def get_plants(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return plant_service.get_plants(db, user_id)


# ===============================
# GET SINGLE PLANT
# ===============================
@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    plant = plant_service.get_plant(db, plant_id, user_id)

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return plant


# ===============================
# UPDATE PLANT
# ===============================
@router.patch("/{plant_id}", response_model=PlantResponse)
def update_plant(
    plant_id: int,
    plant_update: PlantUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    try:
        updated = plant_service.update_plant(db, plant_id, plant_update, user_id)

        if not updated:
            raise HTTPException(status_code=404, detail="Plant not found")

        return updated

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ===============================
# DELETE PLANT
# ===============================
@router.delete("/{plant_id}")
def delete_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    deleted = plant_service.delete_plant(db, plant_id, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Plant deleted successfully"}

