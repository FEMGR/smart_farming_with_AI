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

# backend/main.py

from contextlib import asynccontextmanager
from pathlib import Path
import sys

from fastapi import FastAPI

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# ===============================
# FORCE MODEL REGISTRATION
# ===============================
# Ensures SQLAlchemy detects all tables

import app.models as _models  # noqa: F401,E402
from app.api.v1.routes import plants, auth, locations, irrigation, notifications, species, planning, lifecycle, production  # noqa: E402
from app.core.error_handler import add_exception_handlers  # noqa: E402
from app.core.logger import setup_logger  # noqa: E402
from app.database.db import Base, SessionLocal, engine, sync_all_postgres_id_sequences  # noqa: E402
from app.services.growth_fact_service import ensure_local_growth_facts_loaded  # noqa: E402
from app.services.plant_taxonomy_service import load_plant_taxonomy_cache  # noqa: E402
from app.workers.scheduler import start_scheduler, stop_scheduler  # noqa: E402


# ===============================
# CREATE APP
# ===============================
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # on startup
    load_plant_taxonomy_cache()
    db = SessionLocal()
    try:
        synced_sequences = sync_all_postgres_id_sequences(db, Base.metadata)
        if synced_sequences:
            logger.info("database.sequence.startup_sync count=%s", synced_sequences)
        ensure_local_growth_facts_loaded(db, force=True)
        db.commit()
    finally:
        db.close()
    start_scheduler()
    # The app is running
    yield
    # on shutdown
    stop_scheduler()


app = FastAPI(title="Smart Farming API", version="1.0", lifespan=lifespan)

# ===============================
# LOGGER SETUP
# ===============================
logger = setup_logger()
logger.info("Starting Smart Farming API")

# ===============================
# DATABASE INIT
# ===============================
logger.info(f"Using DB: {engine.url}")  # Corrected to f-string
Base.metadata.create_all(bind=engine)

# ===============================
# ROUTES
# ===============================
app.include_router(auth.router)
app.include_router(plants.router)
app.include_router(species.router)
app.include_router(locations.router)
app.include_router(planning.router)
app.include_router(lifecycle.router)
app.include_router(production.router)
app.include_router(irrigation.router)
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

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
    return {"message": "Smart Farming API running"}
