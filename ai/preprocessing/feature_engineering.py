"""
Purpose
-------
Create new machine learning features from the cleaned and merged dataset.
The goal is to create additional useful information
that helps machine learning models make better predictions.
"""

# ai/prepocessing/feature_engineering.py

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# feature_engineering.py
#        │
# preprocessing/
#        │
from ai.core.constants import (
    CITY_REFERENCES,
    COUNTRY_BOUNDING_BOXES,
    FEATURE_ENG_INPUT_FILE as INPUT_FILE,
    FEATURE_ENG_OUTPUT_FILE as OUTPUT_FILE,
    MASTER_FEATURE_COLUMNS,
    TROPICAL_COUNTRIES,
    UNKNOWN_TEXT_VALUES,
)


# ==========================================================
# Project Paths
# ==========================================================

# ==========================================================
# Helper Functions
# ==========================================================


def safe_lower(value) -> str:
    """
    Convert any value to lowercase text safely.
    Returns empty string for missing values.
    """

    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def is_unknown_text(value) -> bool:
    return safe_lower(value) in UNKNOWN_TEXT_VALUES


def haversine_distance_km(latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float) -> float:
    """
    Calculate distance between two GPS points.
    """

    earth_radius_km = 6371.0
    lat_a = np.radians(latitude_a)
    lon_a = np.radians(longitude_a)
    lat_b = np.radians(latitude_b)
    lon_b = np.radians(longitude_b)

    delta_lat = lat_b - lat_a
    delta_lon = lon_b - lon_a

    haversine = np.sin(delta_lat / 2) ** 2 + np.cos(lat_a) * np.cos(lat_b) * np.sin(delta_lon / 2) ** 2

    return float(earth_radius_km * 2 * np.arcsin(np.sqrt(haversine)))


def infer_country_from_coordinates(latitude: float, longitude: float) -> str:
    for country in COUNTRY_BOUNDING_BOXES:
        if country["latitude_min"] <= latitude <= country["latitude_max"] and country["longitude_min"] <= longitude <= country["longitude_max"]:
            return country["country"]

    return "Unknown"


def infer_country_from_timezone(timezone: str) -> str:
    timezone = safe_lower(timezone)

    timezone_country = {
        "asia/jakarta": "Indonesia",
        "asia/makassar": "Indonesia",
        "asia/jayapura": "Indonesia",
        "asia/kuala_lumpur": "Malaysia",
        "asia/singapore": "Singapore",
        "asia/bangkok": "Thailand",
        "asia/manila": "Philippines",
    }

    return timezone_country.get(timezone, "Unknown")


def infer_city_from_coordinates(latitude: float, longitude: float, max_distance_km: float = 80.0) -> dict[str, str]:
    nearest_city = None
    nearest_distance = None

    for city in CITY_REFERENCES:
        distance = haversine_distance_km(
            latitude,
            longitude,
            city["latitude"],
            city["longitude"],
        )

        if nearest_distance is None or distance < nearest_distance:
            nearest_city = city
            nearest_distance = distance

    if nearest_city is None or nearest_distance is None or nearest_distance > max_distance_km:
        return {
            "city": "Unknown",
            "state": "Unknown",
            "country": "Unknown",
        }

    return {
        "city": nearest_city["city"],
        "state": nearest_city["state"],
        "country": nearest_city["country"],
    }


def fill_unknown_values(df: pd.DataFrame, column: str, values: pd.Series) -> pd.DataFrame:
    if column not in df.columns:
        df[column] = values
        return df

    unknown_mask = df[column].apply(is_unknown_text)
    df.loc[unknown_mask, column] = values.loc[unknown_mask]

    return df


