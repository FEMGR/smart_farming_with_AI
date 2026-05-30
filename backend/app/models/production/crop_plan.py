"""
Database model for production crop plans.

Key Point:
Represents a saved monoculture or polyculture production plan and owns its
groups and batches.
"""

# app/models/production/crop_plan.py
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Date, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class CropPlan(Base):
    __tablename__ = "crop_plans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(150), nullable=True)
    plan_type = Column(String(50), default="polyculture")  # monoculture / polyculture

    # Legacy/simple-crop fields kept for backward compatibility
    crop_name = Column(String(100), nullable=True)
    target_yield = Column(Numeric(10, 2), nullable=True)
    target_yield_unit = Column(String(50), default="kg")
    total_area_m2 = Column(Numeric(10, 2), nullable=True)

    germination_days = Column(Integer, default=7)
    transplant_days = Column(Integer, default=14)
    harvest_days = Column(Integer, default=45)
    desired_harvest_interval_days = Column(Integer, default=14)

    planned_start_date = Column(Date, nullable=False)

    status = Column(String(50), default="draft")
    created_at = Column(TIMESTAMP, server_default=func.now())

    groups = relationship("CropPlanGroup", back_populates="crop_plan", cascade="all, delete")
    batches = relationship("ProductionBatch", back_populates="crop_plan", cascade="all, delete")
