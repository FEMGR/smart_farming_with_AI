"""
Centralized repository for all constants used across the AI components.
"""

# ai/core/constants.py

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# =============================================================================
# Path & Directory Anchors
# =============================================================================

AI_FOLDER = Path(__file__).resolve().parent.parent
PROJECT_ROOT = AI_FOLDER.parent

RAW_DATA_DIR = AI_FOLDER / "datasets" / "raw"
PROCESSED_DATA_DIR = AI_FOLDER / "datasets" / "processed"
ARTIFACTS_DIR = AI_FOLDER / "artifacts"
CONFIG_DIR = AI_FOLDER / "config"
MAPPING_DIR = CONFIG_DIR / "schema_mappings"
UNIT_FOLDER = CONFIG_DIR / "unit_mappings"

DATA_GENERATION_DIR = AI_FOLDER / "data_generation"
PREPROCESSING_DIR = AI_FOLDER / "preprocessing"

# =============================================================================
# Ingestion Constants
# =============================================================================

PLANT_COLUMNS = [
    "user_id",
    "plant_id",
    "location_id",
    "species_id",
    "plant_name",
    "scientific_name",
    "life_cycle",
    "environment_type",
    "watering_interval_days",
    "recommended_soil",
    "recommended_sunlight",
    "propagation_method",
    "pest_susceptibility",
    "latitude",
    "longitude",
    "city",
    "state",
    "country",
    "height_cm",
]

INTEGER_COLUMNS = [
    "user_id",
    "plant_id",
    "location_id",
    "species_id",
    "watering_interval_days",
]

FLOAT_COLUMNS = ["latitude", "longitude", "height_cm"]

DEFAULT_WEATHER_INPUT_FILE = RAW_DATA_DIR / "weather.json"
DEFAULT_WEATHER_OUTPUT_FILE = RAW_DATA_DIR / "weather.csv"

# =============================================================================
# Preprocessing Constants
# =============================================================================

CLEAN_DATA_OUTPUT_FOLDER = PROCESSED_DATA_DIR
CLEAN_DATA_OUTPUT_FILE = CLEAN_DATA_OUTPUT_FOLDER / "cleaned_sensor_readings.csv"

NON_IMPUTED_NUMERIC_COLUMNS = {
    "user_id",
    "plant_id",
    "species_id",
    "location_id",
    "group_id",
    "latitude",
    "longitude",
}

FEATURE_ENG_INPUT_FILE = PROCESSED_DATA_DIR / "merged_data.csv"
FEATURE_ENG_OUTPUT_FILE = PROCESSED_DATA_DIR / "featured_data.csv"

TROPICAL_COUNTRIES = {
    "indonesia",
    "malaysia",
    "singapore",
    "brunei",
    "philippines",
    "thailand",
    "vietnam",
    "cambodia",
    "laos",
    "myanmar",
    "timor-leste",
    "papua new guinea",
    "ecuador",
    "colombia",
    "brazil",
    "kenya",
    "uganda",
    "tanzania",
    "nigeria",
    "ghana",
    "costa rica",
}

UNKNOWN_TEXT_VALUES = {"", "nan", "none", "null", "unknown"}

COUNTRY_BOUNDING_BOXES = [
    {
        "country": "Indonesia",
        "latitude_min": -11.2,
        "latitude_max": 6.3,
        "longitude_min": 94.7,
        "longitude_max": 141.1,
    },
    {
        "country": "Malaysia",
        "latitude_min": 0.8,
        "latitude_max": 7.4,
        "longitude_min": 99.6,
        "longitude_max": 119.4,
    },
    {
        "country": "Singapore",
        "latitude_min": 1.1,
        "latitude_max": 1.5,
        "longitude_min": 103.6,
        "longitude_max": 104.1,
    },
    {
        "country": "Thailand",
        "latitude_min": 5.4,
        "latitude_max": 20.5,
        "longitude_min": 97.3,
        "longitude_max": 105.7,
    },
    {
        "country": "Philippines",
        "latitude_min": 4.5,
        "latitude_max": 21.3,
        "longitude_min": 116.0,
        "longitude_max": 127.0,
    },
]