def add_inferred_location_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Infer country, state, and city from latitude/longitude when possible.
    """

    if not {"latitude", "longitude"}.issubset(df.columns):
        return df

    coordinates = df[["latitude", "longitude"]].apply(pd.to_numeric, errors="coerce")
    inferred_records = []

    for index, row in coordinates.iterrows():
        latitude = row["latitude"]
        longitude = row["longitude"]

        if pd.isna(latitude) or pd.isna(longitude):
            inferred_records.append({"city": "Unknown", "state": "Unknown", "country": "Unknown"})
            continue

        inferred = infer_city_from_coordinates(latitude, longitude)

        if is_unknown_text(inferred["country"]):
            inferred["country"] = infer_country_from_coordinates(latitude, longitude)

        if is_unknown_text(inferred["country"]) and "timezone" in df.columns:
            inferred["country"] = infer_country_from_timezone(df.loc[index, "timezone"])

        inferred_records.append(inferred)

    inferred_df = pd.DataFrame(inferred_records, index=df.index)

    for column in ["country", "state", "city"]:
        df = fill_unknown_values(df, column, inferred_df[column])

    return df


def add_derived_plant_age(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate plant_age_days from planting_date and timestamp/current date.
    """

    if "planting_date" not in df.columns:
        return df

    planting_date = pd.to_datetime(df["planting_date"], errors="coerce")

    if "timestamp" in df.columns:
        reference_date = pd.to_datetime(df["timestamp"], errors="coerce")
    else:
        reference_date = pd.Series(pd.Timestamp.today().normalize(), index=df.index)

    plant_age_days = (reference_date.dt.normalize() - planting_date.dt.normalize()).dt.days
    plant_age_days = plant_age_days.clip(lower=0)

    if "plant_age_days" not in df.columns:
        df["plant_age_days"] = plant_age_days
    else:
        existing_age = pd.to_numeric(df["plant_age_days"], errors="coerce")
        df["plant_age_days"] = existing_age.fillna(plant_age_days)

    return df


# ==========================================================
# Hemisphere Detection
# ==========================================================


def detect_hemisphere(latitude: Optional[float]) -> str:
    """
    Detect hemisphere from latitude.

    Parameters
    ----------
    latitude : float

    Returns
    -------
    str

    Northern
    Southern
    Equator
    Unknown
    """

    if latitude is None or pd.isna(latitude):
        return "Unknown"

    if latitude > 1:
        return "Northern"

    if latitude < -1:
        return "Southern"

    return "Equator"


# ==========================================================
# Season Detection
# ==========================================================


def determine_season(row: pd.Series) -> str:
    """
    Determine agricultural season.

    Priority

    1. GPS latitude
    2. Country
    3. Default northern hemisphere

    Tropical countries use Wet/Dry season.

    Others use Spring/Summer/Autumn/Winter.
    """

    month = row["month"]

    latitude = row.get("latitude", np.nan)

    country = safe_lower(row.get("country", ""))

    hemisphere = detect_hemisphere(latitude)

    # ------------------------------------------------------
    # Tropical countries
    # ------------------------------------------------------

    if country in TROPICAL_COUNTRIES:

        # Simple tropical approximation
        # Wet : November -> April
        # Dry : May -> October

        if month in [11, 12, 1, 2, 3, 4]:
            return "Wet"

        return "Dry"

    # ------------------------------------------------------
    # Northern Hemisphere
    # ------------------------------------------------------

    if hemisphere == "Northern":

        if month in [12, 1, 2]:
            return "Winter"

        if month in [3, 4, 5]:
            return "Spring"

        if month in [6, 7, 8]:
            return "Summer"

        return "Autumn"

    # ------------------------------------------------------
    # Southern Hemisphere
    # ------------------------------------------------------

    if hemisphere == "Southern":

        if month in [12, 1, 2]:
            return "Summer"

        if month in [3, 4, 5]:
            return "Autumn"

        if month in [6, 7, 8]:
            return "Winter"

        return "Spring"

    # ------------------------------------------------------
    # Unknown latitude
    # ------------------------------------------------------

    if month in [12, 1, 2]:
        return "Winter"

    if month in [3, 4, 5]:
        return "Spring"

    if month in [6, 7, 8]:
        return "Summer"

    return "Autumn"


# ==========================================================
# Time Features
# ==========================================================


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create useful time-based features.
    """

    print("Adding time features...")

    if "timestamp" not in df.columns:
        raise ValueError("Dataset must contain a 'timestamp' column.")

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["year"] = df["timestamp"].dt.year

    df["month"] = df["timestamp"].dt.month

    df["day"] = df["timestamp"].dt.day

    df["hour"] = df["timestamp"].dt.hour

    df["day_of_week"] = df["timestamp"].dt.dayofweek

    df["week_of_year"] = df["timestamp"].dt.isocalendar().week.astype(int)

    df["quarter"] = df["timestamp"].dt.quarter

    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    df["season"] = df.apply(determine_season, axis=1)

    return df


# ==========================================================
# Location Features
# ==========================================================


def add_location_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create location-related features.

    Supports

    GPS
    Country
    State
    City
    """

    print("Adding location features...")

    # Hemisphere

    if "latitude" in df.columns:

        df["hemisphere"] = df["latitude"].apply(detect_hemisphere)

    else:

        df["hemisphere"] = "Unknown"

    # Country available

    if "country" in df.columns:

        df["is_tropical_country"] = df["country"].fillna("").str.lower().isin(TROPICAL_COUNTRIES).astype(int)

    else:

        df["is_tropical_country"] = 0

    # Missing location information

    for column in ["country", "state", "city"]:

        if column not in df.columns:

            df[column] = "Unknown"

        df[column] = df[column].fillna("Unknown").astype(str)

    return df


