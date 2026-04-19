"""
Main application entry point.

Key Point:
Initializes and launches the FastAPI backend application.

Responsibilities:
- Create FastAPI app instance
- Register API routes
- Configure logging and error handling
- Initialize database connections and tables
- Start application server

Architecture Role:
- Acts as the composition root of the system
- Connects all layers without containing business logic

Layer Interaction:
- Communicates with: Routes, Core (config, logger, error handler), Database
- Indirectly connects: Services, Models, Schemas (through routes)

Data Flow:
Client (Swagger / Frontend)
        ↓
Routes (handle HTTP requests, validate using schemas)
        ↓
Services (business logic)
        ↓
Models (database structure)
        ↓
Database Layer (db.py)
        ↓
PostgreSQL

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
from contextlib import asynccontextmanager
from app.api.v1.routes import plants, auth, locations, irrigation, notifications
from app.database.db import Base, engine
from app.workers.scheduler import start_scheduler, stop_scheduler
from app.core.logger import setup_logger
from app.core.error_handler import add_exception_handlers


# ===============================
# CREATE APP
# ===============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    start_scheduler()
    # The app is running
    yield
    # on shutdown
    stop_scheduler()


app = FastAPI(
    title="Smart Farming API",
    version="1.0",
    lifespan=lifespan
)

# ===============================
# LOGGER SETUP
# ===============================
logger = setup_logger()
logger.info("Starting Smart Farming API")

# ===============================
# DATABASE INIT
# ===============================
logger.info("Using DB:", engine.url)
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
