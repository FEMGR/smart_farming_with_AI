"""
Main FastAPI application entry point.
the system launcher and central hub, the place that will conta
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



"""

from fastapi import FastAPI

from app.database.db import engine, Base
from app.routes import plants

# Create FastAPI app
app = FastAPI(
    title="Smart Farming System",
    version="1.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(plants.router)


@app.get("/")
def root():
    return {"message": "Smart Farming API is running"}
