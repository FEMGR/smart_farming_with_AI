"""
weather_service.py

Fetch weather data from Open-Meteo and save the raw JSON
into ai/datasets/raw/.

The preprocessing pipeline will later load and clean this data.
"""

# backend/app/services/weather_services.py

import json
from pathlib import Path

import requests

# -----------------------------------------------------
# Locate project folders
# -----------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DATA_DIR = PROJECT_ROOT / "ai" / "datasets" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------
# Weather API
# -----------------------------------------------------

BASE_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(latitude: float, longitude: float) -> dict:
    """
    Fetch weather data from Open-Meteo for explicit coordinates.
    """

    params = {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "rain",
                "precipitation",
                "pressure_msl",
                "wind_speed_10m",
                "wind_direction_10m",
            ]
        ),
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation_probability",
                "rain",
                "wind_speed_10m",
                "soil_temperature_0cm",
                "soil_moisture_0_to_1cm",
            ]
        ),
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
            ]
        ),
        "forecast_days": 7,
        "timezone": "auto",
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


# -----------------------------------------------------
# Save JSON
# -----------------------------------------------------


def save_weather_json(data: dict, filename: str = "weather.json") -> Path:
    """
    Save weather JSON into ai/datasets/raw/.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = RAW_DATA_DIR / filename

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return file_path


def save_raw_json(data: dict, filename: str = "weather.json") -> Path:
    """
    Save raw weather JSON for AI dataset ingestion.
    """

    return save_weather_json(data, filename)


def fetch_weather_and_save(latitude: float, longitude: float, filename: str = "weather.json") -> dict:
    """
    Fetch weather data, save the raw JSON, and return the same data.
    """

    data = fetch_weather(latitude, longitude)
    save_raw_json(data, filename)

    return data


def fetch_and_save_weather(latitude: float, longitude: float) -> Path:
    """
    Fetch weather data and save it.
    """

    data = fetch_weather(latitude, longitude)

    return save_raw_json(data)
