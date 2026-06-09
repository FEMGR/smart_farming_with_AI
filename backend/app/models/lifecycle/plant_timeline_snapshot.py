"""Persisted per-plant timeline snapshots."""

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from app.database.db import Base


class PlantTimelineSnapshot(Base):
    __tablename__ = "plant_timeline_snapshots"
    __table_args__ = (UniqueConstraint("plant_id", name="uq_plant_timeline_snapshots_plant_id"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True)
    growth_fact_id = Column(Integer, ForeignKey("plant_growth_facts.id", ondelete="SET NULL"), nullable=True)

    snapshot_date = Column(Date, nullable=False)
    basis = Column(String(80), nullable=False, default="local_growth_facts")
    timeline_data = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    plant = relationship("Plant", back_populates="timeline_snapshots")
    growth_fact = relationship("PlantGrowthFact")
