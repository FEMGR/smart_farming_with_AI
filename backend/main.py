"""
Main is FastAPI application entry point.
the system launcher and central hub
Client (Swagger / Frontend)
        ↓
Routes (API endpoints/ handle HTTP)
        ↓
Services (handle business logic)
        ↓
Schemas (data validation)
        ↓
Models (database structure)
        ↓
db.py (database connection)
        ↓
PostgreSQL

Purpose:
- Initialize FastAPI app
- Register routes
- Setup logging and error handling
- Create database tables

Architecture Role:
- Connects all layers together
- Starts the backend server
"""

from fastapi import FastAPI

from app.api.v1.routes import plants, auth
from app.database.db import Base, engine

from app.core.logger import setup_logger
from app.core.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# ✅ 1. Create app FIRST
app = FastAPI(
    title="Smart Farming API",
    version="1.0"
)

# ✅ 2. Setup logger
logger = setup_logger()
logger.info("Starting Smart Farming API")

# ✅ 3. Create database tables
Base.metadata.create_all(bind=engine)

# ✅ 4. Register routes
app.include_router(auth.router)
app.include_router(plants.router)

# ✅ 5. Register exception handlers
app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.add_exception_handler(
    Exception,
    general_exception_handler
)


@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Smart Farming API running"
    }