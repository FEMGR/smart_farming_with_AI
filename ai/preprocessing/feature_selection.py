"""
Purpose
-------
Build task-specific training datasets from the master feature repository.

This script does not create new features. It only selects relevant columns from
featured_data.csv and writes one training CSV per model objective.
"""

from pathlib import Path

import pandas as pd

# ==========================================================
# Project Paths
# ==========================================================

AI_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = AI_FOLDER / "datasets" / "processed"

INPUT_FILE = PROCESSED_DATA_DIR / "featured_data.csv"

DATABASE_IDENTIFIER_COLUMNS = {
    "plant_id",
    "location_id",
    "user_id",
    "sensor_id",
}

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


def selected_target_column(df: pd.DataFrame, target_candidates: list[str]) -> str | None:
    """
    Return the first available target candidate for a model.
    """

    for target in target_candidates:
        if target in df.columns:
            return target

    return None


def select_training_columns(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, list[str], str | None]:
    """
    Select model-specific feature columns and one available target column.
    """

    feature_columns = [column for column in config["features"] if column in df.columns and column not in DATABASE_IDENTIFIER_COLUMNS]

    target_column = selected_target_column(df, config["target_candidates"])
    selected_columns = feature_columns.copy()

    if target_column is not None and target_column not in DATABASE_IDENTIFIER_COLUMNS:
        selected_columns.append(target_column)

    missing_columns = [column for column in [*config["features"], *config["target_candidates"]] if column not in df.columns]

    return df.loc[:, selected_columns], missing_columns, target_column


def save_training_dataset(df: pd.DataFrame, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)


def build_training_datasets(featured_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Build and save all configured training datasets.
    """

    training_datasets = {}

    for model_name, config in TRAINING_DATASETS.items():
        training_df, missing_columns, target_column = select_training_columns(featured_df, config)
        save_training_dataset(training_df, config["output_file"])
        training_datasets[model_name] = training_df

        print(f"\n{model_name}_training.csv")
        print(f"Saved to: {config['output_file']}")
        print(f"Shape: {training_df.shape}")

        if target_column is None:
            print(f"Target: missing. Expected one of {config['target_candidates']}")
        else:
            print(f"Target: {target_column}")

        if missing_columns:
            print(f"Missing optional columns: {missing_columns}")

    return training_datasets


def split_training_sets(
    featured_df: pd.DataFrame | None = None,
    input_file: Path = INPUT_FILE,
) -> dict[str, pd.DataFrame]:
    """
    Load the master feature repository and write task-specific training CSVs.
    """

    if featured_df is None:
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        featured_df = pd.read_csv(input_file)

    return build_training_datasets(featured_df)


def main() -> dict[str, pd.DataFrame]:
    return split_training_sets()


if __name__ == "__main__":
    main()
