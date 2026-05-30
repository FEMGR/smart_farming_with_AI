# app/services/planning/batch_scheduler.py

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from app.models.production.production_batch import ProductionBatch


def build_production_batches(
    user_id: int,
    crop_plan_id: int,
    start_date: date,
    batch_count: int,
    harvest_interval_days: int,
    germination_days: int,
    transplant_days: int,
    harvest_days: int,
    area_per_batch_m2: Optional[Decimal] = None,
    expected_yield_per_batch: Optional[Decimal] = None,
) -> list[ProductionBatch]:
    """
    Build overlapping production batches for continuous production.

    Important:
    The next batch starts based on the desired harvest interval,
    NOT after the previous batch is harvested.

    Example:
    harvest_days = 45
    harvest_interval_days = 15

    Batch 1 seed: day 0
    Batch 2 seed: day 15
    Batch 3 seed: day 30

    This creates a continuous harvest pipeline.
    """

    if batch_count <= 0:
        raise ValueError("batch_count must be greater than 0")

    if harvest_interval_days <= 0:
        raise ValueError("harvest_interval_days must be greater than 0")

    batches = []

    for index in range(batch_count):
        batch_number = index + 1

        # Continuous production logic:
        # Start each new batch by interval, not by previous harvest date.
        seed_date = start_date + timedelta(days=index * harvest_interval_days)

        batch = ProductionBatch(
            user_id=user_id,
            crop_plan_id=crop_plan_id,
            batch_number=batch_number,
            seed_start_date=seed_date,
            expected_germination_date=seed_date + timedelta(days=germination_days),
            expected_transplant_date=seed_date + timedelta(days=transplant_days),
            expected_harvest_date=seed_date + timedelta(days=harvest_days),
            allocated_area_m2=area_per_batch_m2,
            expected_yield=expected_yield_per_batch,
            status="planned",
        )

        batches.append(batch)

    return batches
