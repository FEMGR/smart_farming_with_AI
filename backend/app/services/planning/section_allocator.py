# app/services/planning/section_allocator.py

from sqlalchemy.orm import Session

from app.models.production.farm_section import FarmSection
from app.models.production.production_batch import ProductionBatch


def assign_sections_to_batches(db: Session, user_id: int, batches: list[ProductionBatch]):
    sections = (
        db.query(FarmSection)
        .filter(
            FarmSection.user_id == user_id,
            FarmSection.is_active.is_(True),
            FarmSection.section_type == "production",
        )
        .order_by(FarmSection.id.asc())
        .all()
    )

    if not sections:
        return batches

    for index, batch in enumerate(batches):
        section = sections[index % len(sections)]
        batch.section_id = section.id

    return batches