CITY_REFERENCES = [
    {
        "city": "Bandung",
        "state": "West Java",
        "country": "Indonesia",
        "latitude": -6.9175,
        "longitude": 107.6191,
    },
    {
        "city": "Jakarta",
        "state": "Jakarta",
        "country": "Indonesia",
        "latitude": -6.2088,
        "longitude": 106.8456,
    },
    {
        "city": "Surabaya",
        "state": "East Java",
        "country": "Indonesia",
        "latitude": -7.2575,
        "longitude": 112.7521,
    },
    {
        "city": "Yogyakarta",
        "state": "Yogyakarta",
        "country": "Indonesia",
        "latitude": -7.7956,
        "longitude": 110.3695,
    },
    {
        "city": "Semarang",
        "state": "Central Java",
        "country": "Indonesia",
        "latitude": -6.9667,
        "longitude": 110.4167,
    },
    {
        "city": "Denpasar",
        "state": "Bali",
        "country": "Indonesia",
        "latitude": -8.6705,
        "longitude": 115.2126,
    },
    {
        "city": "Medan",
        "state": "North Sumatra",
        "country": "Indonesia",
        "latitude": 3.5952,
        "longitude": 98.6722,
    },
    {
        "city": "Makassar",
        "state": "South Sulawesi",
        "country": "Indonesia",
        "latitude": -5.1477,
        "longitude": 119.4327,
    },
    {
        "city": "Singapore",
        "state": "Singapore",
        "country": "Singapore",
        "latitude": 1.3521,
        "longitude": 103.8198,
    },
    {
        "city": "Kuala Lumpur",
        "state": "Kuala Lumpur",
        "country": "Malaysia",
        "latitude": 3.1390,
        "longitude": 101.6869,
    },
    {
        "city": "Bangkok",
        "state": "Bangkok",
        "country": "Thailand",
        "latitude": 13.7563,
        "longitude": 100.5018,
    },
    {
        "city": "Manila",
        "state": "Metro Manila",
        "country": "Philippines",
        "latitude": 14.5995,
        "longitude": 120.9842,
    },
]

MASTER_FEATURE_COLUMNS = [
    "dataset_source",
    "dataset_origin",
    "model_version",
    "timestamp",
    "user_id",
    "plant_id",
    "location_id",
    "sensor_id",
    "species_id",
    "plant_name",
    "scientific_name",
    "life_cycle",
    "environment_type",
    "watering_interval_days",
    "recommended_soil",
    "recommended_sunlight",
    "propagation_method",
    "pest_susceptibility",
    "growth_stage",
    "temperature",
    "humidity",
    "soil_moisture",
    "soil_ph",
    "soil_temp_c",
    "rainfall",
    "rain_probability",
    "wind_speed",
    "light_intensity",
    "latitude",
    "longitude",
    "country",
    "state",
    "city",
    "timezone",
    "year",
    "month",
    "day",
    "hour",
    "day_of_week",
    "week_of_year",
    "plant_age_days",
    "plant_age_group",
    "current_height_cm",
    "height_cm",
    "season",
    "hemisphere",
    "is_tropical_country",
    "temperature_f",
    "temperature_range",
    "hot_day",
    "cold_day",
    "optimal_temperature",
    "humidity_level",
    "high_humidity",
    "low_humidity",
    "optimal_humidity",
    "soil_status",
    "dry_soil",
    "wet_soil",
    "optimal_soil",
    "growth_progress",
    "days_since_watered",
    "watering_due",
    "irrigation_score",
    "irrigation_needed",
    "irrigation_priority",
    "watering_needed",
    "watering_amount_liters",
    "water_stress",
    "dryness_index",
    "heat_index",
    "evaporation_risk",
    "good_growing_conditions",
    "future_height_cm",
    "growth_rate",
    "disease_name",
    "disease_risk",
]

FEATURE_SEL_INPUT_FILE = PROCESSED_DATA_DIR / "featured_data.csv"

DATABASE_IDENTIFIER_COLUMNS = {
    "plant_id",
    "location_id",
    "user_id",
    "sensor_id",
}

MODEL_TRACE_COLUMNS = {
    "timestamp",
    "dataset_source",
    "dataset_origin",
    "data_source",
    "source_name",
    "model_version",
}

