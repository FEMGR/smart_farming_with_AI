"""Prediction layer for trained Smart Farming AI models.

The layer accepts current plant, sensor, and weather data, recreates the same
feature names used during training, applies saved preprocessing artifacts, and
generates predictions from trained model artifacts.
"""

# ai/inference/prediction_layer.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any
import json
import sys

import pandas as pd
import requests
from ai.core.constants import (  # noqa: E402
    ARTIFACTS_DIR,
    TROPICAL_COUNTRIES,
)
from ai.core.ml.metadata import load_metadata  # noqa: E402
from ai.core.ml.model_io import load_model, load_preprocessing_artifacts  # noqa: E402
from ai.core.ml.prediction import predict_with_confidence  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

TASK_ALIASES = {
    "irrigation": "irrigration_prediction",
    "growth": "growth_prediction",
    "disease": "disease_prediction",
    "yield": "yield_prediction",
}

SUPPORTED_TASKS = (
    "irrigration_prediction",
    "growth_prediction",
    "disease_prediction",
    "yield_prediction",
)

CANONICAL_ALIASES = {
    "timestamp": ("timestamp", "datetime", "date_time", "date", "time", "recorded_at", "created_at"),
    "temperature": ("temperature", "temp", "temp_c", "temperature_c", "air_temperature", "air_temp_c", "temperature_2m"),
    "humidity": ("humidity", "humidity_pct", "relative_humidity", "relative_humidity_2m", "rh"),
    "soil_moisture": ("soil_moisture", "soil_moisture_pct", "soil_water", "soil_water_pct", "moisture", "soil_moisture_0_to_1cm"),
    "soil_ph": ("soil_ph", "ph"),
    "rainfall": ("rainfall", "rainfall_mm", "rain", "precipitation", "precipitation_mm"),
    "rain_probability": ("rain_probability", "precipitation_probability", "precip_probability", "pop"),
    "wind_speed": ("wind_speed", "wind_speed_10m", "wind_kmh", "wind"),
    "latitude": ("latitude", "lat"),
    "longitude": ("longitude", "lon", "lng"),
    "current_height_cm": ("current_height_cm", "height_cm"),
    "light_intensity": ("light_intensity", "light", "light_lux", "sunlight", "lux"),
}


