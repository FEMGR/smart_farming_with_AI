"""
Service layer for yield summaries.

Key Point:
Aggregates harvested quantity for the authenticated user.
"""

# app/services/production/yield_service.py

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.production.harvest_record import HarvestRecord


def get_total_yield(db: Session, user_id: int):
    total = db.query(func.coalesce(func.sum(HarvestRecord.quantity), 0)).filter(HarvestRecord.user_id == user_id).scalar()

    return {"total_yield": total}
