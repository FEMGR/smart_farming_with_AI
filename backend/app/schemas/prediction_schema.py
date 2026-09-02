# app/schemas/prediction_schema.py

from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field


class PlantDataPayload(BaseModel):
    species_id: Optional[int] = Field(3000, example=3000)
    scientific_name: Optional[str] = Field("solanum lycopersicum", example="solanum lycopersicum")
    life_cycle: Optional[str] = Field("annual", example="annual")
    environment_type: Optional[str] = Field("outdoor", example="outdoor")
    watering_interval_days: Optional[float] = Field(2.0, example=2.0)
    recommended_soil: Optional[str] = Field("well-drained loam", example="well-drained loam")
    recommended_sunlight: Optional[str] = Field("full sun", example="full sun")
    pest_susceptibility: Optional[str] = Field("aphid, whitefly, leaf spot", example="aphid, whitefly, leaf spot")
    plant_age_days: Optional[float] = Field(45.0, example=45.0)
    current_height_cm: Optional[float] = Field(24.5, example=24.5)
    latitude: Optional[float] = Field(-6.9175, example=-6.9175)
    longitude: Optional[float] = Field(107.6191, example=107.6191)


class SensorDataPayload(BaseModel):
    temperature: Optional[float] = Field(29.0, example=29.0)
    humidity: Optional[float] = Field(72.0, example=72.0)
    soil_moisture: Optional[float] = Field(38.0, example=38.0)
    soil_ph: Optional[float] = Field(6.7, example=6.7)


class WeatherDataPayload(BaseModel):
    rainfall: Optional[float] = Field(1.2, example=1.2)
    rain_probability: Optional[float] = Field(45.0, example=45.0)
    wind_speed: Optional[float] = Field(4.5, example=4.5)


class SinglePredictionRequest(BaseModel):
    # Enforces allowed dropdown choices in Swagger UI
    task: Literal["irrigation", "disease", "growth", "yield"] = Field(
        "irrigation",
        example="irrigation",
        description="Task domain to run prediction for",
    )
    plant_data: PlantDataPayload
    sensor_data: Optional[SensorDataPayload] = Field(default_factory=SensorDataPayload)
    weather_data: Optional[WeatherDataPayload] = Field(default_factory=WeatherDataPayload)
    fetch_weather: bool = Field(False, example=False)


class AllPredictionsRequest(BaseModel):
    plant_data: PlantDataPayload
    sensor_data: Optional[SensorDataPayload] = Field(default_factory=SensorDataPayload)
    weather_data: Optional[WeatherDataPayload] = Field(default_factory=WeatherDataPayload)
    fetch_weather: bool = Field(False, example=False)


class PredictionResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]