NON_MODEL_FEATURE_COLUMNS = DATABASE_IDENTIFIER_COLUMNS | MODEL_TRACE_COLUMNS

TRAINING_DATASETS = {
    "irrigation": {
        "output_file": PROCESSED_DATA_DIR / "irrigation_training.csv",
        "features": [
            "species_id",
            "scientific_name",
            "life_cycle",
            "environment_type",
            "watering_interval_days",
            "recommended_soil",
            "recommended_sunlight",
            "temperature",
            "humidity",
            "soil_moisture",
            "soil_ph",
            "rainfall",
            "rain_probability",
            "wind_speed",
            "season",
            "month",
            "hour",
            "plant_age_days",
            "latitude",
            "longitude",
            "heat_index",
            "water_stress",
            "dryness_index",
            "evaporation_risk",
        ],
        "target_candidates": [
            "watering_needed",
            "watering_amount_liters",
        ],
    },
    "growth": {
        "output_file": PROCESSED_DATA_DIR / "growth_training.csv",
        "features": [
            "species_id",
            "scientific_name",
            "life_cycle",
            "recommended_soil",
            "recommended_sunlight",
            "plant_age_days",
            "current_height_cm",
            "temperature",
            "humidity",
            "soil_moisture",
            "rainfall",
            "season",
        ],
        "target_candidates": [
            "future_height_cm",
            "growth_rate",
        ],
    },
    "disease": {
        "output_file": PROCESSED_DATA_DIR / "disease_training.csv",
        "features": [
            "species_id",
            "scientific_name",
            "life_cycle",
            "pest_susceptibility",
            "temperature",
            "humidity",
            "soil_moisture",
            "soil_ph",
            "rainfall",
            "wind_speed",
            "heat_index",
            "water_stress",
            "dryness_index",
            "evaporation_risk",
        ],
        "target_candidates": [
            "disease_name",
            "disease_risk",
        ],
    },
    "yield": {
        "output_file": PROCESSED_DATA_DIR / "yield_training.csv",
        "features": [
            "species_id",
            "scientific_name",
            "life_cycle",
            "plant_age_days",
            "current_height_cm",
            "temperature",
            "humidity",
            "soil_moisture",
            "rainfall",
            "season",
            "watering_interval_days",
        ],
        "target_candidates": [
            "yield_kg",
        ],
    },
}

DATASET_NAME_ALIASES = {
    "sensor_readings": "sensor",
}

MERGE_DATA_OUTPUT_FOLDER = PROCESSED_DATA_DIR
MERGE_DATA_OUTPUT_FILE = MERGE_DATA_OUTPUT_FOLDER / "merged_data.csv"

CANONICAL_DUPLICATE_COLUMNS = {
    "temperature": ["temperature_x", "temperature_y"],
    "humidity": ["humidity_x", "humidity_y"],
    "soil_moisture": ["soil_moisture_x", "soil_moisture_y"],
    "latitude": ["latitude_x", "latitude_y"],
    "longitude": ["longitude_x", "longitude_y"],
    "year": ["year_x", "year_y"],
    "month": ["month_x", "month_y"],
    "day": ["day_x", "day_y"],
    "hour": ["hour_x", "hour_y"],
    "weekday": ["weekday_x", "weekday_y"],
    "rainfall": ["rainfall_x", "rainfall_y"],
    "rain_probability": ["rain_probability_x", "rain_probability_y"],
    "wind_speed": ["wind_speed_x", "wind_speed_y"],
}

