# app/services/planning/planning_service.py

from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.production.crop_plan import CropPlan
from app.models.production.farm_section import FarmSection
from app.schemas.planning_schema import CropPlanCreate, FarmSectionCreate, FarmSectionUpdate
from app.services.planning.capacity_calculator import (
    calculate_required_sections,
    calculate_area_per_section,
)
from app.services.planning.batch_scheduler import build_production_batches


def _to_decimal(value) -> Decimal | None:
    if value is None:
        return None

    return Decimal(str(value))


def _location_area(location: Location) -> Decimal | None:
    width = _to_decimal(location.width_m)
    length = _to_decimal(location.length_m)

    if width is None or length is None:
        return None

    return width * length


def _used_section_area(db: Session, user_id: int, location_id: int, exclude_section_id: int | None = None) -> Decimal:
    filters = [
        FarmSection.user_id == user_id,
        FarmSection.location_id == location_id,
        FarmSection.is_active.is_(True),
    ]

    if exclude_section_id is not None:
        filters.append(FarmSection.id != exclude_section_id)

    sections = db.query(FarmSection).filter(*filters).all()

    return sum((_to_decimal(section.area_m2) or Decimal("0")) for section in sections)


def _get_owned_location(db: Session, location_id: int, user_id: int) -> Location:
    location = db.query(Location).filter(Location.id == location_id, Location.user_id == user_id).first()

    if not location:
        raise HTTPException(status_code=400, detail="Location not found or not owned by user")

    return location


def _validate_section_capacity(
    db: Session,
    user_id: int,
    location_id: int,
    width: Decimal,
    length: Decimal,
    exclude_section_id: int | None = None,
) -> Decimal:
    location = _get_owned_location(db, location_id, user_id)
    location_width = _to_decimal(location.width_m)
    location_length = _to_decimal(location.length_m)
    location_area = _location_area(location)

    if location_width is None or location_length is None or location_area is None:
        raise HTTPException(status_code=400, detail="Set location width and length before creating sections")

    area = width * length

    if width > location_width or length > location_length:
        raise HTTPException(status_code=400, detail="Section dimensions cannot be larger than the location dimensions")

    if area > location_area:
        raise HTTPException(status_code=400, detail="Section area cannot be larger than the location area")

    remaining_area = location_area - _used_section_area(db, user_id, location_id, exclude_section_id)

    if area > remaining_area:
        raise HTTPException(
            status_code=400,
            detail=f"Section area exceeds remaining location capacity ({remaining_area} m2 available)",
        )

    return area


def create_farm_section(db: Session, data: FarmSectionCreate, user_id: int):
    width = _to_decimal(data.width_m)
    length = _to_decimal(data.length_m)
    area = _validate_section_capacity(db, user_id, data.location_id, width, length)

    section = FarmSection(
        user_id=user_id,
        location_id=data.location_id,
        name=data.name,
        section_type=data.section_type,
        width_m=data.width_m,
        length_m=data.length_m,
        area_m2=area,
    )

    db.add(section)
    db.commit()
    db.refresh(section)

    return section


def get_farm_sections(db: Session, user_id: int):
    return db.query(FarmSection).filter(FarmSection.user_id == user_id, FarmSection.is_active.is_(True)).all()


def get_farm_section(db: Session, section_id: int, user_id: int):
    return (
        db.query(FarmSection)
        .filter(
            FarmSection.id == section_id,
            FarmSection.user_id == user_id,
            FarmSection.is_active.is_(True),
        )
        .first()
    )


def update_farm_section(db: Session, section_id: int, data: FarmSectionUpdate, user_id: int):
    section = get_farm_section(db, section_id, user_id)

    if not section:
        return None

    updates = data.model_dump(exclude_unset=True)
    target_location_id = updates.get("location_id", section.location_id)
    target_width = _to_decimal(updates.get("width_m", section.width_m))
    target_length = _to_decimal(updates.get("length_m", section.length_m))
    target_area = _validate_section_capacity(
        db=db,
        user_id=user_id,
        location_id=target_location_id,
        width=target_width,
        length=target_length,
        exclude_section_id=section.id,
    )

    for field in ["location_id", "name", "section_type", "width_m", "length_m"]:
        if field in updates:
            setattr(section, field, updates[field])

    section.area_m2 = target_area

    db.commit()
    db.refresh(section)

    return section


def delete_farm_section(db: Session, section_id: int, user_id: int):
    section = get_farm_section(db, section_id, user_id)

    if not section:
        return False

    section.is_active = False
    db.commit()

    return True


def create_crop_plan(db: Session, data: CropPlanCreate, user_id: int):
    plan = CropPlan(
        user_id=user_id,
        crop_name=data.crop_name,
        target_yield=data.target_yield,
        target_yield_unit=data.target_yield_unit,
        total_area_m2=data.total_area_m2,
        germination_days=data.germination_days,
        transplant_days=data.transplant_days,
        harvest_days=data.harvest_days,
        desired_harvest_interval_days=data.desired_harvest_interval_days,
        planned_start_date=data.planned_start_date,
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


def get_crop_plans(db: Session, user_id: int):
    return db.query(CropPlan).filter(CropPlan.user_id == user_id).all()


def generate_batches_for_plan(db: Session, crop_plan_id: int, user_id: int):
    plan = db.query(CropPlan).filter(CropPlan.id == crop_plan_id, CropPlan.user_id == user_id).first()

    if not plan:
        return None

    required_sections = calculate_required_sections(
        harvest_days=plan.harvest_days,
        desired_harvest_interval_days=plan.desired_harvest_interval_days,
    )

    area_per_batch = calculate_area_per_section(
        total_area_m2=plan.total_area_m2,
        section_count=required_sections,
    )

    expected_yield_per_batch = None

    if plan.target_yield is not None:
        expected_yield_per_batch = plan.target_yield / Decimal(required_sections)

    batches = build_production_batches(
        user_id=user_id,
        crop_plan_id=plan.id,
        start_date=plan.planned_start_date,
        batch_count=required_sections,
        harvest_interval_days=plan.desired_harvest_interval_days,
        germination_days=plan.germination_days,
        transplant_days=plan.transplant_days,
        harvest_days=plan.harvest_days,
        area_per_batch_m2=area_per_batch,
        expected_yield_per_batch=expected_yield_per_batch,
    )

    db.add_all(batches)
    db.commit()

    for batch in batches:
        db.refresh(batch)

    return {
        "crop_name": plan.crop_name,
        "required_sections": required_sections,
        "recommended_section_count": required_sections,
        "area_per_section_m2": area_per_batch,
        "batches": batches,
        "planning_explanation": (
            f"This plan uses overlapping batches for continuous production. "
            f"A new batch starts every {plan.desired_harvest_interval_days} days, "
            f"not after the previous batch is harvested. "
            f"Because the crop takes about {plan.harvest_days} days to harvest, "
            f"the system recommends {required_sections} production sections."
        ),
    }
