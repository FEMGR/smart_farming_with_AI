"""
Plant API routes.

Defines what the API can do by defining endpoints (HTTP methods) and hand it over to service layer.
HTTP methods used:
GET     → retrieve data
POST    → create new data
PUT     → update existing data
DELETE  → remove data

Receives request with JSON
↓
Call services
↓
Uses schema to validate
↓
Uses model to create object
↓
Uses db session saves
↓
Returns response
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database.db import get_db
from app.schemas.plant_schema import (
    PlantCreate,
    PlantUpdate,
    PlantResponse
)
from app.services import plant_service


router = APIRouter(
    prefix="/plants",
    tags=["Plants"]
)

logger = logging.getLogger("smart_farming")


# Create plant
@router.post(
    "/",
    response_model=PlantResponse,
    status_code=status.HTTP_201_CREATED
)
def create_plant(
    plant: PlantCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Creating plant: {plant.name}")

    new_plant = plant_service.create_plant(db, plant)

    logger.info(f"Plant created with ID: {new_plant.id}")

    return new_plant


# Get all plants
@router.get(
    "/",
    response_model=list[PlantResponse]
)
def get_all_plants(
    db: Session = Depends(get_db)
):
    logger.info("Fetching all plants")

    plants = plant_service.get_all_plants(db)

    logger.info(f"{len(plants)} plants retrieved")

    return plants


# Get plant by id
@router.get(
    "/{plant_id}",
    response_model=PlantResponse
)
def get_plant(
    plant_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching plant ID: {plant_id}")

    plant = plant_service.get_plant_by_id(db, plant_id)

    if not plant:
        logger.warning(f"Plant not found: {plant_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )

    return plant


# Update plant
@router.put(
    "/{plant_id}",
    response_model=PlantResponse
)
def update_plant(
    plant_id: int,
    plant_update: PlantUpdate,
    db: Session = Depends(get_db)
):
    logger.info(f"Updating plant ID: {plant_id}")

    updated_plant = plant_service.update_plant(
        db,
        plant_id,
        plant_update
    )

    if not updated_plant:
        logger.warning(f"Plant not found for update: {plant_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )

    logger.info(f"Plant updated: {plant_id}")

    return updated_plant


# Delete plant
@router.delete(
    "/{plant_id}",
    status_code=status.HTTP_200_OK
)
def delete_plant(
    plant_id: int,
    db: Session = Depends(get_db)
):
    logger.info(f"Deleting plant ID: {plant_id}")

    success = plant_service.delete_plant(db, plant_id)

    if not success:
        logger.warning(f"Plant not found for deletion: {plant_id}")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant not found"
        )

    logger.info(f"Plant deleted: {plant_id}")

    return {
        "message": "Plant deleted successfully"
    }

