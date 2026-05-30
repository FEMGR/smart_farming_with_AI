# app/services/planning/succession_planner.py

from decimal import Decimal
from typing import Optional

from app.services.planning.capacity_calculator import (
    calculate_required_sections,
    calculate_area_per_section,
)


def preview_succession_plan(
    crop_name: str,
    harvest_days: int,
    desired_harvest_interval_days: int,
    total_area_m2: Optional[Decimal] = None,
):
    required_sections = calculate_required_sections(
        harvest_days=harvest_days,
        desired_harvest_interval_days=desired_harvest_interval_days,
    )

    area_per_section = calculate_area_per_section(
        total_area_m2=total_area_m2,
        section_count=required_sections,
    )

    return {
        "crop_name": crop_name,
        "required_sections": required_sections,
        "recommended_section_count": required_sections,
        "area_per_section_m2": area_per_section,
        "reason": (
            f"{harvest_days} harvest days / " f"{desired_harvest_interval_days} day harvest interval " f"requires {required_sections} production sections."
        ),
    }