CANONICAL_COLUMNS = {
    "timestamp": [
        "timestamp",
        "datetime",
        "date_time",
        "date",
        "time",
        "recorded_at",
        "created_at",
    ],
    "sensor_id": ["id", "sensor", "sensor_id", "device_id"],
    "plant_id": ["plant_id", "plant id"],
    "species_id": ["species_id", "species id"],
    "plant_name": [
        "plant_name",
        "plant name",
        "plant",
        "crop_name",
        "crop name",
        "crop_id",
        "crop id",
        "crop",
    ],
    "scientific_name": [
        "scientific_name",
        "scientific name",
        "botanical_name",
        "botanical name",
        "latin_name",
        "latin name",
    ],
    "life_cycle": ["life_cycle", "life cycle", "lifecycle"],
    "growth_stage": [
        "growth_stage",
        "growth stage",
        "seedling_stage",
        "seedling stage",
        "stage",
    ],
    "recommended_soil": [
        "recommended_soil",
        "recommended soil",
        "soil_type",
        "soil type",
        "soil",
    ],
    "recommended_sunlight": [
        "recommended_sunlight",
        "recommended sunlight",
        "sunlight",
        "sun_exposure",
        "sun exposure",
    ],
    "group_id": ["group", "group_id", "bed_id", "zone_id"],
    "location_id": ["location", "location_id", "field_id"],
    "latitude": ["latitude", "lat"],
    "longitude": ["longitude", "lon", "lng"],
    "country": ["country"],
    "city": ["city", "town"],
    "temperature": [
        "temperature",
        "temp",
        "temp_c",
        "temperature_c",
        "air_temperature",
    ],
    "humidity": ["humidity", "humidity_pct", "relative_humidity", "rh"],
    "rainfall": ["rain", "rainfall", "precipitation"],
    "rain_probability": ["rain_probability", "pop", "precip_probability"],
    "wind_speed": ["wind", "wind_speed"],
    "soil_moisture": [
        "soil_moisture",
        "soil_moisture_pct",
        "soil_water",
        "soil_water_pct",
        "moisture",
        "moi",
    ],
    "soil_ph": ["ph", "soil_ph"],
    "light": ["light", "light_lux", "sunlight", "lux", "illumination"],
    "watering_needed": [
        "watering_needed",
        "watering needed",
        "irrigation_needed",
        "irrigation needed",
        "needs_water",
        "needs water",
        "result",
    ],
    "watering_amount_liters": [
        "watering_amount_liters",
        "watering amount liters",
        "water_amount",
        "water amount",
        "irrigation_amount",
        "irrigation amount",
    ],
}

AUTO_ACCEPT_THRESHOLD = 95
REVIEW_THRESHOLD = 80


# Unit conversion helper functions
def fahrenheit_to_celsius(series):
    return (series - 32) * 5 / 9


def kelvin_to_celsius(series):
    return series - 273.15


def inch_to_mm(series):
    return series * 25.4


def cm_to_mm(series):
    return series * 10


def mph_to_ms(series):
    return series * 0.44704


def kmh_to_ms(series):
    return series / 3.6


def pa_to_hpa(series):
    return series / 100


def atm_to_hpa(series):
    return series * 1013.25


def feet_to_meter(series):
    return series * 0.3048


UNIT_CONVERSIONS = {
    "temperature": {
        "C": lambda x: x,
        "F": fahrenheit_to_celsius,
        "K": kelvin_to_celsius,
    },
    "rainfall": {
        "mm": lambda x: x,
        "cm": cm_to_mm,
        "inch": inch_to_mm,
    },
    "wind_speed": {
        "m/s": lambda x: x,
        "km/h": kmh_to_ms,
        "mph": mph_to_ms,
    },
    "pressure": {
        "hPa": lambda x: x,
        "Pa": pa_to_hpa,
        "atm": atm_to_hpa,
    },
    "distance": {
        "m": lambda x: x,
        "ft": feet_to_meter,
    },
    "soil_moisture": {
        "%": lambda x: x,
    },
}

# =============================================================================
# Model Default Parameters
# =============================================================================

DEFAULT_GB_CLASSIFIER_PARAMS = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "max_depth": 3,
    "random_state": 42,
}

DEFAULT_GB_REGRESSOR_PARAMS = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "max_depth": 3,
    "random_state": 42,
}

DEFAULT_RF_CLASSIFIER_PARAMS = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "random_state": 42,
    "n_jobs": -1,
    "class_weight": "balanced",
}

DEFAULT_RF_REGRESSOR_PARAMS = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "random_state": 42,
    "n_jobs": -1,
}

DEFAULT_XGB_CLASSIFIER_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "n_jobs": -1,
}

DEFAULT_XGB_REGRESSOR_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
    "objective": "reg:squarederror",
    "n_jobs": -1,
}

# =============================================================================
# Data Generation Constants
# =============================================================================

