"""
Database model for Plant.

Key Point:
Represents an individual plant owned by a user.

Responsibilities:
- Store plant-specific data (name, species, environment)
- Maintain relationships with user, location, and groups

Architecture Role:
- Core data representation for plant management

Layer Interaction:
- Used by: Services, Database layer

Notes:
- Each plant belongs to a user
- Can be associated with a location or group
"""

# app.models.plant.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Date,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship

from app.core.constants import DEFAULT_PLANT_TYPE
from app.database.db import Base


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    plant_type = Column(String(50), default=DEFAULT_PLANT_TYPE)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    group_id = Column(Integer, ForeignKey("plant_groups.id", ondelete="SET NULL"))

    # Link to species cache
    species_id = Column(Integer, ForeignKey("plant_species.id"), nullable=True)
    species = relationship("PlantSpeciesCache", backref="plants")  # Relationships

    # Link to location
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"))
    location = relationship("Location", back_populates="plants")  # Relationships

    # User-specific overrides
    watering_interval_days = Column(Integer, default=3)
    # Runtime state
    last_watered = Column(Date)
    # Metadata
    planting_date = Column(Date)
    data_source = Column(String(50), default="manual")  # {"manual", "perenual", "import", "sensor", "ai"}

    use_sensor = Column(Boolean, default=False, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="plants")
    group = relationship("PlantGroup", back_populates="plants")

    growth_records = relationship("PlantGrowth", back_populates="plant", cascade="all, delete")
    soil_records = relationship("SoilCondition", back_populates="plant", cascade="all, delete")
    actions = relationship("PlantAction", back_populates="plant", cascade="all, delete")
    notifications = relationship("Notification", back_populates="plant", cascade="all, delete")
