"""
Database model for PlantGroup.

Key Point:
Represents a grouping of plants, including companion planting arrangements.

Responsibilities:
- Group plants based on compatibility or user-defined organization
- Maintain relationships with user and plants

Architecture Role:
- Supports companion planting features and plant organization

Layer Interaction:
- Used by: Services, Database layer

Notes:
- Companion plant recommendations are determined in the service layer
- A group belongs to a user and can contain multiple plants
"""


#app.models.plant_group.py

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class PlantGroup(Base):
    __tablename__ = "plant_groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    name = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="plant_groups")
    plants = relationship("Plant", back_populates="group")
