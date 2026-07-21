"""
normalize.py

Purpose
-------
Normalize cleaned data into a format suitable for machine learning.

"""

# ai/prepocessing/normalize.py

import pandas as pd
from sklearn.preprocessing import (
    MinMaxScaler,
    StandardScaler,
)

# -----------------------------------------------------
# Global Scalers
# -----------------------------------------------------

# Scale values between 0 and 1
minmax_scaler = MinMaxScaler()

# Scale values to mean=0, std=1
standard_scaler = StandardScaler()


# =====================================================
# Numeric Normalization
# =====================================================


def normalize_minmax(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Normalize selected columns to the range [0, 1].

    Formula:
        (value - min) / (max - min)
    """

    df = df.copy()

    df[columns] = minmax_scaler.fit_transform(df[columns])

    return df


def normalize_standard(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Standardize selected columns.

    Formula:
        (value - mean) / std
    """

    df = df.copy()

    df[columns] = standard_scaler.fit_transform(df[columns])

    return df


# =====================================================
# Categorical Encoding
# =====================================================


def encode_categorical(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Convert categorical columns into one-hot encoded columns.

    Example:

        sunny
        rainy

    becomes

        weather_sunny
        weather_rainy
    """

    return pd.get_dummies(df, columns=columns, dtype=int)


# =====================================================
# Boolean Conversion
# =====================================================


def convert_boolean(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Convert True/False columns into 1/0.
    """

    df = df.copy()

    for column in columns:
        df[column] = df[column].astype(int)

    return df


# =====================================================
# Datetime Features
# =====================================================


def extract_datetime_features(df: pd.DataFrame, datetime_column: str) -> pd.DataFrame:
    """
    Extract useful features from a datetime column.
    """

    df = df.copy()

    df[datetime_column] = pd.to_datetime(df[datetime_column])

    df["year"] = df[datetime_column].dt.year
    df["month"] = df[datetime_column].dt.month
    df["day"] = df[datetime_column].dt.day
    df["hour"] = df[datetime_column].dt.hour
    df["weekday"] = df[datetime_column].dt.dayofweek

    return df


# =====================================================
# Complete Normalization
# =====================================================


def normalize_sensor_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the sensor dataset.
    """

    numeric_columns = [
        "temperature",
        "humidity",
        "soil_moisture",
        "light_intensity",
    ]

    df = normalize_minmax(df, numeric_columns)

    df = extract_datetime_features(df, "timestamp")

    return df


# =====================================================
# Preview Utility
# =====================================================


def preview(df: pd.DataFrame):

    print("\nNormalized Data")
    print("-" * 60)

    print(df.head())

    print("\nData Types")
    print(df.dtypes)


# =====================================================
# Example
# =====================================================

if __name__ == "__main__":

    sample = pd.DataFrame(
        {
            "temperature": [24, 30, 35],
            "humidity": [60, 70, 90],
            "soil_moisture": [35, 50, 65],
            "light_intensity": [400, 800, 1200],
            "timestamp": [
                "2026-07-01 08:00",
                "2026-07-01 12:00",
                "2026-07-01 16:00",
            ],
        }
    )

    normalized = normalize_sensor_data(sample)

    preview(normalized)
