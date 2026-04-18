"""
Database module for connection and session management.

Key Point:
Provides database connection, session handling, and base model configuration.

Responsibilities:
- Create SQLAlchemy engine (database connection)
- Provide session factory for database operations
- Define base class for ORM models
- Manage database session lifecycle for API requests

Architecture Role:
- Acts as the bridge between application and PostgreSQL
- Centralizes database configuration and access

Layer Interaction:
- Used by: Models, Services, Dependencies (get_db), Core modules
- Communicates with: PostgreSQL database

Data Flow:
Application starts
        ↓
Database engine created using configuration
        ↓
Session factory (SessionLocal) initialized
        ↓
Routes request database session via dependency
        ↓
Session used for database operations
        ↓
Session closed after request completes

Notes:
- Each request gets its own database session
- Sessions are safely closed after use
- Engine configuration is loaded from environment variables
"""

# app.database.db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Import DATABASE_URL from config
from app.core.config import DATABASE_URL

# ===============================
# CREATE DATABASE ENGINE
# ===============================

#Engine is the core connection between Python and PostgreSQL, uses the DATABASE_URL from .env
engine = create_engine(
    DATABASE_URL,
    echo=False  # set True to log SQL in terminal
)

# ===============================
# CREATE SESSION
# ===============================
#Session is used to talk to the database. Open->operations->close session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ===============================
# BASE MODEL
# ===============================
Base = declarative_base() #a factory function used to create a base class for the db

# ===============================
# DATABASE DEPENDENCY
# ===============================

# used in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