# ==========================================================
# Temperature Features
# ==========================================================


def add_temperature_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create temperature-related features.

    Expected column:
        temperature

    New features:
        temperature_f
        temperature_range
        hot_day
        cold_day
        optimal_temperature
    """

    print("Adding temperature features...")

    if "temperature" not in df.columns:
        print("Temperature column not found. Skipping...")
        return df

    # Celsius → Fahrenheit
    df["temperature_f"] = df["temperature"] * 9 / 5 + 32

    # Difference from ideal growing temperature
    # (25°C chosen as a general reference)
    df["temperature_range"] = df["temperature"] - 25

    # Simple indicators

    df["hot_day"] = (df["temperature"] >= 30).astype(int)

    df["cold_day"] = (df["temperature"] <= 15).astype(int)

    # Ideal range for many crops
    df["optimal_temperature"] = (df["temperature"].between(20, 30)).astype(int)

    return df


# ==========================================================
# Humidity Features
# ==========================================================


def add_humidity_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create humidity-related features.

    Expected column:
        humidity

    New features:
        humidity_level
        high_humidity
        low_humidity
        optimal_humidity
    """

    print("Adding humidity features...")

    if "humidity" not in df.columns:
        print("Humidity column not found. Skipping...")
        return df

    # Categorize humidity

    conditions = [
        df["humidity"] < 40,
        df["humidity"].between(40, 70),
        df["humidity"] > 70,
    ]

    labels = [
        "Low",
        "Normal",
        "High",
    ]

    df["humidity_level"] = np.select(
        conditions,
        labels,
        default="Unknown",
    )

    df["high_humidity"] = (df["humidity"] > 80).astype(int)

    df["low_humidity"] = (df["humidity"] < 35).astype(int)

    df["optimal_humidity"] = (df["humidity"].between(50, 70)).astype(int)

    return df


# ==========================================================
# Soil Features
# ==========================================================


def add_soil_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create soil-related features.

    Expected column:
        soil_moisture

    New features:
        soil_status
        dry_soil
        wet_soil
        optimal_soil
    """

    print("Adding soil features...")

    if "soil_moisture" not in df.columns:
        print("Soil moisture column not found. Skipping...")
        return df

    conditions = [
        df["soil_moisture"] < 30,
        df["soil_moisture"].between(30, 70),
        df["soil_moisture"] > 70,
    ]

    labels = [
        "Dry",
        "Optimal",
        "Wet",
    ]

    df["soil_status"] = np.select(
        conditions,
        labels,
        default="Unknown",
    )

    df["dry_soil"] = (df["soil_moisture"] < 30).astype(int)

    df["wet_soil"] = (df["soil_moisture"] > 70).astype(int)

    df["optimal_soil"] = (df["soil_moisture"].between(30, 70)).astype(int)

    return df


# ==========================================================
# Weather Interaction Features
# ==========================================================


def add_weather_interaction_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create interaction features between weather variables.

    These often help ML models perform better.
    """

    print("Adding weather interaction features...")

    # ---------------------------------------
    # Heat Index (simple approximation)
    # ---------------------------------------

    if {
        "temperature",
        "humidity",
    }.issubset(df.columns):

        df["heat_index"] = df["temperature"] + (0.1 * df["humidity"])

    # ---------------------------------------
    # Dryness Index
    # ---------------------------------------

    if {
        "temperature",
        "humidity",
    }.issubset(df.columns):

        df["dryness_index"] = df["temperature"] - (df["humidity"] / 10)

    # ---------------------------------------
    # Water Stress Index
    # ---------------------------------------

    if {
        "soil_moisture",
        "temperature",
    }.issubset(df.columns):

        df["water_stress"] = df["temperature"] / (df["soil_moisture"] + 1)

    # ---------------------------------------
    # Evaporation Risk
    # ---------------------------------------

    if {
        "temperature",
        "humidity",
        "soil_moisture",
    }.issubset(df.columns):

        df["evaporation_risk"] = ((df["temperature"] * 2) + (100 - df["humidity"]) + (100 - df["soil_moisture"])) / 3

    # ---------------------------------------
    # Favorable Growing Conditions
    # ---------------------------------------

    required_columns = {
        "temperature",
        "humidity",
        "soil_moisture",
    }

    if required_columns.issubset(df.columns):

        df["good_growing_conditions"] = ((df["temperature"].between(20, 30)) & (df["humidity"].between(50, 70)) & (df["soil_moisture"].between(30, 70))).astype(
            int
        )

    return df


