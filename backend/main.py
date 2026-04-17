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



#backend/main.py

# ===============================
# FORCE MODEL REGISTRATION
# ===============================
# Ensures SQLAlchemy detects all tables
from app.models.user import User
from app.models.location import Location
from app.models.plant_group import PlantGroup
from app.models.plant import Plant
from app.models.plant_growth import PlantGrowth
from app.models.soil_condition import SoilCondition
from app.models.plant_action import PlantAction
from app.models.notification import Notification
from app.models.plant_species_cache import PlantSpeciesCache


# ===============================
# IMPORTS
# ===============================
from fastapi import FastAPI

from app.api.v1.routes import plants, auth, locations, irrigation, notifications
from app.database.db import Base, engine
from app.workers.scheduler import start_scheduler
from app.core.logger import setup_logger
from app.core.error_handler import add_exception_handlers


# ===============================
# CREATE APP
# ===============================
app = FastAPI(
    title="Smart Farming API",
    version="1.0"
)
@app.on_event("startup")
def startup_event():
    start_scheduler()


# ===============================
# LOGGER SETUP
# ===============================
logger = setup_logger()
logger.info("Starting Smart Farming API")


# ===============================
# DATABASE INIT
# ===============================
print("Using DB:", engine.url)
Base.metadata.create_all(bind=engine)


# ===============================
# ROUTES
# ===============================
app.include_router(auth.router)
app.include_router(plants.router)
app.include_router(locations.router)
app.include_router(irrigation.router)
app.include_router(notifications.router, prefix="/notifications",tags=["Notifications"])

# ===============================
# ERROR HANDLERS (CENTRALIZED)
# ===============================
add_exception_handlers(app)


# ===============================
# ROOT ENDPOINT
# ===============================
@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Smart Farming API running"
    }