PLANTS_FILE = RAW_DATA_DIR / "plants.csv"
WEATHER_FILE = RAW_DATA_DIR / "weather.csv"
SENSOR_FILE = RAW_DATA_DIR / "sensor_readings.csv"

DATA_GEN_RANDOM_SEED = 42
DATA_GEN_DEFAULT_START = datetime(2026, 1, 1, 0, 0, 0)
DATA_GEN_DEFAULT_DAYS = 45
DATA_GEN_DEFAULT_INTERVAL_HOURS = 3
DATA_GEN_DEFAULT_TIMEZONE = "Asia/Jakarta"


@dataclass(frozen=True)
class SpeciesTemplate:
    plant_name: str
    scientific_name: str
    life_cycle: str
    environment_type: str
    watering_interval_days: int
    recommended_soil: str
    recommended_sunlight: str
    propagation_method: str
    pest_susceptibility: str
    base_growth_cm_per_day: float
    base_yield_kg: float


SPECIES_TEMPLATES = [
    SpeciesTemplate(
        "tomato",
        "Solanum lycopersicum",
        "Annual",
        "outdoor",
        2,
        "Well-drained loam",
        "full sun",
        "Seed Propagation",
        "aphid, whitefly, leaf spot",
        0.42,
        3.8,
    ),
    SpeciesTemplate(
        "cabbage",
        "Brassica oleracea var. capitata",
        "Annual",
        "outdoor",
        3,
        "Fertile well-drained soil",
        "full sun",
        "Seed Propagation",
        "cabbage worm, aphid, flea beetle",
        0.28,
        2.4,
    ),
    SpeciesTemplate(
        "lettuce",
        "Lactuca sativa",
        "Annual",
        "outdoor",
        2,
        "Moist well-drained soil",
        "partial shade",
        "Seed Propagation",
        "aphid, downy mildew",
        0.24,
        0.7,
    ),
    SpeciesTemplate(
        "chili pepper",
        "Capsicum annuum",
        "Perennial",
        "outdoor",
        3,
        "Sandy loam",
        "full sun",
        "Seed Propagation",
        "thrips, mite, anthracnose",
        0.31,
        1.6,
    ),
    SpeciesTemplate(
        "basil",
        "Ocimum basilicum",
        "Annual",
        "outdoor",
        2,
        "Rich well-drained soil",
        "full sun",
        "Seed Propagation, Cutting",
        "aphid, fungal leaf spot",
        0.35,
        0.5,
    ),
]

# =============================================================================
# Task Configurations
# =============================================================================

# Irrigation Prediction Task
IRRIGATION_TASK_NAME = "irrigation_prediction"
IRRIGATION_TASK_LABEL = "Irrigation Prediction"
IRRIGATION_TASK_FOLDER = AI_FOLDER / "tasks" / "irrigation_prediction"
IRRIGATION_DATASET_PATH = PROCESSED_DATA_DIR / "irrigation_training.csv"
IRRIGATION_ARTIFACT_DIR = ARTIFACTS_DIR / IRRIGATION_TASK_NAME
IRRIGATION_TARGET_COLUMN = "watering_needed"
IRRIGATION_TARGET_CANDIDATES = ("watering_needed", "watering_amount_liters")
IRRIGATION_PROBLEM_TYPE = "classification"
IRRIGATION_TEST_SIZE = 0.20
IRRIGATION_RANDOM_STATE = 42
IRRIGATION_MODELS = {
    "random_forest": {
        "algorithm": "Random Forest",
        "primary_metric": "f1",
        "greater_is_better": True,
        "params": {},
    },
    "xgboost": {
        "algorithm": "XGBoost",
        "primary_metric": "f1",
        "greater_is_better": True,
        "params": {},
    },
    "pytorch_mlp": {
        "algorithm": "PyTorch MLP",
        "primary_metric": "f1",
        "greater_is_better": True,
        "enabled": True,
        "params": {
            "epochs": 50,
            "batch_size": 128,
            "learning_rate": 0.001,
            "hidden_layers": (64, 32),
            "dropout": 0.10,
            "random_state": 42,
        },
    },
}
IRRIGATION_MODEL_ORDER = ("random_forest", "xgboost", "pytorch_mlp")

