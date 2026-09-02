"""
This service imports PredictionLayer, exposes business methods
for single/all tasks, and acts as the bridge between FastAPI routes
and ML layer.
"""

# backend/app/services/prediction/prediction_service.py

from pathlib import Path
import sys
from typing import Any, Dict, Optional
from ai.core.constants import ARTIFACTS_DIR
from ai.inference.prediction_layer import PredictionLayer, PredictionResult

# 1. Resolve project root (/smart-farming-system)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class PredictionService:
    """Service layer bridging FastAPI routes to AI PredictionLayer."""

    def __init__(self, artifacts_dir: Optional[Path] = None):
        # Force absolute path to /smart-farming-system/ai/artifacts
        target_artifacts = Path(artifacts_dir) if artifacts_dir else ARTIFACTS_DIR
        self.prediction_layer = PredictionLayer(artifacts_dir=target_artifacts)

    def predict_task(
        self,
        task: str,
        plant_data: Dict[str, Any],
        sensor_data: Optional[Dict[str, Any]] = None,
        weather_data: Optional[Dict[str, Any]] = None,
        fetch_weather: bool = True,
    ) -> Dict[str, Any]:
        """Predict a single AI task domain."""
        result: PredictionResult = self.prediction_layer.predict_task(
            task=task,
            plant_data=plant_data,
            sensor_data=sensor_data,
            weather_data=weather_data,
            fetch_weather=fetch_weather,
        )
        return result.to_dict()

    def predict_all_tasks(
        self,
        plant_data: Dict[str, Any],
        sensor_data: Optional[Dict[str, Any]] = None,
        weather_data: Optional[Dict[str, Any]] = None,
        fetch_weather: bool = True,
    ) -> Dict[str, Dict[str, Any]]:
        """Run inference across all 4 supported ML models."""
        results = self.prediction_layer.predict_all(
            plant_data=plant_data,
            sensor_data=sensor_data,
            weather_data=weather_data,
            fetch_weather=fetch_weather,
        )
        return {task: res.to_dict() for task, res in results.items()}


_prediction_service: Optional[PredictionService] = None


def get_prediction_service() -> PredictionService:
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service
