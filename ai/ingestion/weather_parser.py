"""
Parse raw Open-Meteo weather JSON saved by backend weather_service.py.
"""

# ai/ingestion/weather_parser.py

import csv
import json
from pathlib import Path

AI_FOLDER = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = AI_FOLDER / "datasets" / "raw"

DEFAULT_INPUT_FILE = RAW_DATA_DIR / "weather.json"
DEFAULT_OUTPUT_FILE = RAW_DATA_DIR / "weather.csv"


def load_weather_json(path: Path = DEFAULT_INPUT_FILE) -> dict:
    """
    Load raw Open-Meteo JSON from ai/datasets/raw/.
    """

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_weather_json(data: dict) -> list[dict]:
    """
    Convert Open-Meteo hourly weather JSON into tabular rows.
    """

    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []

    rows = []
    for index, timestamp in enumerate(times):
        rows.append(
            {
                "date": timestamp,
                "air_temp_c": _get_hourly_value(hourly, "temperature_2m", index),
                "humidity_pct": _get_hourly_value(hourly, "relative_humidity_2m", index),
                "rainfall_mm": _get_hourly_value(hourly, "rain", index),
                "precipitation_probability": _get_hourly_value(hourly, "precipitation_probability", index),
                "wind_kmh": _get_hourly_value(hourly, "wind_speed_10m", index),
                "soil_temp_c": _get_hourly_value(hourly, "soil_temperature_0cm", index),
                "soil_moisture_pct": _soil_moisture_to_percent(_get_hourly_value(hourly, "soil_moisture_0_to_1cm", index)),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timezone"),
            }
        )

    return rows


def save_rows_csv(rows: list[dict], path: Path = DEFAULT_OUTPUT_FILE) -> Path:
    """
    Save parsed weather rows as CSV for downstream preprocessing.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "date",
        "air_temp_c",
        "humidity_pct",
        "rainfall_mm",
        "precipitation_probability",
        "wind_kmh",
        "soil_temp_c",
        "soil_moisture_pct",
        "latitude",
        "longitude",
        "timezone",
    ]

    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return path


def parse_weather_file(input_path: Path = DEFAULT_INPUT_FILE, output_path: Path = DEFAULT_OUTPUT_FILE) -> Path:
    """
    Parse ai/datasets/raw/weather.json and save a tabular CSV copy.
    """

    data = load_weather_json(input_path)
    rows = parse_weather_json(data)

    return save_rows_csv(rows, output_path)


def _get_hourly_value(hourly: dict, key: str, index: int):
    values = hourly.get(key) or []

    if index >= len(values):
        return None

    return values[index]


def _soil_moisture_to_percent(value):
    if value is None:
        return None

    return value * 100


if __name__ == "__main__":
    output_file = parse_weather_file()
    print(f"Parsed weather data saved to: {output_file}")
