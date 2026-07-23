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

# ==========================================================
# Project Paths
# ==========================================================

# feature_engineering.py
#        │
# preprocessing/
#        │
# ai/

AI_FOLDER = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = AI_FOLDER / "datasets" / "processed"

INPUT_FILE = PROCESSED_DATA_DIR / "merged_data.csv"
OUTPUT_FILE = PROCESSED_DATA_DIR / "featured_data.csv"

# ==========================================================
# Countries that generally use Tropical Wet / Dry seasons
# ==========================================================

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
        plant_age
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

    if "plant_age" in df.columns:

        conditions = [
            df["plant_age"] <= 30,
            df["plant_age"].between(31, 90),
            df["plant_age"] > 90,
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

        growth_map = {
            "seed": 0,
            "seedling": 1,
            "vegetative": 2,
            "flowering": 3,
            "fruiting": 4,
            "mature": 5,
        }

        df["growth_progress"] = df["growth_stage"].astype(str).str.lower().map(growth_map).fillna(-1).astype(int)

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

    irrigation_score = np.zeros(len(df))

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


# ==========================================================
# Feature Engineering Pipeline
# ==========================================================


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the complete feature engineering pipeline.
    """

    print("\nStarting feature engineering...\n")

    df = add_time_features(df)

    df = add_location_features(df)

    df = add_temperature_features(df)

    df = add_humidity_features(df)

    df = add_soil_features(df)

    df = add_weather_interaction_features(df)

    df = add_plant_features(df)

    df = add_irrigation_features(df)

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
    # Sort columns alphabetically
    # (Optional but makes inspection easier)
    # ------------------------------------------------------

    featured_df = featured_df.reindex(
        sorted(featured_df.columns),
        axis=1,
    )

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

        assert len(engineered.columns) >= len(df.columns)

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

        test_feature_engineering()

        print("\nDone.")

    except Exception as e:

        print("\nAn error occurred during feature engineering.")

        print(e)
