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

from sqlalchemy import Column, Integer, String
from app.database.db import Base


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    location = Column(String, nullable=False)
