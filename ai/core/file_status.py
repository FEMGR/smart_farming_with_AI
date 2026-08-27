"""
Reusable file creation status helpers for long-running pipeline writes.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

import joblib
import pandas as pd

T = TypeVar("T")


def run_file_creation(
    output_file: str | Path,
    writer: Callable[[Path], T],
    description: str = "file",
) -> T:
    """
    Run a file write while printing started/completed/interrupted/failed status.
    """

    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[creating] {description}: {path}", flush=True)

    try:
        result = writer(path)
    except KeyboardInterrupt:
        print(
            f"[interrupted] {description}: {path}. The file may be incomplete.",
            flush=True,
        )
        raise
    except Exception as error:
        print(f"[failed] {description}: {path} ({error})", flush=True)
        raise

    print(f"[completed] {description}: {path}", flush=True)
    return result


def write_dataframe_csv_with_status(
    df: pd.DataFrame,
    output_file: str | Path,
    description: str = "CSV dataset",
    **to_csv_kwargs,
) -> Path:
    """
    Write a DataFrame to CSV with lifecycle status messages.
    """

    def writer(path: Path) -> Path:
        df.to_csv(path, index=False, **to_csv_kwargs)
        return path

    return run_file_creation(output_file, writer, description=description)


def write_json_with_status(
    data: Any,
    output_file: str | Path,
    description: str = "JSON file",
    **json_kwargs,
) -> Path:
    """
    Write JSON with lifecycle status messages.
    """

    def writer(path: Path) -> Path:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, **json_kwargs)
        return path

    return run_file_creation(output_file, writer, description=description)


def write_joblib_with_status(
    artifact: Any,
    output_file: str | Path,
    description: str = "joblib artifact",
) -> Path:
    """
    Write a joblib artifact with lifecycle status messages.
    """

    def writer(path: Path) -> Path:
        joblib.dump(artifact, path)
        return path

    return run_file_creation(output_file, writer, description=description)
