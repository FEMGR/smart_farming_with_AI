# app/models/production/production_batch.py

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Date, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class ProductionBatch(Base):
    __tablename__ = "production_batches"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    crop_plan_id = Column(Integer, ForeignKey("crop_plans.id", ondelete="CASCADE"), nullable=False)
    crop_plan_group_id = Column(Integer, ForeignKey("crop_plan_groups.id", ondelete="CASCADE"), nullable=True)
    section_id = Column(Integer, ForeignKey("farm_sections.id", ondelete="SET NULL"), nullable=True)

    batch_number = Column(Integer, nullable=False)

    seed_start_date = Column(Date, nullable=False)
    expected_germination_date = Column(Date, nullable=True)
    expected_transplant_date = Column(Date, nullable=True)
    expected_harvest_date = Column(Date, nullable=True)

    actual_harvest_date = Column(Date, nullable=True)

    allocated_area_m2 = Column(Numeric(10, 2), nullable=True)

    expected_yield = Column(Numeric(10, 2), nullable=True)
    actual_yield = Column(Numeric(10, 2), nullable=True)
    yield_unit = Column(String(50), default="kg")

    status = Column(String(50), default="planned")

    created_at = Column(TIMESTAMP, server_default=func.now())

    crop_plan = relationship("CropPlan", back_populates="batches")
    crop_plan_group = relationship("CropPlanGroup", back_populates="batches")
    section = relationship("FarmSection", back_populates="batches")

    harvest_records = relationship(
        "HarvestRecord",
        back_populates="batch",
        cascade="all, delete",
    )