# Growth Prediction Task
GROWTH_TASK_NAME = "growth_prediction"
GROWTH_TASK_LABEL = "Growth Prediction"
GROWTH_TASK_FOLDER = AI_FOLDER / "tasks" / "growth_prediction"
GROWTH_DATASET_PATH = PROCESSED_DATA_DIR / "growth_training.csv"
GROWTH_ARTIFACT_DIR = ARTIFACTS_DIR / GROWTH_TASK_NAME
GROWTH_TARGET_COLUMN = "future_height_cm"
GROWTH_TARGET_CANDIDATES = ("future_height_cm", "growth_rate")
GROWTH_PROBLEM_TYPE = "regression"
GROWTH_TEST_SIZE = 0.20
GROWTH_RANDOM_STATE = 42
GROWTH_MODELS = {
    "random_forest": {
        "algorithm": "Random Forest",
        "primary_metric": "rmse",
        "greater_is_better": False,
        "enabled": True,
        "params": {},
    },
    "pytorch_mlp": {
        "algorithm": "PyTorch MLP",
        "primary_metric": "rmse",
        "greater_is_better": False,
        "enabled": True,
        "params": {
            "epochs": 80,
            "batch_size": 128,
            "learning_rate": 0.001,
            "hidden_layers": (64, 32),
            "dropout": 0.10,
            "random_state": 42,
        },
    },
}
GROWTH_MODEL_ORDER = ("random_forest", "pytorch_mlp")

# Disease Prediction Task
DISEASE_TASK_NAME = "disease_prediction"
DISEASE_TASK_LABEL = "Disease Prediction"
DISEASE_TASK_FOLDER = AI_FOLDER / "tasks" / "disease_prediction"
DISEASE_DATASET_PATH = PROCESSED_DATA_DIR / "disease_training.csv"
DISEASE_ARTIFACT_DIR = ARTIFACTS_DIR / DISEASE_TASK_NAME
DISEASE_TARGET_COLUMN = "disease_name"
DISEASE_TARGET_CANDIDATES = ("disease_name", "disease_risk")
DISEASE_PROBLEM_TYPE = "classification"
DISEASE_TEST_SIZE = 0.20
DISEASE_RANDOM_STATE = 42
DISEASE_MODELS = {
    "xgboost": {
        "algorithm": "XGBoost",
        "primary_metric": "f1",
        "greater_is_better": True,
        "enabled": True,
        "params": {},
    },
    "pytorch_mlp": {
        "algorithm": "PyTorch MLP",
        "primary_metric": "f1",
        "greater_is_better": True,
        "enabled": True,
        "params": {
            "epochs": 50,
            "batch_size": 128,
            "learning_rate": 0.001,
            "hidden_layers": (64, 32),
            "dropout": 0.10,
            "random_state": 42,
        },
    },
}
DISEASE_MODEL_ORDER = ("xgboost", "pytorch_mlp")

# Yield Prediction Task
YIELD_TASK_NAME = "yield_prediction"
YIELD_TASK_LABEL = "Yield Prediction"
YIELD_TASK_FOLDER = AI_FOLDER / "tasks" / "yield_prediction"
YIELD_DATASET_PATH = PROCESSED_DATA_DIR / "yield_training.csv"
YIELD_ARTIFACT_DIR = ARTIFACTS_DIR / YIELD_TASK_NAME
YIELD_TARGET_COLUMN = "yield_kg"
YIELD_TARGET_CANDIDATES = ("yield_kg",)
YIELD_PROBLEM_TYPE = "regression"
YIELD_TEST_SIZE = 0.20
YIELD_RANDOM_STATE = 42
YIELD_MODELS = {
    "gradient_boosting": {
        "algorithm": "Gradient Boosting",
        "primary_metric": "rmse",
        "greater_is_better": False,
        "enabled": True,
        "params": {},
    },
    "pytorch_mlp": {
        "algorithm": "PyTorch MLP",
        "primary_metric": "rmse",
        "greater_is_better": False,
        "enabled": True,
        "params": {
            "epochs": 80,
            "batch_size": 128,
            "learning_rate": 0.001,
            "hidden_layers": (64, 32),
            "dropout": 0.10,
            "random_state": 42,
        },
    },
}
YIELD_MODEL_ORDER = ("gradient_boosting", "pytorch_mlp")
