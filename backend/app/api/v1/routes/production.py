"""
Route layer for FastAPI (Production).

Key Point:
Exposes harvest and yield endpoints for production tracking.

Responsibilities:
- Record harvest quantities
- Return harvest history
- Summarize total yield for the authenticated user
"""

# app/api/v1/routes/production.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_id
from app.database.db import get_db
from app.schemas.production_schema import HarvestRecordCreate, HarvestRecordResponse
from app.services.production import harvest_service
from app.services.production import yield_service

router = APIRouter(prefix="/production", tags=["Production"])


@router.post("/harvests", response_model=HarvestRecordResponse)
def create_harvest(
    harvest: HarvestRecordCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return harvest_service.create_harvest_record(db, harvest, user_id)


@router.get("/harvests", response_model=list[HarvestRecordResponse])
def get_harvests(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return harvest_service.get_harvest_records(db, user_id)


@router.get("/yield-summary")
def get_yield_summary(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return yield_service.get_total_yield(db, user_id)