@dataclass
class PredictionResult:
    task: str
    algorithm: str
    target: str
    prediction: Any
    probabilities: Any | None
    scores: Any | None
    features: dict[str, Any]
    artifact_dir: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PredictionLayer:
    """Load trained artifacts and run current-state predictions."""

    def __init__(
        self,
        artifacts_dir: str | Path = ARTIFACTS_DIR,
        weather_timeout_seconds: int = 30,
    ) -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.weather_timeout_seconds = weather_timeout_seconds

    def predict_task(
        self,
        task: str,
        plant_data: dict[str, Any],
        sensor_data: dict[str, Any] | None = None,
        weather_data: dict[str, Any] | None = None,
        artifact_dir: str | Path | None = None,
        fetch_weather: bool = True,
    ) -> PredictionResult:
        """Predict one configured task from current plant/sensor/weather data."""

        task_name = normalize_task_name(task)
        resolved_artifact_dir = Path(artifact_dir) if artifact_dir else self.artifacts_dir / task_name / "best_model"
        bundle = self.load_artifact_bundle(resolved_artifact_dir)
        weather_record = self.resolve_weather_data(
            plant_data=plant_data,
            sensor_data=sensor_data,
            weather_data=weather_data,
            fetch_weather=fetch_weather,
        )
        features = build_prediction_features(
            plant_data=plant_data,
            sensor_data=sensor_data,
            weather_data=weather_record,
            expected_features=bundle["metadata"]["features"],
        )
        prediction_output = predict_with_confidence(
            bundle["model"],
            features,
            preprocessing_artifacts=bundle["preprocessing"],
            inverse_transform=True,
        )

        prediction = prediction_output["predictions"][0] if prediction_output.get("predictions") else None
        probabilities = first_or_none(prediction_output.get("probabilities"))
        scores = first_or_none(prediction_output.get("scores"))

        return PredictionResult(
            task=task_name,
            algorithm=bundle["metadata"].get("algorithm"),
            target=bundle["metadata"].get("target"),
            prediction=prediction,
            probabilities=probabilities,
            scores=scores,
            features=features.iloc[0].to_dict(),
            artifact_dir=str(resolved_artifact_dir),
        )

    def predict_all(
        self,
        plant_data: dict[str, Any],
        sensor_data: dict[str, Any] | None = None,
        weather_data: dict[str, Any] | None = None,
        fetch_weather: bool = True,
    ) -> dict[str, PredictionResult]:
        """Predict every supported task using the best saved model for each."""

        weather_record = self.resolve_weather_data(
            plant_data=plant_data,
            sensor_data=sensor_data,
            weather_data=weather_data,
            fetch_weather=fetch_weather,
        )
        return {
            task: self.predict_task(
                task,
                plant_data=plant_data,
                sensor_data=sensor_data,
                weather_data=weather_record,
                fetch_weather=False,
            )
            for task in SUPPORTED_TASKS
        }

    def load_artifact_bundle(self, artifact_dir: str | Path) -> dict[str, Any]:
        """Load model, preprocessing, and metadata artifacts."""

        directory = Path(artifact_dir)
        return {
            "model": load_model(directory / "model.pkl"),
            "preprocessing": load_preprocessing_artifacts(directory / "preprocessing.pkl"),
            "metadata": load_metadata(directory / "metadata.json"),
        }

    def resolve_weather_data(
        self,
        plant_data: dict[str, Any],
        sensor_data: dict[str, Any] | None = None,
        weather_data: dict[str, Any] | None = None,
        fetch_weather: bool = True,
    ) -> dict[str, Any]:
        """Use supplied weather data or fetch current Open-Meteo weather."""

        if weather_data:
            return parse_weather_data(weather_data)

        if not fetch_weather:
            return {}

        latitude = first_present(plant_data, sensor_data or {}, keys=("latitude", "lat"))
        longitude = first_present(plant_data, sensor_data or {}, keys=("longitude", "lon", "lng"))
        if latitude is None or longitude is None:
            return {}

        return fetch_current_weather(
            latitude=float(latitude),
            longitude=float(longitude),
            timeout_seconds=self.weather_timeout_seconds,
        )


def predict_task(
    task: str,
    plant_data: dict[str, Any],
    sensor_data: dict[str, Any] | None = None,
    weather_data: dict[str, Any] | None = None,
    fetch_weather: bool = True,
) -> dict[str, Any]:
    """Convenience function for one-task prediction."""

    return (
        PredictionLayer()
        .predict_task(
            task=task,
            plant_data=plant_data,
            sensor_data=sensor_data,
            weather_data=weather_data,
            fetch_weather=fetch_weather,
        )
        .to_dict()
    )


def predict_all_tasks(
    plant_data: dict[str, Any],
    sensor_data: dict[str, Any] | None = None,
    weather_data: dict[str, Any] | None = None,
    fetch_weather: bool = True,
) -> dict[str, dict[str, Any]]:
    """Convenience function for predicting every supported task."""

    results = PredictionLayer().predict_all(
        plant_data=plant_data,
        sensor_data=sensor_data,
        weather_data=weather_data,
        fetch_weather=fetch_weather,
    )
    return {task: result.to_dict() for task, result in results.items()}


