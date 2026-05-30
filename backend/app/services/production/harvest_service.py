# app/services/production/harvest_service.py

from sqlalchemy.orm import Session

from app.models.production.harvest_record import HarvestRecord
from app.models.production.production_batch import ProductionBatch
from app.schemas.production_schema import HarvestRecordCreate


def create_harvest_record(db: Session, data: HarvestRecordCreate, user_id: int):
    record = HarvestRecord(
        user_id=user_id,
        batch_id=data.batch_id,
        plant_id=data.plant_id,
        harvest_date=data.harvest_date,
        quantity=data.quantity,
        unit=data.unit,
        quality_grade=data.quality_grade,
        notes=data.notes,
    )

    db.add(record)

    if data.batch_id:
        batch = (
            db.query(ProductionBatch)
            .filter(
                ProductionBatch.id == data.batch_id,
                ProductionBatch.user_id == user_id,
            )
            .first()
        )

        if batch:
            batch.actual_harvest_date = data.harvest_date
            batch.actual_yield = data.quantity
            batch.yield_unit = data.unit
            batch.status = "harvested"

    db.commit()
    db.refresh(record)

    return record


def get_harvest_records(db: Session, user_id: int):
    return db.query(HarvestRecord).filter(HarvestRecord.user_id == user_id).order_by(HarvestRecord.harvest_date.desc()).all()
