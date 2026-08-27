"""
normalize.py

Purpose
-------
Normalize cleaned data into a format suitable for machine learning.
Converting values into scale between 0 to 1, standardizing, et.c to enable easier analysis.
"""

# ai/prepocessing/normalize.py

import pandas as pd
from sklearn.preprocessing import (
    MinMaxScaler,
    StandardScaler,
)

# =====================================================
# Helper Functions
# =====================================================


def get_existing_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    """
    Return only the columns that exist in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    columns : list[str]
        List of requested column names.

    Returns
    -------
    list[str]
        Existing column names.
    """

    return [col for col in columns if col in df.columns]


def normalize_with_scaler(df: pd.DataFrame, columns: list[str], scaler) -> pd.DataFrame:
    """
    Normalize selected columns using the provided scaler.
    """

    df = df.copy()

    existing_columns = get_existing_columns(df, columns)

    if not existing_columns:
        return df

    df[existing_columns] = scaler.fit_transform(df[existing_columns])

    return df


# =====================================================
# Numeric Normalization
# =====================================================


def normalize_minmax(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Normalize values to the range [0, 1]. Used for Neural Networks,Deep Learning or Deep Learning
    Data already within known bounds, such as  soil moisture, humidity, light intensity
    """

    scaler = MinMaxScaler()

    return normalize_with_scaler(df, columns, scaler)


def normalize_standard(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Standardize values to mean=0 and std=1.
    Good for Logistic Regression, Linear Regression, SVM, PCA, K-Means clustering
    """

    scaler = StandardScaler()

    return normalize_with_scaler(df, columns, scaler)


# =====================================================
# Categorical Encoding
# =====================================================


def normalize_text_columns(df: pd.DataFrame, exclude: list[str] | None = None) -> pd.DataFrame:
    """
    Normalize all text columns except those excluded.
    """

    df = df.copy()

    if exclude is None:
        exclude = []

    text_columns = df.select_dtypes(include=["object", "string"]).columns

    for col in text_columns:
        if col in exclude:
            continue

        df[col] = df[col].fillna("unknown").astype(str).str.strip().str.lower()

    return df


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

    existing_columns = get_existing_columns(df, columns)

    if not existing_columns:
        return df

    return pd.get_dummies(df, columns=existing_columns, dtype=int)


# =====================================================
# Boolean Conversion
# =====================================================


def convert_boolean(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Convert True/False columns into 1/0.
    """

    df = df.copy()

    existing_columns = get_existing_columns(df, columns)

    for column in existing_columns:
        df[column] = df[column].astype(int)

    return df


# =====================================================
# Datetime Features
# =====================================================


def extract_datetime_features(df: pd.DataFrame, datetime_column: str) -> pd.DataFrame:
    """
    Extract useful features from a datetime column when valid values exist.
    """

    df = df.copy()

    df[datetime_column] = pd.to_datetime(df[datetime_column], errors="coerce")

    if df[datetime_column].notna().sum() == 0:
        return df

    df["year"] = df[datetime_column].dt.year
    df["month"] = df[datetime_column].dt.month
    df["day"] = df[datetime_column].dt.day
    df["hour"] = df[datetime_column].dt.hour
    df["day_of_week"] = df[datetime_column].dt.dayofweek
    df["week_of_year"] = df[datetime_column].dt.isocalendar().week.astype("Int64")

    return df


# =====================================================
# Complete Normalization
# =====================================================


def normalize_dataframe(
    df: pd.DataFrame,
    datetime_columns: list[str] | None = None,
    boolean_columns: list[str] | None = None,
    exclude_text_columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    Apply generic normalization to any DataFrame.

    This function:
        - Normalizes text columns
        - Converts boolean columns to integers
        - Extracts datetime features

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    datetime_columns : list[str], optional
        Columns containing datetime values.

    boolean_columns : list[str], optional
        Columns containing boolean values.

    exclude_text_columns : list[str], optional
        Text columns to exclude from normalization.

    Returns
    -------
    pd.DataFrame
        Normalized DataFrame.
    """

    df = df.copy()

    # Normalize text
    df = normalize_text_columns(df, exclude=exclude_text_columns)

    # Convert booleans
    if boolean_columns:
        existing_boolean_columns = [col for col in boolean_columns if col in df.columns]

        if existing_boolean_columns:
            df = convert_boolean(df, existing_boolean_columns)

    # Extract datetime features
    if datetime_columns:
        for column in datetime_columns:
            if column in df.columns:
                df = extract_datetime_features(df, column)

    return df


def normalize_sensor_data(df: pd.DataFrame, method: str = "minmax") -> pd.DataFrame:
    """
    Normalize the sensor dataset.
    """
    numeric_columns = [
        "temperature",
        "humidity",
        "soil_moisture",
        "soil_ph",
        "light",
        "light_intensity",
    ]

    if method == "minmax":
        df = normalize_minmax(df, numeric_columns)

    elif method == "standard":
        df = normalize_standard(df, numeric_columns)

    else:
        raise ValueError(f"Unknown normalization method: {method}")

    # Extract datetime features if timestamp exists
    if "timestamp" in df.columns:
        df = extract_datetime_features(df, "timestamp")

    return df


def normalize_all_data(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Normalize every dataset used in the AI pipeline.

    Parameters
    ----------
    datasets : dict
        Dictionary containing DataFrames.

    Returns
    -------
    dict
        Dictionary of normalized DataFrames.
    """

    normalized = {}

    for name, df in datasets.items():

        # Apply generic normalization
        df = normalize_dataframe(
            df,
            datetime_columns=["timestamp"],
            boolean_columns=["is_raining", "use_sensor"],
        )

        # Dataset-specific normalization
        if name == "sensor":
            df = normalize_sensor_data(df)

        # Future expansion
        # elif name == "weather":
        #     df = normalize_weather_data(df)

        # elif name == "plants":
        #     df = normalize_plant_data(df)

        normalized[name] = df

    return normalized


# =====================================================
# Preview Utility
# =====================================================


def preview(df: pd.DataFrame):

    print("\nNormalized Data")
    print("-" * 60)

    print(df.head())

    print("\nData Types")
    print(df.dtypes)
    print("-" * 60)


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

    normalizedMinMax = normalize_sensor_data(
        sample,
    )
    normalizedStd = normalize_sensor_data(sample, method="standard")

    preview(normalizedMinMax)
    preview(normalizedStd)
