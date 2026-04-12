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

from sqlalchemy import Column, Integer, String
from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)
