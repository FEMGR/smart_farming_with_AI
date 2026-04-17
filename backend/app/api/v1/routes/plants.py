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
from typing import List
from app.api.deps import get_current_user_id
from app.database.db import get_db
from app.schemas.plant_schema import PlantCreate, PlantUpdate, PlantResponse
from app.services import plant_service

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

