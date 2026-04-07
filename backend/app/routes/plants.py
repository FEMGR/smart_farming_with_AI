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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.plant_schema import (
    PlantCreate,
    PlantUpdate,
    PlantResponse
)
from app.services import plant_service


router = APIRouter(prefix="/plants", tags=["Plants"])


# Create plant
@router.post("/", response_model=PlantResponse)
def create_plant(plant: PlantCreate, db: Session = Depends(get_db)):
    return plant_service.create_plant(db, plant)


# Get all plants
@router.get("/", response_model=list[PlantResponse])
def get_all_plants(db: Session = Depends(get_db)):
    return plant_service.get_all_plants(db)


# Get plant by id
@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant(plant_id: int, db: Session = Depends(get_db)):

    plant = plant_service.get_plant_by_id(db, plant_id)

    if not plant:
        raise HTTPException(
            status_code=404,
            detail="Plant not found"
        )

    return plant


# Update plant
@router.put("/{plant_id}", response_model=PlantResponse)
def update_plant(
    plant_id: int,
    plant_update: PlantUpdate,
    db: Session = Depends(get_db)
):

    updated_plant = plant_service.update_plant(
        db,
        plant_id,
        plant_update
    )

    if not updated_plant:
        raise HTTPException(
            status_code=404,
            detail="Plant not found"
        )

    return updated_plant


# Delete plant
@router.delete("/{plant_id}")
def delete_plant(plant_id: int, db: Session = Depends(get_db)):

    success = plant_service.delete_plant(db, plant_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Plant not found"
        )

    return {"message": "Plant deleted successfully"}
