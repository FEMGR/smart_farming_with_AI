"""
Planning capacity calculations.

Key Point:
Calculates required sections and area allocation for production plans.
"""

# app/services/planning/capacity_calculator.py

import math
from decimal import Decimal
from typing import Optional


def calculate_required_sections(
    harvest_days: int,
    desired_harvest_interval_days: int,
) -> int:
    if harvest_days <= 0:
        raise ValueError("harvest_days must be greater than 0")

    if desired_harvest_interval_days <= 0:
        raise ValueError("desired_harvest_interval_days must be greater than 0")

    return max(1, math.ceil(harvest_days / desired_harvest_interval_days))


def calculate_area_per_section(
    total_area_m2: Optional[Decimal],
    section_count: int,
) -> Optional[Decimal]:
    if total_area_m2 is None:
        return None

    if section_count <= 0:
        raise ValueError("section_count must be greater than 0")

    return total_area_m2 / Decimal(section_count)
