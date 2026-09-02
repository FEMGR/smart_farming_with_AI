# app/api/v1/routes/prediction.py

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.prediction_schema import (
    AllPredictionsRequest,
    PredictionResponse,
    SinglePredictionRequest,
)
from app.services.prediction.prediction_service import (
    PredictionService,
    get_prediction_service,
)

router = APIRouter(prefix="/predictions", tags=["ML Predictions"])


@router.post("/task", response_model=PredictionResponse)
def predict_single_task(
    payload: SinglePredictionRequest,
    service: PredictionService = Depends(get_prediction_service),
):
    """Run prediction for a specific task ('irrigation', 'disease', 'growth', 'yield')."""
    try:
        plant_dict = payload.plant_data.model_dump(exclude_unset=True)
        sensor_dict = payload.sensor_data.model_dump(exclude_unset=True) if payload.sensor_data else None
        weather_dict = payload.weather_data.model_dump(exclude_unset=True) if payload.weather_data else None

        result = service.predict_task(
            task=payload.task,
            plant_data=plant_dict,
            sensor_data=sensor_dict,
            weather_data=weather_dict,
            fetch_weather=payload.fetch_weather,
        )

        return PredictionResponse(success=True, data=result)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(err)}")


@router.post("/all", response_model=PredictionResponse)
def predict_all_tasks(
    payload: AllPredictionsRequest,
    service: PredictionService = Depends(get_prediction_service),
):
    """Run predictions across all 4 supported models in one request."""
    try:
        plant_dict = payload.plant_data.model_dump(exclude_unset=True)
        sensor_dict = payload.sensor_data.model_dump(exclude_unset=True) if payload.sensor_data else None
        weather_dict = payload.weather_data.model_dump(exclude_unset=True) if payload.weather_data else None

        results = service.predict_all_tasks(
            plant_data=plant_dict,
            sensor_data=sensor_dict,
            weather_data=weather_dict,
            fetch_weather=payload.fetch_weather,
        )

        return PredictionResponse(success=True, data=results)
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(err)}")
