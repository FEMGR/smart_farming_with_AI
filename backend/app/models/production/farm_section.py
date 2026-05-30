"""
Database model for farm sections.

Key Point:
Represents user-defined production areas inside a location.
"""

# app/models/production/farm_section.py

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class FarmSection(Base):
    __tablename__ = "farm_sections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(100), nullable=False)
    width_m = Column(Numeric(8, 2), nullable=False)
    length_m = Column(Numeric(8, 2), nullable=False)
    area_m2 = Column(Numeric(10, 2), nullable=False)

    section_type = Column(String(50), default="production")
    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    batches = relationship("ProductionBatch", back_populates="section", cascade="all, delete")
