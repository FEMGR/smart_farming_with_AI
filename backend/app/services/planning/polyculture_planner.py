# app/services/planning/polyculture_planner.py

from decimal import Decimal
from types import SimpleNamespace

from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.production.farm_section import FarmSection
from app.models.production.crop_plan import CropPlan
from app.models.production.crop_plan_group import CropPlanGroup
from app.models.production.production_batch import ProductionBatch

from app.services.grouping_service import generate_groups_internal, generate_groups_display
from app.services.positioning_service import generate_layout
from app.services.prolog.prolog_service import get_recommendations, get_companion_suggestions
from app.services.lifecycle.timeline_service import generate_group_timeline, get_group_timeline
from app.services.planning.capacity_calculator import calculate_required_sections
from app.utils.prolog_normalizer import to_prolog_atom


def _normalize_name(name: str) -> str:
    return str(name or "").strip().lower().replace(" ", "_")


def _build_virtual_plants(intended_crops: list[str]):
    """
    The grouping engine expects Plant-like objects.
    Planning happens before real Plant rows exist, so we create lightweight virtual plants.
    """
    virtual_plants = []

    for index, crop in enumerate(intended_crops, start=1):
        virtual_plants.append(
            SimpleNamespace(
                id=index,
                name=crop,
                plant_type="vegetable",
                species_id=None,
                species=None,
                group_id=None,
                bed_x=None,
                bed_y=None,
                location_id=None,
                location=None,
                watering_interval_days=None,
            )
        )

    return virtual_plants


def _plants_to_atoms(virtual_plants) -> list[str]:
    atoms = []

    for plant in virtual_plants:
        atom = to_prolog_atom(
            {
                "name": plant.name,
                "species": None,
            }
        )

        if atom:
            atoms.append(atom)

    return list(dict.fromkeys(atoms))


def _get_sections(db: Session, user_id: int, location_id: int, section_ids: list[int]):
    sections = (
        db.query(FarmSection)
        .filter(
            FarmSection.user_id == user_id,
            FarmSection.location_id == location_id,
            FarmSection.id.in_(section_ids),
            FarmSection.is_active.is_(True),
        )
        .order_by(FarmSection.id.asc())
        .all()
    )

    return sections


def _get_available_sections_not_used(db: Session, user_id: int, location_id: int, used_section_ids: list[int]):
    return (
        db.query(FarmSection)
        .filter(
            FarmSection.user_id == user_id,
            FarmSection.location_id == location_id,
            FarmSection.is_active.is_(True),
            FarmSection.id.notin_(used_section_ids),
        )
        .order_by(FarmSection.id.asc())
        .all()
    )


def _section_to_dict(section: FarmSection):
    return {
        "id": section.id,
        "name": section.name,
        "location_id": section.location_id,
        "area_m2": section.area_m2,
        "width_m": section.width_m,
        "length_m": section.length_m,
    }


def _allocate_sections_to_groups(groups: list[dict], sections: list[FarmSection]):
    """
    Basic allocation:
    - one safe group per section if possible
    - if fewer sections than groups, assign what we can and warn
    """
    warnings = []

    for index, group in enumerate(groups):
        if index < len(sections):
            section = sections[index]
            group["section_id"] = section.id
            group["section_name"] = section.name
            group["allocated_area_m2"] = section.area_m2
            group["section_width_m"] = section.width_m
            group["section_length_m"] = section.length_m
        else:
            group["section_id"] = None
            group["section_name"] = None
            group["allocated_area_m2"] = None
            group["section_width_m"] = None
            group["section_length_m"] = None
            group.setdefault("warnings", [])
            group["warnings"].append("No available section assigned to this compatibility group.")
            warnings.append(f"Group {group.get('group_id')} has no section. Add another section or reduce intended crops.")

    return groups, warnings


def _extract_group_main_crops(group: dict) -> list[str]:
    return [plant["name"] for plant in group.get("plants", [])]


def _extract_group_companion_suggestions(group_main_crops: list[str], suggestions: dict) -> list[dict]:
    result = []

    suggest_good = suggestions.get("suggest_good", {})

    normalized_main = {_normalize_name(crop) for crop in group_main_crops}

    for crop in group_main_crops:
        crop_atom = _normalize_name(crop)

        for suggestion in suggest_good.get(crop_atom, []):
            suggested_plant = suggestion.get("plant")

            if not suggested_plant:
                continue

            if _normalize_name(suggested_plant) in normalized_main:
                continue

            result.append(suggestion)

    # Deduplicate by plant name
    seen = set()
    unique = []

    for item in result:
        plant = item.get("plant")
        if plant in seen:
            continue
        seen.add(plant)
        unique.append(item)

    return unique


