"""
Database model for crop plan groups.

Key Point:
Stores compatible crop groups, assigned farm sections, and saved layout data.
"""

# app/models/production/crop_plan_group.py

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, JSON, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class CropPlanGroup(Base):
    __tablename__ = "crop_plan_groups"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    crop_plan_id = Column(Integer, ForeignKey("crop_plans.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("farm_sections.id", ondelete="SET NULL"), nullable=True)

    group_number = Column(Integer, nullable=False)
    group_name = Column(String(100), nullable=True)

    main_crops = Column(JSON, nullable=False, default=list)
    suggested_companions = Column(JSON, nullable=True, default=list)
    layout_json = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True, default=list)

    allocated_area_m2 = Column(Numeric(10, 2), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    crop_plan = relationship("CropPlan", back_populates="groups")
    section = relationship("FarmSection")
    batches = relationship("ProductionBatch", back_populates="crop_plan_group", cascade="all, delete")