def build_prediction_features(
    plant_data: dict[str, Any],
    sensor_data: dict[str, Any] | None,
    weather_data: dict[str, Any] | None,
    expected_features: list[str],
) -> pd.DataFrame:
    """Merge current inputs and engineer the features expected by a model."""

    record = {}
    for source in (plant_data or {}, sensor_data or {}, weather_data or {}):
        record.update(source)

    record = normalize_record(record)
    record = add_time_features(record)
    record = add_plant_age(record)
    record = add_season(record)
    record = add_weather_interaction_features(record)

    for feature in expected_features:
        record.setdefault(feature, None)

    return pd.DataFrame([{feature: record.get(feature) for feature in expected_features}])


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize common plant/sensor/weather aliases to training feature names."""

    normalized = dict(record)
    for canonical, aliases in CANONICAL_ALIASES.items():
        if canonical in normalized and normalized[canonical] is not None:
            continue

        for alias in aliases:
            if alias in normalized and normalized[alias] is not None:
                normalized[canonical] = normalized[alias]
                break

    for column in [
        "temperature",
        "humidity",
        "soil_moisture",
        "soil_ph",
        "rainfall",
        "rain_probability",
        "wind_speed",
        "latitude",
        "longitude",
        "current_height_cm",
        "plant_age_days",
        "watering_interval_days",
    ]:
        if column in normalized:
            normalized[column] = to_float(normalized[column])

    return normalized


def add_time_features(record: dict[str, Any]) -> dict[str, Any]:
    """Add time-derived features used by training datasets."""

    timestamp = parse_timestamp(record.get("timestamp")) or datetime.now()
    record["timestamp"] = timestamp.isoformat(sep=" ")
    record.setdefault("year", timestamp.year)
    record.setdefault("month", timestamp.month)
    record.setdefault("day", timestamp.day)
    record.setdefault("hour", timestamp.hour)
    record.setdefault("day_of_week", timestamp.weekday())
    record.setdefault("week_of_year", int(timestamp.strftime("%U")))
    return record


def add_plant_age(record: dict[str, Any]) -> dict[str, Any]:
    """Calculate plant_age_days from planting_date when needed."""

    if record.get("plant_age_days") is not None:
        return record

    planting_date = parse_timestamp(record.get("planting_date"))
    current_timestamp = parse_timestamp(record.get("timestamp")) or datetime.now()
    if planting_date is None:
        return record

    record["plant_age_days"] = max(0, (current_timestamp.date() - planting_date.date()).days)
    return record


def add_season(record: dict[str, Any]) -> dict[str, Any]:
    """Add agricultural season from country/latitude/month when missing."""

    if record.get("season"):
        return record

    month = int(record.get("month") or datetime.now().month)
    country = str(record.get("country") or "").strip().lower()

    if country in TROPICAL_COUNTRIES or -23.5 <= float(record.get("latitude") or 99) <= 23.5:
        record["season"] = "Wet" if month in {11, 12, 1, 2, 3, 4} else "Dry"
    elif month in {12, 1, 2}:
        record["season"] = "Winter"
    elif month in {3, 4, 5}:
        record["season"] = "Spring"
    elif month in {6, 7, 8}:
        record["season"] = "Summer"
    else:
        record["season"] = "Autumn"

    return record


def add_weather_interaction_features(record: dict[str, Any]) -> dict[str, Any]:
    """Add derived weather interaction features used during training."""

    temperature = to_float(record.get("temperature"))
    humidity = to_float(record.get("humidity"))
    soil_moisture = to_float(record.get("soil_moisture"))
    rainfall = to_float(record.get("rainfall")) or 0.0
    wind_speed = to_float(record.get("wind_speed")) or 0.0

    if temperature is not None and humidity is not None:
        record["heat_index"] = round(temperature + (0.1 * humidity), 2)

    if temperature is not None and humidity is not None and soil_moisture is not None:
        record["water_stress"] = calculate_water_stress(temperature, humidity, soil_moisture)
        record["dryness_index"] = calculate_dryness_index(temperature, humidity, soil_moisture, rainfall, wind_speed)
        record["evaporation_risk"] = calculate_evaporation_risk(temperature, humidity, soil_moisture, wind_speed)

    return record


def calculate_water_stress(temperature: float, humidity: float, soil_moisture: float) -> float:
    stress = 0.0
    stress += max(0, 35 - soil_moisture) * 1.7
    stress += max(0, temperature - 30) * 3.0
    stress += max(0, 50 - humidity) * 0.8
    return round(max(0, min(100, stress)), 2)


def calculate_dryness_index(
    temperature: float,
    humidity: float,
    soil_moisture: float,
    rainfall: float,
    wind_speed: float,
) -> float:
    dryness = 100 - soil_moisture
    dryness += max(0, temperature - 26) * 1.3
    dryness += wind_speed * 0.8
    dryness += max(0, 55 - humidity) * 0.5
    dryness -= rainfall * 2.0
    return round(max(0, min(100, dryness)), 2)


def calculate_evaporation_risk(
    temperature: float,
    humidity: float,
    soil_moisture: float,
    wind_speed: float,
) -> float:
    risk = ((temperature * 2) + (100 - humidity) + (100 - soil_moisture) + (wind_speed * 4)) / 4
    return round(max(0, min(100, risk)), 2)


def fetch_current_weather(
    latitude: float,
    longitude: float,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Fetch and parse current Open-Meteo weather for coordinates."""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,rain,precipitation,wind_speed_10m",
        "hourly": "precipitation_probability,soil_moisture_0_to_1cm",
        "forecast_days": 1,
        "timezone": "auto",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=timeout_seconds)
    response.raise_for_status()
    return parse_weather_data(response.json())