# ==========================================================
# Plant Features
# ==========================================================


def add_plant_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create plant-specific features.

    Expected columns (if available):
        plant_type
        plant_age_days
        growth_stage
        watering_interval_days
        last_watered
        timestamp

    New features:
        plant_age_group
        watering_due
        days_since_watered
        growth_progress
    """

    print("Adding plant features...")

    # ------------------------------------------------------
    # Plant Age Group
    # ------------------------------------------------------

    if "plant_age_days" in df.columns:

        conditions = [
            df["plant_age_days"] <= 30,
            df["plant_age_days"].between(31, 90),
            df["plant_age_days"] > 90,
        ]

        labels = [
            "Seedling",
            "Growing",
            "Mature",
        ]

        df["plant_age_group"] = np.select(
            conditions,
            labels,
            default="Unknown",
        )

    # ------------------------------------------------------
    # Growth Progress
    # ------------------------------------------------------

    if "growth_stage" in df.columns:
        growth_stage = df["growth_stage"].astype(str).str.strip().str.lower()
        has_growth_stage_data = (~growth_stage.isin(UNKNOWN_TEXT_VALUES)).any()

        if has_growth_stage_data:
            growth_map = {
                "seed": 0,
                "seedling": 1,
                "vegetative": 2,
                "flowering": 3,
                "fruiting": 4,
                "mature": 5,
            }

            df["growth_progress"] = growth_stage.map(growth_map).fillna(-1).astype(int)

    # ------------------------------------------------------
    # Days Since Last Watering
    # ------------------------------------------------------

    if {
        "last_watered",
        "timestamp",
    }.issubset(df.columns):

        df["last_watered"] = pd.to_datetime(df["last_watered"])

        df["days_since_watered"] = (df["timestamp"] - df["last_watered"]).dt.days

    # ------------------------------------------------------
    # Watering Due
    # ------------------------------------------------------

    if {
        "days_since_watered",
        "watering_interval_days",
    }.issubset(df.columns):

        df["watering_due"] = (df["days_since_watered"] >= df["watering_interval_days"]).astype(int)

    return df


# ==========================================================
# Irrigation Features
# ==========================================================


def add_irrigation_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create irrigation-related features.

    New features:
        irrigation_priority
        irrigation_needed
        irrigation_score
    """

    print("Adding irrigation features...")

    irrigation_score = pd.Series(0.0, index=df.index)

    # Dry soil contributes the most
    if "soil_moisture" in df.columns:

        irrigation_score += 100 - df["soil_moisture"]

    # High temperature increases water demand
    if "temperature" in df.columns:

        irrigation_score += df["temperature"] * 0.8

    # Low humidity increases evaporation
    if "humidity" in df.columns:

        irrigation_score += (100 - df["humidity"]) * 0.4

    df["irrigation_score"] = irrigation_score.round(2)

    # ------------------------------------------------------
    # Irrigation Needed
    # ------------------------------------------------------

    df["irrigation_needed"] = (irrigation_score >= 80).astype(int)

    # ------------------------------------------------------
    # Irrigation Priority
    # ------------------------------------------------------

    conditions = [
        irrigation_score < 40,
        irrigation_score.between(40, 80),
        irrigation_score > 80,
    ]

    labels = [
        "Low",
        "Medium",
        "High",
    ]

    df["irrigation_priority"] = np.select(
        conditions,
        labels,
        default="Unknown",
    )

    return df


def add_target_aliases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add canonical target aliases when equivalent raw fields already exist.
    """

    if "light" in df.columns and "light_intensity" not in df.columns:
        df["light_intensity"] = df["light"]

    if "height_cm" in df.columns and "current_height_cm" not in df.columns:
        df["current_height_cm"] = df["height_cm"]

    if "irrigation_needed" in df.columns and "watering_needed" not in df.columns:
        df["watering_needed"] = df["irrigation_needed"]

    return df


def select_master_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep the broad master feature repository columns in a stable order.
    """

    selected_columns = [column for column in MASTER_FEATURE_COLUMNS if column in df.columns]

    return df.loc[:, selected_columns]


