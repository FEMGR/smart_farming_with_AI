"""
Route layer for FastAPI (Plants).

Key Point:
Handles API endpoints for plant management and recommendations.

Responsibilities:
- Receive plant-related HTTP requests
- Validate input using schemas
- Call plant service layer for CRUD operations and recommendations
- Return plant data responses

Architecture Role:
- Entry point for plant-related operations
- Keeps routes clean by delegating business logic to services

Layer Interaction:
- Communicates with: Services (plant_service), Schemas, Dependencies

Data Flow:
Client Request (plant operation or recommendation)
        ↓
Route receives request
        ↓
Schema validates input (for CRUD operations)
        ↓
Plant service processes logic (CRUD, recommendations)
        ↓
Database updated/queried via models
        ↓
Response returned to client
"""

# app.api.routes.plants.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_current_user_id
from app.database.db import get_db
from app.schemas.plant_schema import PlantCreate, PlantUpdate, PlantResponse
from app.services import plant_service
from app.core.exceptions import NotFoundError, PermissionDeniedError

router = APIRouter(prefix="/plants", tags=["Plants"])


# ===============================
# COMPANION PLANT RECOMMENDATIONS
# ===============================
@router.get("/recommendations")
def get_recommendations_endpoint(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """
    Retrieves companion plant recommendations for the user's existing plants.
    """
    return plant_service.get_companion_recommendations(db, user_id)


# ===============================
# CREATE PLANT
# ===============================
@router.post("/", response_model=PlantResponse)
def create_plant(
    plant: PlantCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Creates a new plant entry for the current user.
    """
    try:
        return plant_service.create_plant(db, plant, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ===============================
# CREATE PLANT WITH SPECIES
# ===============================
@router.post("/with-species", response_model=PlantResponse)
def create_plant_with_species(
    plant: PlantCreate,
    species_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Creates a new plant entry linked to an existing species for the current user.
    """
    try:
        return plant_service.create_plant_with_species(db, plant, user_id, species_id)

    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ===============================
# GET ALL PLANTS
# ===============================
@router.get("/", response_model=List[PlantResponse])
def get_plants(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """
    Retrieves all plants belonging to the current user.
    """
    return plant_service.get_plants(db, user_id)


# ===============================
# GET SINGLE PLANT
# ===============================
@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Retrieves a single plant by its ID for the current user.
    """
    plant = plant_service.get_plant(db, plant_id, user_id)

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return plant


# ===============================
# DUPLICATE PLANT
# ===============================
@router.post("/{plant_id}/duplicate", response_model=PlantResponse)
def duplicate_plant(
    plant_id: int,
    group_id: int | None = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Duplicates an existing plant entry for the current user.
    """
    try:
        duplicate = plant_service.duplicate_plant(db, plant_id, user_id, group_id)

        if not duplicate:
            raise HTTPException(status_code=404, detail="Plant not found")

        return duplicate

    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ===============================
# UPDATE PLANT
# ===============================
@router.patch("/{plant_id}", response_model=PlantResponse)
def update_plant(
    plant_id: int,
    plant_update: PlantUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Updates an existing plant's details for the current user.
    """
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
    user_id: int = Depends(get_current_user_id),
):
    """
    Deletes a plant entry by its ID for the current user.
    """
    deleted = plant_service.delete_plant(db, plant_id, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Plant not found")

    return {"message": "Plant deleted successfully"}