def parse_weather_data(weather_data: dict[str, Any]) -> dict[str, Any]:
    """Parse supplied weather records or Open-Meteo JSON into canonical fields."""

    if "current" not in weather_data:
        return normalize_record(weather_data)

    current = weather_data.get("current") or {}
    hourly = weather_data.get("hourly") or {}
    parsed = {
        "timestamp": current.get("time"),
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "rainfall": first_non_null(current.get("rain"), current.get("precipitation")),
        "wind_speed": current.get("wind_speed_10m"),
        "rain_probability": first_hourly_value(hourly, "precipitation_probability"),
        "soil_moisture": soil_moisture_to_percent(first_hourly_value(hourly, "soil_moisture_0_to_1cm")),
    }
    return normalize_record(parsed)


def normalize_task_name(task: str) -> str:
    """Normalize task aliases to artifact task names."""

    task_name = TASK_ALIASES.get(task, task)
    if task_name not in SUPPORTED_TASKS:
        raise ValueError(f"Unsupported prediction task: {task}")
    return task_name


def first_present(*records: dict[str, Any], keys: tuple[str, ...]):
    for record in records:
        for key in keys:
            if key in record and record[key] is not None:
                return record[key]
    return None


def first_non_null(*values):
    for value in values:
        if value is not None:
            return value
    return None


def first_hourly_value(hourly: dict[str, Any], key: str):
    values = hourly.get(key)
    if isinstance(values, list) and values:
        return values[0]
    return None


def soil_moisture_to_percent(value):
    if value is None:
        return None
    value = to_float(value)
    if value is None:
        return None
    return value * 100 if 0 <= value <= 1 else value


def parse_timestamp(value) -> datetime | None:
    if value in (None, ""):
        return None
    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        return None
    return timestamp.to_pydatetime()


def to_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def first_or_none(values):
    if values is None:
        return None
    if isinstance(values, list) and values:
        return values[0]
    return values


def main() -> None:
    """Small CLI smoke path using JSON strings from files is intentionally avoided."""

    example_plant = {
        "species_id": 3000,
        "scientific_name": "solanum lycopersicum",
        "life_cycle": "annual",
        "environment_type": "outdoor",
        "watering_interval_days": 2,
        "recommended_soil": "well-drained loam",
        "recommended_sunlight": "full sun",
        "pest_susceptibility": "aphid, whitefly, leaf spot",
        "plant_age_days": 45,
        "current_height_cm": 24.5,
        "latitude": -6.9175,
        "longitude": 107.6191,
    }
    example_sensor = {
        "temperature": 29.0,
        "humidity": 72.0,
        "soil_moisture": 38.0,
        "soil_ph": 6.7,
    }
    example_weather = {
        "rainfall": 1.2,
        "rain_probability": 45,
        "wind_speed": 4.5,
    }
    results = predict_all_tasks(example_plant, example_sensor, example_weather, fetch_weather=False)
    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    main()
