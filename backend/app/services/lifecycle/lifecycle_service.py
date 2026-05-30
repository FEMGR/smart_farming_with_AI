"""
Service layer for lifecycle tracking.

Key Point:
Creates and retrieves plant events and growth snapshots.
"""

# app/services/lifecycle/lifecycle_service.py

from sqlalchemy.orm import Session

from app.models.lifecycle.plant_event import PlantEvent
from app.models.lifecycle.growth_snapshot import GrowthSnapshot
from app.schemas.lifecycle_schema import PlantEventCreate, GrowthSnapshotCreate


def create_plant_event(db: Session, data: PlantEventCreate, user_id: int):
    event = PlantEvent(
        user_id=user_id,
        plant_id=data.plant_id,
        batch_id=data.batch_id,
        event_type=data.event_type,
        event_date=data.event_date,
        notes=data.notes,
        data=data.data,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_plant_events(db: Session, user_id: int, plant_id: int | None = None):
    query = db.query(PlantEvent).filter(PlantEvent.user_id == user_id)

    if plant_id is not None:
        query = query.filter(PlantEvent.plant_id == plant_id)

    return query.order_by(PlantEvent.event_date.desc()).all()


def create_growth_snapshot(db: Session, data: GrowthSnapshotCreate, user_id: int):
    snapshot = GrowthSnapshot(
        user_id=user_id,
        plant_id=data.plant_id,
        batch_id=data.batch_id,
        recorded_date=data.recorded_date,
        stage=data.stage,
        height_cm=data.height_cm,
        width_cm=data.width_cm,
        leaf_count=data.leaf_count,
        health_status=data.health_status,
        vigor_score=data.vigor_score,
        image_path=data.image_path,
        notes=data.notes,
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return snapshot


def get_growth_snapshots(db: Session, user_id: int, plant_id: int | None = None):
    query = db.query(GrowthSnapshot).filter(GrowthSnapshot.user_id == user_id)

    if plant_id is not None:
        query = query.filter(GrowthSnapshot.plant_id == plant_id)

    return query.order_by(GrowthSnapshot.recorded_date.desc()).all()
