"""Generate and persist per-plant timeline snapshots."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.lifecycle.plant_timeline_snapshot import PlantTimelineSnapshot
from app.models.plant import Plant
from app.models.production.farm_section import FarmSection
from app.models.soil_condition import SoilCondition
from app.services.growth_fact_service import GrowthFactMatch, resolve_growth_fact
from app.services.lifecycle.timeline_service import get_crop_timeline
from app.services.plant_taxonomy_service import PlantIdentity

DEFAULT_GERMINATION_MIN = 7
DEFAULT_GERMINATION_MAX = 14
PROJECT_ROOT = Path(__file__).resolve().parents[4]
WEATHER_FACT_PATH = PROJECT_ROOT / "logic_companion_planting" / "data" / "weather_fact.pl"
_WEATHER_FACT_RE = re.compile(r"^\s*current_weather\(([^,]+),\s*([^,]+),\s*([^)]+)\)\.\s*$")


def _iso(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _int_or_default(value: int | None, default: int) -> int:
    return int(value) if value is not None else default


def _timeline_basis_days(plant_atom: str) -> dict:
    return get_crop_timeline(plant_atom)


def _load_local_weather_facts() -> dict[str, dict[str, str]]:
    try:
        lines = WEATHER_FACT_PATH.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}

    weather: dict[str, dict[str, str]] = {}
    for line in lines:
        match = _WEATHER_FACT_RE.match(line)
        if not match:
            continue
        time_key, factor, level = [part.strip().strip("'").lower() for part in match.groups()]
        weather.setdefault(time_key, {})[factor] = level
    return weather


def _latest_soil_condition(db: Session, plant_id: int) -> SoilCondition | None:
    return db.query(SoilCondition).filter(SoilCondition.plant_id == plant_id).order_by(SoilCondition.recorded_at.desc()).first()


def _context_adjustments(db: Session, plant: Plant, fact) -> dict:
    warnings: list[str] = []
    prolog_warnings: list[dict] = []
    weather = _load_local_weather_facts()

    today = weather.get("today", {})
    tomorrow = weather.get("tomorrow", {})
    if tomorrow.get("precipitation") in {"high", "extreme"}:
        message = "Local Prolog weather facts indicate high precipitation tomorrow; delay transplanting if the section is exposed."
        warnings.append(message)
        prolog_warnings.append({"source": "weather_fact.pl", "rule": "precipitation_risk", "message": message})
    if tomorrow.get("wind") in {"high", "extreme"}:
        message = "Local Prolog weather facts indicate high wind tomorrow; protect seedlings and avoid transplant shock."
        warnings.append(message)
        prolog_warnings.append({"source": "weather_fact.pl", "rule": "wind_risk", "message": message})
    if today.get("temperature") == "high" and getattr(fact, "optimum_soil_temp_c", None):
        warnings.append(
            f"Current local Prolog weather temperature is high; verify soil temperature stays near " f"{fact.optimum_soil_temp_c} C for germination."
        )

    sections = []
    if plant.location_id:
        sections = (
            db.query(FarmSection)
            .filter(
                FarmSection.user_id == plant.user_id,
                FarmSection.location_id == plant.location_id,
                FarmSection.is_active.is_(True),
            )
            .all()
        )
        if not sections:
            warnings.append("Plant has a location but no active farm section context for timeline adjustment.")
    else:
        warnings.append("Plant has no location; section and weather exposure adjustments are limited.")

    sensor_context = {"use_sensor": bool(plant.use_sensor), "latest_soil": None}
    if plant.use_sensor:
        soil = _latest_soil_condition(db, plant.id)
        if soil:
            soil_temperature = float(soil.temperature) if soil.temperature is not None else None
            soil_moisture = float(soil.moisture) if soil.moisture is not None else None
            sensor_context["latest_soil"] = {
                "recorded_at": soil.recorded_at.isoformat() if soil.recorded_at else None,
                "temperature_c": soil_temperature,
                "moisture": soil_moisture,
                "humidity": float(soil.humidity) if soil.humidity is not None else None,
                "ph": float(soil.ph) if soil.ph is not None else None,
            }
            viable_min = getattr(fact, "viable_temp_min_c", None)
            viable_max = getattr(fact, "viable_temp_max_c", None)
            if soil_temperature is not None and viable_min is not None and soil_temperature < viable_min:
                warnings.append(f"Sensor soil temperature is below viable germination range ({viable_min}-{viable_max} C).")
            if soil_temperature is not None and viable_max is not None and soil_temperature > viable_max:
                warnings.append(f"Sensor soil temperature is above viable germination range ({viable_min}-{viable_max} C).")
        else:
            warnings.append("Plant is marked sensor-enabled but has no soil sensor reading yet.")

    return {
        "weather": {"source": "local_prolog_weather_fact", "facts": weather},
        "section": {
            "location_id": plant.location_id,
            "active_section_count": len(sections),
            "active_sections": [{"id": section.id, "name": section.name, "type": section.section_type} for section in sections],
        },
        "sensor": sensor_context,
        "prolog_warnings": prolog_warnings,
        "warnings": warnings,
    }


def build_plant_timeline_snapshot(
    plant: Plant,
    identity: PlantIdentity,
    fact_match: GrowthFactMatch,
    context_adjustments: dict | None = None,
) -> dict:
    start_date = plant.planting_date or date.today()
    fact = fact_match.fact

    germination_min = _int_or_default(getattr(fact, "germination_days_min", None), DEFAULT_GERMINATION_MIN)
    germination_max = _int_or_default(getattr(fact, "germination_days_max", None), DEFAULT_GERMINATION_MAX)
    timeline_defaults = _timeline_basis_days(identity.plant_atom)

    stratification_required = bool(getattr(fact, "stratification_required", False)) if fact else False
    stratification_days_max = _int_or_default(getattr(fact, "stratification_days_max", None), 0)
    transplant_days = int(timeline_defaults.get("transplant_days") or 0)
    harvest_days = int(timeline_defaults.get("harvest_days") or 60)

    events = []
    if stratification_required and stratification_days_max > 0:
        events.append(
            {
                "event_type": "stratification_start",
                "label": "Start seed stratification",
                "date": _iso(start_date - timedelta(days=stratification_days_max)),
                "offset_days": -stratification_days_max,
            }
        )

    events.extend(
        [
            {
                "event_type": "sow",
                "label": "Sow seeds or record planting",
                "date": _iso(start_date),
                "offset_days": 0,
            },
            {
                "event_type": "germination_window_start",
                "label": "Expected germination window starts",
                "date": _iso(start_date + timedelta(days=germination_min)),
                "offset_days": germination_min,
            },
            {
                "event_type": "germination_window_end",
                "label": "Expected germination window ends",
                "date": _iso(start_date + timedelta(days=germination_max)),
                "offset_days": germination_max,
            },
        ]
    )

    if transplant_days > 0:
        events.append(
            {
                "event_type": "transplant",
                "label": "Estimated transplant date",
                "date": _iso(start_date + timedelta(days=transplant_days)),
                "offset_days": transplant_days,
            }
        )

    events.append(
        {
            "event_type": "harvest",
            "label": "Estimated first harvest",
            "date": _iso(start_date + timedelta(days=harvest_days)),
            "offset_days": harvest_days,
        }
    )

    warnings = []
    if fact_match.warning:
        warnings.append(fact_match.warning)
    if not fact:
        warnings.append("Timeline uses default crop timing because no local growth facts matched this plant.")
    if context_adjustments:
        warnings.extend(context_adjustments.get("warnings") or [])

    return {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "identity": identity.as_dict(),
        "start_date": _iso(start_date),
        "growth_fact_id": fact.id if fact else None,
        "growth_fact_match_level": fact_match.match_level,
        "confidence": getattr(fact, "confidence", None),
        "events": events,
        "guidance": {
            "germination_days_min": germination_min,
            "germination_days_max": germination_max,
            "germination_light": getattr(fact, "germination_light", None),
            "stratification_required": stratification_required,
            "stratification_days_min": getattr(fact, "stratification_days_min", None),
            "stratification_days_max": getattr(fact, "stratification_days_max", None),
            "sowing_depth_cm": getattr(fact, "sowing_depth_cm", None),
            "minimum_soil_temp_c": getattr(fact, "minimum_soil_temp_c", None),
            "optimum_soil_temp_c": getattr(fact, "optimum_soil_temp_c", None),
            "viable_temp_min_c": getattr(fact, "viable_temp_min_c", None),
            "viable_temp_max_c": getattr(fact, "viable_temp_max_c", None),
            "special_treatments": getattr(fact, "special_treatments", None) or [],
        },
        "source_names": getattr(fact, "source_names", None) or [],
        "source_urls": getattr(fact, "source_urls", None) or [],
        "adjustments": context_adjustments or {},
        "warnings": warnings,
    }


def save_plant_timeline_snapshot(db: Session, plant: Plant, identity: PlantIdentity) -> PlantTimelineSnapshot:
    fact_match = resolve_growth_fact(db, identity)
    timeline_data = build_plant_timeline_snapshot(plant, identity, fact_match, _context_adjustments(db, plant, fact_match.fact))

    snapshot = db.query(PlantTimelineSnapshot).filter(PlantTimelineSnapshot.plant_id == plant.id).first()
    if not snapshot:
        snapshot = PlantTimelineSnapshot(user_id=plant.user_id, plant_id=plant.id)
        db.add(snapshot)

    snapshot.user_id = plant.user_id
    snapshot.growth_fact_id = fact_match.fact.id if fact_match.fact else None
    snapshot.snapshot_date = plant.planting_date or date.today()
    snapshot.basis = fact_match.match_level if fact_match.fact else "default_timeline"
    snapshot.timeline_data = timeline_data
    db.flush()
    return snapshot
