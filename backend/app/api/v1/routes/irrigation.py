# backend/app/api/v1/routes/irrigation.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.api.deps import get_current_user_id
from app.services import irrigation_service

# ✅ Add prefix here for clean routing
router = APIRouter(
    prefix="/irrigation",
    tags=["Irrigation"]
)


# ===============================
# CHECK PLANTS NEEDING WATER
# ===============================
@router.get("/needs-water")
def get_plants_needing_water(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Returns plants that need watering for the logged-in user.
    Also triggers notification creation if needed.
    """
    plants = irrigation_service.get_plants_needing_water(
        db=db,
        user_id=user_id
    )

    return plants


# ===============================
# WATER A PLANT
# ===============================
@router.post("/water/{plant_id}")
def water_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Marks a plant as watered (only if it belongs to the user).
    """
    plant = irrigation_service.water_plant(
        db=db,
        plant_id=plant_id,
        user_id=user_id
    )

    if not plant:
        raise HTTPException(
            status_code=404,
            detail="Plant not found or not owned by user"
        )

    return {
        "message": "Plant watered successfully",
        "plant_id": plant.id
    }


# ===============================
# BULK WATERING (OPTIONAL)
# ===============================
@router.post("/water-all")
def water_all_plants(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Waters all plants that are currently due.
    """
    plants = irrigation_service.water_all_due_plants(
        db=db,
        user_id=user_id
    )

    return {
        "message": f"{len(plants)} plants watered",
        "count": len(plants)
    }
