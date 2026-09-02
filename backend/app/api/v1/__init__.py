# app/api/v1/__init__.py

from fastapi import APIRouter

from backend.app.api.v1.routes import prediction

"""
from app.api.v1.routes import (
    auth,
    irrigation,
    knowledge,
    lifecycle,
    locations,
    notifications,
    planning,
    plants,
    production,
    species,
    weather,
    prediction,
)
"""
api_router = APIRouter()

# Register existing routers...
api_router.include_router(prediction.router)  # <--- Register router
