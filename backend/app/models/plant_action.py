"""
Database model for PlantAction.

Key Point:
Represents actions performed on plants (e.g., watering, fertilizing).

Responsibilities:
- Record actions taken on plants
- Track timestamps and action types

Architecture Role:
- Provides historical activity tracking for plants

Layer Interaction:
- Used by: Services, Database layer
- Does NOT depend on: Routes, HTTP layer

Notes:
- Helps support automation and auditing of plant care
"""

#app.models.plant_action.py

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class PlantAction(Base):
    __tablename__ = "plant_actions"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))
    action_type = Column(String(50))
    quantity = Column(Numeric(8, 2))
    unit = Column(String(50))
    notes = Column(String)
    performed_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    plant = relationship("Plant", back_populates="actions")
