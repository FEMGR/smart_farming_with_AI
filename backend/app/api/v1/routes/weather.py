"""
Route layer for weather data.
"""

# backend/app/api/v1/routes/weather.py

import requests
from fastapi import APIRouter, HTTPException, Query

from app.schemas.weather_schema import WeatherRequest
from app.services import weather_service

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current")
def get_weather(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
):
    """
    Return weather data for coordinates supplied by the frontend.
    """

    return _fetch_weather_or_raise(latitude=latitude, longitude=longitude)


@router.post("/current")
def post_weather(request: WeatherRequest):
    """
    Return weather data for coordinates supplied by the frontend.
    """

    return _fetch_weather_or_raise(latitude=request.latitude, longitude=request.longitude)


def _fetch_weather_or_raise(latitude: float, longitude: float) -> dict:
    try:
        return weather_service.fetch_weather_and_save(latitude=latitude, longitude=longitude)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="Weather provider request failed") from exc