def generate_polyculture_preview(
    db: Session,
    user_id: int,
    location_id: int,
    section_ids: list[int],
    intended_crops: list[str],
    start_date,
    harvest_interval_days: int,
):
    if not intended_crops:
        raise ValueError("intended_crops cannot be empty")

    if harvest_interval_days <= 0:
        raise ValueError("harvest_interval_days must be greater than 0")

    location = db.query(Location).filter(Location.id == location_id, Location.user_id == user_id).first()

    if not location:
        raise ValueError("Location not found or not owned by user")

    sections = _get_sections(db, user_id, location_id, section_ids)

    if len(sections) != len(set(section_ids)):
        raise ValueError("One or more sections do not exist or do not belong to this location")

    virtual_plants = _build_virtual_plants(intended_crops)
    atoms = _plants_to_atoms(virtual_plants)

    interactions = get_recommendations(atoms)
    recommended_items = interactions.get("recommended", [])
    avoid_items = interactions.get("avoid", [])

    recommended_pairs = [item["pair"] for item in recommended_items]
    avoid_pairs = [item["pair"] for item in avoid_items]

    pair_reasons = {item["pair"]: item for item in recommended_items}

    groups_internal = generate_groups_internal(
        plants=virtual_plants,
        valid_pairs=recommended_pairs,
        avoid_pairs=avoid_pairs,
    )

    groups_display = generate_groups_display(
        plants=virtual_plants,
        valid_pairs=recommended_pairs,
        avoid_pairs=avoid_pairs,
        pair_reasons=pair_reasons,
    )

    groups, allocation_warnings = _allocate_sections_to_groups(groups_internal, sections)

    layout = generate_layout(
        groups=groups,
        recommended_pairs=recommended_pairs,
        avoid_pairs=avoid_pairs,
        grid_width=10,
        grid_height=10,
    )

    suggestions = get_companion_suggestions(atoms)

    total_area = sum((section.area_m2 or Decimal("0")) for section in sections)

    preview_groups = []

    for group in groups:
        main_crops = _extract_group_main_crops(group)
        companions = _extract_group_companion_suggestions(main_crops, suggestions)

        group_timeline_basis = get_group_timeline(main_crops)

        required_batches = calculate_required_sections(
            harvest_days=group_timeline_basis["harvest_days"],
            desired_harvest_interval_days=harvest_interval_days,
        )

        timeline = generate_group_timeline(
            start_date=start_date,
            main_crops=main_crops,
            harvest_interval_days=harvest_interval_days,
            batch_count=required_batches,
        )

        preview_groups.append(
            {
                "group_id": group.get("group_id"),
                "section_id": group.get("section_id"),
                "section_name": group.get("section_name"),
                "main_crops": main_crops,
                "suggested_companions": companions,
                "allocated_area_m2": group.get("allocated_area_m2"),
                "warnings": group.get("warnings", []),
                "required_batches": required_batches,
                "timeline_basis": group_timeline_basis,
                "timeline": timeline,
            }
        )

    warnings = []
    warnings.extend(allocation_warnings)
    warnings.extend(layout.get("warnings", []))

    if len(groups_internal) > len(sections):
        warnings.append(f"This plan needs {len(groups_internal)} safe compatibility groups, " f"but only {len(sections)} section(s) were selected.")

    extra_sections = _get_available_sections_not_used(db, user_id, location_id, section_ids)

    suggested_additional_sections = []

    if len(groups_internal) > len(sections):
        suggested_additional_sections = [_section_to_dict(section) for section in extra_sections]

        if suggested_additional_sections:
            warnings.append("You have unused sections in the same location that can be added to this plan.")
        else:
            warnings.append("No unused section is available in this location. Create another section or reduce crops.")

    return {
        "location_id": location_id,
        "section_ids": section_ids,
        "group_count": len(preview_groups),
        "total_available_area_m2": total_area,
        "groups": preview_groups,
        "groups_display": groups_display,
        "layout": layout,
        "warnings": warnings,
        "suggested_additional_sections": suggested_additional_sections,
        "avoid_pairs": avoid_items,
        "recommended_pairs": recommended_items,
    }


def confirm_polyculture_plan(
    db: Session,
    user_id: int,
    location_id: int,
    section_ids: list[int],
    intended_crops: list[str],
    start_date,
    harvest_interval_days: int,
    name: str | None = None,
):
    preview = generate_polyculture_preview(
        db=db,
        user_id=user_id,
        location_id=location_id,
        section_ids=section_ids,
        intended_crops=intended_crops,
        start_date=start_date,
        harvest_interval_days=harvest_interval_days,
    )

    plan = CropPlan(
        user_id=user_id,
        location_id=location_id,
        name=name or "Polyculture Production Plan",
        plan_type="polyculture",
        crop_name=None,
        planned_start_date=start_date,
        desired_harvest_interval_days=harvest_interval_days,
        status="active",
    )

    db.add(plan)
    db.flush()

    saved_groups = []

    for group in preview["groups"]:
        crop_group = CropPlanGroup(
            user_id=user_id,
            crop_plan_id=plan.id,
            section_id=group.get("section_id"),
            group_number=group["group_id"],
            group_name=f"Group {group['group_id']}",
            main_crops=group["main_crops"],
            suggested_companions=group["suggested_companions"],
            warnings=group["warnings"],
            allocated_area_m2=group.get("allocated_area_m2"),
        )

        db.add(crop_group)
        db.flush()

        saved_groups.append(crop_group)

        for timeline_item in group["timeline"]:
            batch = ProductionBatch(
                user_id=user_id,
                crop_plan_id=plan.id,
                crop_plan_group_id=crop_group.id,
                section_id=group.get("section_id"),
                batch_number=timeline_item["batch_number"],
                seed_start_date=timeline_item["seed_start_date"],
                expected_germination_date=timeline_item["expected_germination_date"],
                expected_transplant_date=timeline_item["expected_transplant_date"],
                expected_harvest_date=timeline_item["expected_harvest_date"],
                allocated_area_m2=group.get("allocated_area_m2"),
                status="planned",
            )

            db.add(batch)

    db.commit()
    db.refresh(plan)

    return {
        "message": "Polyculture plan confirmed",
        "crop_plan_id": plan.id,
        "preview": preview,
    }