# ==========================================================
# Feature Engineering Pipeline
# ==========================================================


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the complete feature engineering pipeline.
    """

    print("\nStarting feature engineering...\n")

    df = df.copy()

    df = add_inferred_location_fields(df)

    df = add_derived_plant_age(df)

    df = add_time_features(df)

    df = add_location_features(df)

    df = add_temperature_features(df)

    df = add_humidity_features(df)

    df = add_soil_features(df)

    df = add_weather_interaction_features(df)

    df = add_plant_features(df)

    df = add_irrigation_features(df)

    df = add_target_aliases(df)

    df = select_master_feature_columns(df)

    print("\nFeature engineering completed.\n")

    return df


# ==========================================================
# Save Engineered Dataset
# ==========================================================


def save_featured_dataset(
    df: pd.DataFrame,
    output_file: Path = OUTPUT_FILE,
) -> None:
    """
    Save engineered dataset to CSV.
    """

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print(f"\nDataset saved to:\n{output_file}")


# ==========================================================
# Preview Engineered Dataset
# ==========================================================


def preview_featured_dataset(
    df: pd.DataFrame,
) -> None:
    """
    Display a quick summary of the engineered dataset.
    """

    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING SUMMARY")
    print("=" * 60)

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nFirst 5 Rows:")
    print(df.head())

    print("\nStatistical Summary:")
    print(df.describe(include="all"))


# ==========================================================
# Main Program
# ==========================================================


def main():
    """
    Execute the complete feature engineering pipeline.
    """

    print("=" * 60)
    print("SMART FARMING FEATURE ENGINEERING")
    print("=" * 60)

    # ------------------------------------------------------
    # Check input file
    # ------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"\nInput file not found:\n{INPUT_FILE}")

    print(f"\nLoading dataset:\n{INPUT_FILE}")

    # ------------------------------------------------------
    # Load merged dataset
    # ------------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    print(f"\nOriginal Shape: {df.shape}")

    # ------------------------------------------------------
    # Ensure timestamp is datetime
    # ------------------------------------------------------

    if "timestamp" in df.columns:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
        )

    # ------------------------------------------------------
    # Run Feature Engineering
    # ------------------------------------------------------

    featured_df = engineer_features(df)

    # ------------------------------------------------------
    # Remove duplicated columns (if any)
    # ------------------------------------------------------

    featured_df = featured_df.loc[:, ~featured_df.columns.duplicated()]

    # ------------------------------------------------------
    # Preview Result
    # ------------------------------------------------------

    preview_featured_dataset(featured_df)

    # ------------------------------------------------------
    # Save Dataset
    # ------------------------------------------------------

    save_featured_dataset(featured_df)

    print("\nFeature engineering completed successfully!")

    return featured_df


# ==========================================================
# Testing Utilities
# ==========================================================


def test_feature_engineering():
    """
    Basic test to verify that the feature engineering
    pipeline runs successfully.
    """

    print("\nRunning feature engineering tests...")

    try:

        df = pd.read_csv(INPUT_FILE)

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
        )

        engineered = engineer_features(df)

        assert len(engineered) == len(df)

        required_columns = {column for column in MASTER_FEATURE_COLUMNS if column in df.columns}
        assert required_columns.issubset(engineered.columns)

        duplicate_suffixes = ("_x", "_y")
        assert not any(column.endswith(duplicate_suffixes) for column in engineered.columns)

        if "growth_stage" not in df.columns or df["growth_stage"].isna().all():
            assert "growth_progress" not in engineered.columns

        assert engineered.isnull().sum().sum() >= 0

        print("All tests passed.")

        print(f"Original columns : {len(df.columns)}")

        print(f"Engineered columns : {len(engineered.columns)}")

    except Exception as e:

        print("Feature engineering test failed.")

        raise e


# ==========================================================
# Script Entry Point
# ==========================================================

if __name__ == "__main__":

    try:

        featured_dataset = main()

        print("\n" + "=" * 60)
        print("ENGINEERED DATASET PREVIEW")
        print("=" * 60)

        print(featured_dataset.head())

        print("\n")

        print("\nDone.")

    except Exception as e:

        print("\nAn error occurred during feature engineering.")

        print(e)
