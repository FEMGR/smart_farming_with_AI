"""
Plant database model.

This defines the structure of the plants table in PostgreSQL.
Defines how data or the structure of the table is stored inside PostgreSQL.

defines database table
defines columns
defines types
defines primary keys
SQLAlchemy converts this to SQL

"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    group_id = Column(Integer, ForeignKey("plant_groups.id", ondelete="SET NULL"))
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"))

    name = Column(String(100), nullable=False)
    species = Column(String(100))

    external_species_id = Column(String(100))
    is_synced = Column(Boolean, default=False)

    environment_type = Column(String(50), default="outdoor")

    planting_date = Column(Date)
    source = Column(String(50), default="manual")

    # 🌱 ===============================
    # IRRIGATION FIELDS (NEW)
    # ===============================
    last_watered = Column(Date, nullable=True)  # last watering date
    watering_interval_days = Column(Integer, default=3)  # default every 3 days

    # 🌱 SENSOR CONTROL (NEW)
    use_sensor = Column(Boolean, default=False, nullable=False)

    # ===============================

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="plants")
    group = relationship("PlantGroup", back_populates="plants")
    location = relationship("Location", back_populates="plants")

    growth_records = relationship("PlantGrowth", back_populates="plant", cascade="all, delete")
    soil_records = relationship("SoilCondition", back_populates="plant", cascade="all, delete")
    actions = relationship("PlantAction", back_populates="plant", cascade="all, delete")
    notifications = relationship("Notification", back_populates="plant", cascade="all, delete")
