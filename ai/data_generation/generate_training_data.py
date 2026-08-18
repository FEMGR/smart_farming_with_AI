"""
Generate realistic mock raw data for the training pipeline.

This module intentionally stops at raw CSV generation. It writes only:

- ai/datasets/raw/plants.csv
- ai/datasets/raw/weather.csv
- ai/datasets/raw/sensor_readings.csv

Preprocessing, merging, feature engineering, and model-specific feature
selection are handled by ai/data_generation/generate_training_pipeline.py.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from ai.core.constants import (
    DATA_GEN_DEFAULT_DAYS as DEFAULT_DAYS,
    DATA_GEN_DEFAULT_INTERVAL_HOURS as DEFAULT_INTERVAL_HOURS,
    DATA_GEN_DEFAULT_START as DEFAULT_START,
    DATA_GEN_DEFAULT_TIMEZONE as DEFAULT_TIMEZONE,
    DATA_GEN_RANDOM_SEED as RANDOM_SEED,
    RAW_DATA_DIR,
    SPECIES_TEMPLATES,
)


def reset_random_seed(seed: int = RANDOM_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def timestamp_range(
    start: datetime = DEFAULT_START,
    days: int = DEFAULT_DAYS,
    interval_hours: int = DEFAULT_INTERVAL_HOURS,
) -> list[datetime]:
    end = start + timedelta(days=days)
    current = start
    timestamps = []

    while current < end:
        timestamps.append(current)
        current += timedelta(hours=interval_hours)

    return timestamps


def season_for_month(month: int) -> str:
    if month in {11, 12, 1, 2, 3, 4}:
        return "Wet"
    return "Dry"


def daylight_factor(hour: int) -> float:
    if hour < 6 or hour > 18:
        return 0.0

    return math.sin(math.pi * (hour - 6) / 12)


def generate_plants(num_plants: int = 20) -> pd.DataFrame:
    rows = []
    base_latitude = -6.9175
    base_longitude = 107.6191

    for index in range(num_plants):
        template = SPECIES_TEMPLATES[index % len(SPECIES_TEMPLATES)]
        plant_id = 1000 + index
        location_id = 2000 + index
        planting_age_days = random.randint(12, 80)
        height_cm = round(max(5.0, planting_age_days * template.base_growth_cm_per_day * random.uniform(0.75, 1.2)), 2)

        rows.append(
            {
                "user_id": random.randint(1, 4),
                "plant_id": plant_id,
                "location_id": location_id,
                "species_id": 3000 + (index % len(SPECIES_TEMPLATES)),
                "plant_name": template.plant_name,
                "scientific_name": template.scientific_name,
                "last_watered": (DEFAULT_START - timedelta(days=random.randint(0, 4))).date().isoformat(),
                "planting_date": (DEFAULT_START - timedelta(days=planting_age_days)).date().isoformat(),
                "watering_interval_days": template.watering_interval_days,
                "recommended_soil": template.recommended_soil,
                "life_cycle": template.life_cycle,
                "environment_type": template.environment_type,
                "latitude": round(base_latitude + random.uniform(-0.02, 0.02), 6),
                "longitude": round(base_longitude + random.uniform(-0.02, 0.02), 6),
                "plant_age_days": planting_age_days,
                "height_cm": height_cm,
                "growth_stage": growth_stage_for_age(planting_age_days),
                "propagation_method": template.propagation_method,
                "pest_susceptibility": template.pest_susceptibility,
                "recommended_sunlight": template.recommended_sunlight,
                "is_sensor_enabled": True,
            }
        )

    return pd.DataFrame(rows)


def growth_stage_for_age(age_days: int) -> str:
    if age_days < 20:
        return "Seedling"
    if age_days < 55:
        return "Vegetative"
    if age_days < 90:
        return "Flowering"
    if age_days < 130:
        return "Fruiting"
    return "Mature"


def simulate_weather_for_location(timestamp: datetime, latitude: float, longitude: float) -> dict:
    daylight = daylight_factor(timestamp.hour)
    seasonal_rain_bonus = 22 if season_for_month(timestamp.month) == "Wet" else -8
    daily_temperature = 24 + (7 * daylight) + random.uniform(-1.5, 1.5)
    humidity = max(45, min(98, 92 - (daily_temperature - 22) * 2.1 + random.uniform(-5, 5)))
    rain_probability = max(0, min(100, humidity - 58 + seasonal_rain_bonus + random.uniform(-12, 12)))
    rainfall = round(np.random.gamma(2.0, 2.0), 2) if random.random() < rain_probability / 100 else 0.0
    wind_speed = round(max(0.5, 4.0 + (2.5 * daylight) + random.uniform(-1.5, 2.0)), 2)
    soil_moisture = max(12, min(92, 55 + rainfall * 2.2 - daylight * 14 + random.uniform(-8, 8)))

    return {
        "date": timestamp.isoformat(sep=" "),
        "air_temp_c": round(daily_temperature, 2),
        "humidity_pct": round(humidity, 1),
        "rainfall_mm": rainfall,
        "precipitation_probability": round(rain_probability, 1),
        "wind_kmh": wind_speed,
        "soil_temp_c": round(daily_temperature - random.uniform(0.5, 2.0), 2),
        "soil_moisture_pct": round(soil_moisture, 2),
        "latitude": latitude,
        "longitude": longitude,
        "timezone": DEFAULT_TIMEZONE,
    }


def generate_weather(plants: pd.DataFrame, timestamps: list[datetime]) -> pd.DataFrame:
    rows = []

    for _, plant in plants.iterrows():
        for timestamp in timestamps:
            rows.append(
                simulate_weather_for_location(
                    timestamp,
                    plant["latitude"],
                    plant["longitude"],
                )
            )

    return pd.DataFrame(rows)


def heat_index(temperature: float, humidity: float) -> float:
    return temperature + (0.1 * humidity)


def water_stress(temperature: float, humidity: float, soil_moisture: float) -> float:
    stress = 0.0
    stress += max(0, 35 - soil_moisture) * 1.7
    stress += max(0, temperature - 30) * 3.0
    stress += max(0, 50 - humidity) * 0.8
    return round(max(0, min(100, stress)), 2)


def dryness_index(temperature: float, humidity: float, soil_moisture: float, rainfall: float, wind_speed: float) -> float:
    dryness = 100 - soil_moisture
    dryness += max(0, temperature - 26) * 1.3
    dryness += wind_speed * 0.8
    dryness += max(0, 55 - humidity) * 0.5
    dryness -= rainfall * 2.0
    return round(max(0, min(100, dryness)), 2)


def evaporation_risk(temperature: float, humidity: float, soil_moisture: float, wind_speed: float) -> float:
    risk = ((temperature * 2) + (100 - humidity) + (100 - soil_moisture) + (wind_speed * 4)) / 4
    return round(max(0, min(100, risk)), 2)


def watering_amount_liters(watering_needed: bool, dryness: float, plant_age_days: int) -> float:
    if not watering_needed:
        return 0.0

    age_factor = 0.8 if plant_age_days < 30 else 1.2 if plant_age_days < 90 else 1.6
    return round(max(0.25, (dryness / 35) * age_factor), 2)


def disease_label(disease_risk: float, humidity: float, soil_moisture: float) -> str:
    if disease_risk < 45:
        return "none"
    if humidity > 82 and soil_moisture > 65:
        return "fungal_leaf_spot"
    if soil_moisture > 75:
        return "root_rot"
    return "powdery_mildew"


def generate_sensor_readings(plants: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    rows = []
    plants_by_location = plants.set_index("location_id").to_dict(orient="index")
    location_by_coordinates = {(round(row.latitude, 6), round(row.longitude, 6)): row.location_id for row in plants.itertuples(index=False)}

    for weather_row in weather.itertuples(index=False):
        location_id = location_by_coordinates[(round(weather_row.latitude, 6), round(weather_row.longitude, 6))]
        plant = plants_by_location[location_id]
        template = next(item for item in SPECIES_TEMPLATES if item.scientific_name == plant["scientific_name"])

        timestamp = pd.Timestamp(weather_row.date)
        days_elapsed = max(0, (timestamp.to_pydatetime() - DEFAULT_START).days)
        current_age = int(plant["plant_age_days"] + days_elapsed)
        temperature = round(weather_row.air_temp_c + random.uniform(-0.4, 0.4), 2)
        humidity = round(max(0, min(100, weather_row.humidity_pct + random.uniform(-2.0, 2.0))), 1)
        soil_moisture = round(max(5, min(100, weather_row.soil_moisture_pct + random.uniform(-5, 4))), 2)
        soil_ph = round(random.uniform(6.0, 7.2), 2)
        light_lux = int(max(0, 100000 * daylight_factor(timestamp.hour) + random.uniform(-2500, 2500)))

        stress = water_stress(temperature, humidity, soil_moisture)
        dryness = dryness_index(temperature, humidity, soil_moisture, weather_row.rainfall_mm, weather_row.wind_kmh)
        needs_water = soil_moisture < 32 or stress > 62 or dryness > 68
        current_height = plant["height_cm"] + (days_elapsed * template.base_growth_cm_per_day * random.uniform(0.85, 1.15))
        growth_penalty = 1 - min(0.45, stress / 220)
        future_height = current_height + (7 * template.base_growth_cm_per_day * growth_penalty)
        disease_risk = round(max(0, min(100, (humidity - 55) * 0.8 + (soil_moisture - 50) * 0.5 + max(0, temperature - 29) * 2)), 2)
        yield_kg = round(max(0.05, template.base_yield_kg * growth_penalty * random.uniform(0.75, 1.25)), 2)

        rows.append(
            {
                "timestamp": timestamp.isoformat(sep=" "),
                "sensor_id": f"S{int(location_id):04d}",
                "location_id": int(location_id),
                "temperature_c": temperature,
                "humidity_pct": humidity,
                "soil_moisture_pct": soil_moisture,
                "ph": soil_ph,
                "light_lux": light_lux,
                "watering_amount_liters": watering_amount_liters(needs_water, dryness, current_age),
                "future_height_cm": round(future_height, 2),
                "growth_rate": round(template.base_growth_cm_per_day * growth_penalty, 3),
                "disease_name": disease_label(disease_risk, humidity, soil_moisture),
                "disease_risk": disease_risk,
                "yield_kg": yield_kg,
            }
        )

    return pd.DataFrame(rows)


def save_raw_dataset(df: pd.DataFrame, output_file: Path) -> None:
    ensure_output_dir(output_file.parent)
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df):,} rows to {output_file}")


def generate_all(
    num_plants: int = 20,
    days: int = DEFAULT_DAYS,
    interval_hours: int = DEFAULT_INTERVAL_HOURS,
    output_dir: Path | str = RAW_DATA_DIR,
) -> dict[str, pd.DataFrame]:
    """
    Generate all mock raw datasets used by the training pipeline.
    """

    reset_random_seed()
    output_dir = Path(output_dir)
    timestamps = timestamp_range(days=days, interval_hours=interval_hours)

    plants = generate_plants(num_plants=num_plants)
    weather = generate_weather(plants, timestamps)
    sensor_readings = generate_sensor_readings(plants, weather)

    save_raw_dataset(plants, output_dir / "plants.csv")
    save_raw_dataset(weather, output_dir / "weather.csv")
    save_raw_dataset(sensor_readings, output_dir / "sensor_readings.csv")

    return {
        "plants": plants,
        "weather": weather,
        "sensor": sensor_readings,
    }


def main() -> dict[str, pd.DataFrame]:
    return generate_all()


if __name__ == "__main__":
    main()
