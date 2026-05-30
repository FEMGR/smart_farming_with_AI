# app/schemas/planning_schema.py <<'PY'
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FarmSectionCreate(BaseModel):
    location_id: int
    name: str
    section_type: str = "production"
    width_m: Decimal = Field(gt=0)
    length_m: Decimal = Field(gt=0)
    area_m2: Optional[Decimal] = None


class FarmSectionUpdate(BaseModel):
    location_id: Optional[int] = None
    name: Optional[str] = None
    section_type: Optional[str] = None
    width_m: Optional[Decimal] = Field(default=None, gt=0)
    length_m: Optional[Decimal] = Field(default=None, gt=0)
    area_m2: Optional[Decimal] = None


class FarmSectionResponse(FarmSectionCreate):
    id: int
    user_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CropPlanCreate(BaseModel):
    crop_name: str
    target_yield: Optional[Decimal] = None
    target_yield_unit: str = "kg"
    total_area_m2: Optional[Decimal] = None

    germination_days: int = 7
    transplant_days: int = 14
    harvest_days: int = 45
    desired_harvest_interval_days: int = 14

    planned_start_date: date


class CropPlanResponse(CropPlanCreate):
    id: int
    user_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class ProductionBatchResponse(BaseModel):
    id: int
    user_id: int
    crop_plan_id: int
    section_id: Optional[int]

    batch_number: int

    seed_start_date: date
    expected_germination_date: Optional[date]
    expected_transplant_date: Optional[date]
    expected_harvest_date: Optional[date]

    allocated_area_m2: Optional[Decimal]
    expected_yield: Optional[Decimal]

    status: str

    model_config = ConfigDict(from_attributes=True)


class SuccessionPlanPreview(BaseModel):
    crop_name: str
    required_sections: int
    recommended_section_count: int
    area_per_section_m2: Optional[Decimal]
    batches: list[ProductionBatchResponse]
    planning_explanation: Optional[str] = None


class PolyculturePreviewRequest(BaseModel):
    location_id: int
    section_ids: list[int]
    intended_crops: list[str]
    start_date: date
    harvest_interval_days: int = 14


class PolycultureConfirmRequest(PolyculturePreviewRequest):
    name: Optional[str] = None


class PolycultureGroupPreview(BaseModel):
    group_id: int
    section_id: Optional[int] = None
    main_crops: list[str]
    suggested_companions: list[dict] = []
    allocated_area_m2: Optional[Decimal] = None
    warnings: list[str] = []
    timeline: list[dict] = []


class PolyculturePreviewResponse(BaseModel):
    location_id: int
    section_ids: list[int]
    group_count: int
    total_available_area_m2: Decimal
    groups: list[dict]
    layout: dict
    warnings: list[str]
    suggested_additional_sections: list[dict]
