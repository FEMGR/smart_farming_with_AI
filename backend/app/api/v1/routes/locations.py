"""
Route layer for FastAPI (Locations).

Key Point:
Handles API endpoints for managing plant locations.

Responsibilities:
- Receive location-related requests
- Validate input using schemas
- Call location service layer
- Return location data responses

Architecture Role:
- Entry point for location management
- Delegates business logic to services

Layer Interaction:
- Communicates with: Services (location_service), Schemas, Dependencies

Data Flow:
Client Request (location operation)
        ↓
Route receives request
        ↓
Schema validates input
        ↓
Location service processes logic
        ↓
Database updated via models
        ↓
Response returned to client
"""

#app.api.routes.locations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.api.dependencies import get_current_user_id
from app.schemas.location_schema import LocationCreate, LocationUpdate, LocationResponse
from app.services import location_service

router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


# ===============================
# CREATE
# ===============================
@router.post("/", response_model=LocationResponse)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return location_service.create_location(db, location, user_id)


# ===============================
# GET ALL
# ===============================
@router.get("/", response_model=List[LocationResponse])
def get_locations(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return location_service.get_locations(db, user_id)


# ===============================
# GET ONE
# ===============================
@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    location = location_service.get_location(db, location_id, user_id)

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    return location


# ===============================
# UPDATE
# ===============================
@router.patch("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    location_update: LocationUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    updated = location_service.update_location(db, location_id, location_update, user_id)

    if not updated:
        raise HTTPException(status_code=404, detail="Location not found")

    return updated


# ===============================
# DELETE
# ===============================
@router.delete("/{location_id}")
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    deleted = location_service.delete_location(db, location_id, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Location not found")

    return {"message": "Location deleted successfully"}
