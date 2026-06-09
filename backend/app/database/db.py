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

import re

from sqlalchemy import Integer, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base

# Import DATABASE_URL from config
from app.core.config import DATABASE_URL
from app.core.logger import setup_logger

logger = setup_logger()

# ===============================
# CREATE DATABASE ENGINE
# ===============================

# Engine is the core connection between Python and PostgreSQL, uses the DATABASE_URL from .env
engine = create_engine(DATABASE_URL, echo=False)  # set True to log SQL in terminal

# ===============================
# CREATE SESSION
# ===============================
# Session is used to talk to the database. Open->operations->close session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===============================
# BASE MODEL
# ===============================
Base = declarative_base()  # a factory function used to create a base class for the db


_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _quote_identifier(identifier: str) -> str:
    if not _IDENTIFIER_RE.match(identifier):
        raise ValueError(f"Unsafe SQL identifier: {identifier!r}")
    return f'"{identifier}"'


def sync_postgres_sequence(db, table_name: str, id_column: str = "id") -> bool:
    """Align a PostgreSQL serial/identity sequence with the current max table id."""
    if db.get_bind().dialect.name != "postgresql":
        return False

    table_ref = _quote_identifier(table_name)
    column_ref = _quote_identifier(id_column)

    sequence_name = db.execute(
        text("SELECT pg_get_serial_sequence(:table_name, :id_column)"),
        {"table_name": table_name, "id_column": id_column},
    ).scalar()
    if not sequence_name:
        return False

    max_id = db.execute(text(f"SELECT COALESCE(MAX({column_ref}), 0) FROM {table_ref}")).scalar() or 0
    db.execute(
        text("SELECT setval(to_regclass(:sequence_name), :sequence_value, :is_called)"),
        {
            "sequence_name": sequence_name,
            "sequence_value": max(max_id, 1),
            "is_called": max_id > 0,
        },
    )
    logger.info("database.sequence.synced table=%s column=%s max_id=%s", table_name, id_column, max_id)
    return True


def sync_all_postgres_id_sequences(db, metadata=None) -> int:
    """Repair all ORM integer primary-key sequences after imports/manual inserts."""
    if db.get_bind().dialect.name != "postgresql":
        return 0

    metadata = metadata or Base.metadata
    synced = 0
    for table in metadata.sorted_tables:
        id_column = table.columns.get("id")
        if id_column is None or not id_column.primary_key or not isinstance(id_column.type, Integer):
            continue
        try:
            if sync_postgres_sequence(db, table.name, id_column.name):
                synced += 1
        except (SQLAlchemyError, ValueError) as exc:
            logger.warning("database.sequence.sync_failed table=%s error=%s", table.name, exc)
    return synced


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
