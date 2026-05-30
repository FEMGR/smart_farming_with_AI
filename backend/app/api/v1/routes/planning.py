"""
Route layer for FastAPI (Planning).

Key Point:
Exposes farm section, crop plan, polyculture preview, and saved plan endpoints.

Responsibilities:
- Validate planning requests with schemas
- Delegate planning logic to service modules
- Scope all planning data to the authenticated user
"""

# app/api/v1/routes/planning.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_id
from app.database.db import get_db

from app.schemas.planning_schema import (
    FarmSectionCreate,
    FarmSectionUpdate,
    FarmSectionResponse,
    CropPlanCreate,
    CropPlanResponse,
    SuccessionPlanPreview,
    PolyculturePreviewRequest,
    PolycultureConfirmRequest,
)

from app.services.planning import planning_service
from app.services.planning import polyculture_planner

router = APIRouter(prefix="/planning", tags=["Planning"])


@router.post("/sections", response_model=FarmSectionResponse)
def create_section(
    section: FarmSectionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return planning_service.create_farm_section(db, section, user_id)


@router.get("/sections", response_model=list[FarmSectionResponse])
def get_sections(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return planning_service.get_farm_sections(db, user_id)


@router.patch("/sections/{section_id}", response_model=FarmSectionResponse)
def update_section(
    section_id: int,
    section: FarmSectionUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    updated = planning_service.update_farm_section(db, section_id, section, user_id)

    if not updated:
        raise HTTPException(status_code=404, detail="Farm section not found")

    return updated


@router.delete("/sections/{section_id}")
def delete_section(
    section_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    deleted = planning_service.delete_farm_section(db, section_id, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Farm section not found")

    return {"message": "Farm section deleted successfully"}


@router.post("/crop-plans", response_model=CropPlanResponse)
def create_crop_plan(
    plan: CropPlanCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return planning_service.create_crop_plan(db, plan, user_id)


@router.get("/crop-plans", response_model=list[CropPlanResponse])
def get_crop_plans(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return planning_service.get_crop_plans(db, user_id)


@router.post("/crop-plans/{crop_plan_id}/generate-batches", response_model=SuccessionPlanPreview)
def generate_batches(
    crop_plan_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    result = planning_service.generate_batches_for_plan(db, crop_plan_id, user_id)

    if not result:
        raise HTTPException(status_code=404, detail="Crop plan not found")

    return result


@router.post("/polyculture-preview")
def polyculture_preview(
    request: PolyculturePreviewRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return polyculture_planner.generate_polyculture_preview(
            db=db,
            user_id=user_id,
            location_id=request.location_id,
            section_ids=request.section_ids,
            intended_crops=request.intended_crops,
            start_date=request.start_date,
            harvest_interval_days=request.harvest_interval_days,
            desired_harvest_batches=request.desired_harvest_batches,
            plant_variations_per_group=request.plant_variations_per_group,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/polyculture-plans")
def get_saved_polyculture_plans(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return polyculture_planner.get_saved_polyculture_plans(db=db, user_id=user_id)


@router.delete("/polyculture-plans/{crop_plan_id}")
def delete_saved_polyculture_plan(
    crop_plan_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    deleted = polyculture_planner.delete_saved_polyculture_plan(
        db=db,
        user_id=user_id,
        crop_plan_id=crop_plan_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Saved polyculture plan not found")

    return {"message": "Saved polyculture plan deleted successfully"}


@router.post("/polyculture-confirm")
def polyculture_confirm(
    request: PolycultureConfirmRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return polyculture_planner.confirm_polyculture_plan(
            db=db,
            user_id=user_id,
            location_id=request.location_id,
            section_ids=request.section_ids,
            intended_crops=request.intended_crops,
            start_date=request.start_date,
            harvest_interval_days=request.harvest_interval_days,
            desired_harvest_batches=request.desired_harvest_batches,
            plant_variations_per_group=request.plant_variations_per_group,
            name=request.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
