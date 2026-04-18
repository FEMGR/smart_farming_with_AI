"""
Database model for User.

Key Point:
Represents a system user and their authentication data.

Responsibilities:
- Store user credentials (email and hashed password)
- Maintain relationships with user-owned entities

Architecture Role:
- Core data representation for user accounts

Layer Interaction:
- Used by: Services, Database layer

"""

#app.models.user.py

from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    locations = relationship("Location", back_populates="user", cascade="all, delete")
    plants = relationship("Plant", back_populates="user", cascade="all, delete")
    plant_groups = relationship("PlantGroup", back_populates="user", cascade="all, delete")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete")
