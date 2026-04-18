"""
Database model for Location.

Key Point:
Represents a physical or logical location for plants.

Responsibilities:
- Store location details
- Associate plants with environments

Architecture Role:
- Supports organization of plants by environment

Layer Interaction:
- Used by: Services, Database layer
"""

#app.models.location.py

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    # GEO DATA (for future weather integration)
    latitude = Column(Numeric(9, 6), nullable=True)
    longitude = Column(Numeric(9, 6), nullable=True)
    # CONTEXT DATA (for farming logic)
    description = Column(String, nullable=True)
    environment_type = Column(String, nullable=True)  # indoor/outdoor/greenhouse
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="locations")
    plants = relationship("Plant", back_populates="location")
