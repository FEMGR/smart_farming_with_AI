"""
This file defines the User database model.

Purpose:
- Represents users in the database
- Stores authentication data (email + hashed password)

Architecture Role:
- Part of the "models" layer
- Maps Python objects to database tables using SQLAlchemy

Key Notes:
- Passwords are NOT stored in plain text
- Only hashed_password is stored for security
"""

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
