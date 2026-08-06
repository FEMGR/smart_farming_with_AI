#!/usr/bin/env python3
"""
Export plant data from the local PostgreSQL backend database.

The exported CSV is intended as raw plant input for the AI pipeline. It keeps
watering-derived features out of the extract; those belong in
feature_engineering.py.
"""

# ai/ingestion/export_plants.py

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import OperationalError, SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "ai" / "datasets" / "raw"

PLANT_COLUMNS = [
    "user_id",
    "plant_id",
    "location_id",
    "species_id",
    "plant_name",
    "scientific_name",
    "last_watered",
    "planting_date",
    "watering_interval_days",
    "recommended_soil",
    "life_cycle",
    "environment_type",
    "latitude",
    "longitude",
    "height_cm",
    "growth_stage",
    "propagation_method",
    "pest_susceptibility",
    "recommended_sunlight",
    "is_sensor_enabled",
]

INTEGER_COLUMNS = [
    "user_id",
    "plant_id",
    "location_id",
    "species_id",
    "watering_interval_days",
]

FLOAT_COLUMNS = [
    "latitude",
    "longitude",
    "height_cm",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export backend PostgreSQL plant data to an AI raw CSV dataset.",
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=None,
        help="Export only one user's plants. If omitted, export all users.",
    )
    parser.add_argument(
        "--location-id",
        type=int,
        default=None,
        help="Export only plants in one location. If omitted, include all locations.",
    )
    parser.add_argument(
        "--species-id",
        type=int,
        default=None,
        help="Export only plants for one species. If omitted, include all species.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="CSV output path. If omitted, a filter-aware filename is created in ai/datasets/raw/.",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="PostgreSQL URL. Defaults to DATABASE_URL from the environment or .env.",
    )
    parser.add_argument(
        "--empty-ok",
        action="store_true",
        help="Write a header-only CSV instead of failing when no plants are found.",
    )
    return parser.parse_args()


def load_database_url(cli_database_url: str | None) -> URL:
    load_dotenv(PROJECT_ROOT / ".env")

    database_url = cli_database_url or os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set. Add it to .env or pass --database-url.")

    url = make_url(database_url)
    if url.drivername.startswith("postgresql+asyncpg"):
        url = url.set(drivername="postgresql+psycopg2")
    elif url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg2")
    elif not url.drivername.startswith("postgresql"):
        raise ValueError(f"Expected a PostgreSQL DATABASE_URL, got {url.drivername!r}.")

    return url


def load_sql(filename: str) -> str:
    sql = (PROJECT_ROOT / "backend" / "app" / "sql" / filename).read_text(encoding="utf-8").strip()
    return sql.removesuffix(";").strip()


def build_default_output_path(
    user_id: int | None = None,
    location_id: int | None = None,
    species_id: int | None = None,
) -> Path:
    filename_parts = ["plants"]
    if user_id is not None:
        filename_parts.extend(["user", str(user_id)])
    if location_id is not None:
        filename_parts.extend(["location", str(location_id)])
    if species_id is not None:
        filename_parts.extend(["species", str(species_id)])
    if len(filename_parts) == 1:
        filename_parts.append("all")

    return RAW_DATA_DIR / f"{'_'.join(filename_parts)}.csv"


def build_filtered_query(
    base_sql: str,
    user_id: int | None = None,
    location_id: int | None = None,
    species_id: int | None = None,
) -> tuple[str, dict[str, int]]:
    conditions = []
    parameters = {}

    if user_id is not None:
        conditions.append("p.user_id = :user_id")
        parameters["user_id"] = user_id
    if location_id is not None:
        conditions.append("p.location_id = :location_id")
        parameters["location_id"] = location_id
    if species_id is not None:
        conditions.append("p.species_id = :species_id")
        parameters["species_id"] = species_id

    query = base_sql
    if conditions:
        query += "\nWHERE " + " AND ".join(conditions)

    query += """
ORDER BY
    p.user_id,
    p.location_id NULLS LAST,
    p.id
"""

    return query, parameters


def describe_filters(
    user_id: int | None = None,
    location_id: int | None = None,
    species_id: int | None = None,
) -> str:
    filters = []
    if user_id is not None:
        filters.append(f"user_id={user_id}")
    if location_id is not None:
        filters.append(f"location_id={location_id}")
    if species_id is not None:
        filters.append(f"species_id={species_id}")

    return ", ".join(filters) if filters else "all plants"


def fetch_plants(
    database_url: URL,
    user_id: int | None = None,
    location_id: int | None = None,
    species_id: int | None = None,
) -> pd.DataFrame:
    base_sql = load_sql("export_plants.sql")
    query, parameters = build_filtered_query(base_sql, user_id, location_id, species_id)
    engine = create_engine(database_url)

    with engine.connect() as connection:
        df = pd.read_sql_query(text(query), connection, params=parameters)

    return normalize_dataframe_types(df.reindex(columns=PLANT_COLUMNS))


def normalize_dataframe_types(df: pd.DataFrame) -> pd.DataFrame:
    for column in INTEGER_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

    for column in FLOAT_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def export_dataframe_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def export_plants(
    database_url: URL,
    output_path: Path,
    user_id: int | None = None,
    location_id: int | None = None,
    species_id: int | None = None,
    empty_ok: bool = False,
) -> int:
    df = fetch_plants(database_url, user_id, location_id, species_id)

    if df.empty and not empty_ok:
        raise RuntimeError(f"No plants found for {describe_filters(user_id, location_id, species_id)}. " "Use --empty-ok to write a header-only CSV.")

    export_dataframe_to_csv(df, output_path)
    return len(df)


def main() -> int:
    args = parse_args()
    output_path = args.output or build_default_output_path(args.user_id, args.location_id, args.species_id)
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    try:
        database_url = load_database_url(args.database_url)
        row_count = export_plants(
            database_url,
            output_path,
            user_id=args.user_id,
            location_id=args.location_id,
            species_id=args.species_id,
            empty_ok=args.empty_ok,
        )
    except OperationalError as exc:
        detail = str(getattr(exc, "orig", exc)).strip() or str(exc).strip()
        print(f"export_plants failed: could not connect to PostgreSQL. {detail}", file=sys.stderr)
        return 1
    except (SQLAlchemyError, RuntimeError, ValueError) as exc:
        print(f"export_plants failed: {exc}", file=sys.stderr)
        return 1

    print(f"Exported {row_count} plants for " f"{describe_filters(args.user_id, args.location_id, args.species_id)} to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
