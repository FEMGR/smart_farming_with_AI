"""
Route layer for FastAPI (Lifecycle).

Key Point:
Exposes plant event and growth snapshot endpoints.

Responsibilities:
- Record lifecycle events
- Record growth measurements
- Return lifecycle history scoped to the authenticated user
"""

# app/api/v1/routes/lifecycle.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_id
from app.database.db import get_db
from app.schemas.lifecycle_schema import (
    PlantEventCreate,
    PlantEventResponse,
    GrowthSnapshotCreate,
    GrowthSnapshotResponse,
)
from app.services.lifecycle import lifecycle_service

router = APIRouter(prefix="/lifecycle", tags=["Lifecycle"])


@router.post("/events", response_model=PlantEventResponse)
def create_event(
    event: PlantEventCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return lifecycle_service.create_plant_event(db, event, user_id)


@router.get("/events", response_model=list[PlantEventResponse])
def get_events(
    plant_id: int | None = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return lifecycle_service.get_plant_events(db, user_id, plant_id)


@router.post("/growth", response_model=GrowthSnapshotResponse)
def create_growth_snapshot(
    snapshot: GrowthSnapshotCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return lifecycle_service.create_growth_snapshot(db, snapshot, user_id)


@router.get("/growth", response_model=list[GrowthSnapshotResponse])
def get_growth_snapshots(
    plant_id: int | None = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return lifecycle_service.get_growth_snapshots(db, user_id, plant_id)
