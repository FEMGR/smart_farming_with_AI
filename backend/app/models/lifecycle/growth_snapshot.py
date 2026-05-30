"""
Database model for plant growth snapshots.

Key Point:
Stores time-based plant measurements and health observations.
"""

# app/models/lifecycle/growth_snapshot.py

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Date, TIMESTAMP, func

from app.database.db import Base


class GrowthSnapshot(Base):
    __tablename__ = "growth_snapshots"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(Integer, ForeignKey("production_batches.id", ondelete="SET NULL"), nullable=True)

    recorded_date = Column(Date, nullable=False)

    stage = Column(String(50), nullable=True)
    height_cm = Column(Numeric(8, 2), nullable=True)
    width_cm = Column(Numeric(8, 2), nullable=True)
    leaf_count = Column(Integer, nullable=True)

    health_status = Column(String(50), nullable=True)
    vigor_score = Column(Integer, nullable=True)

    image_path = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
