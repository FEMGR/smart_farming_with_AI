# app/services/lifecycle/timeline_service.py

from datetime import date, timedelta


DEFAULT_CROP_TIMELINES = {
    "lettuce": {"germination_days": 5, "transplant_days": 14, "harvest_days": 45},
    "cabbage": {"germination_days": 7, "transplant_days": 28, "harvest_days": 80},
    "tomato": {"germination_days": 7, "transplant_days": 35, "harvest_days": 90},
    "carrot": {"germination_days": 10, "transplant_days": 0, "harvest_days": 75},
    "cucumber": {"germination_days": 5, "transplant_days": 21, "harvest_days": 60},
    "potato": {"germination_days": 14, "transplant_days": 0, "harvest_days": 100},
    "asparagus": {"germination_days": 14, "transplant_days": 90, "harvest_days": 365},
}


def normalize_crop_name(name: str) -> str:
    return str(name or "").lower().strip().replace(" ", "_")


def get_crop_timeline(crop_name: str) -> dict:
    crop = normalize_crop_name(crop_name)
    return DEFAULT_CROP_TIMELINES.get(
        crop,
        {"germination_days": 7, "transplant_days": 14, "harvest_days": 60},
    )


def get_group_timeline(main_crops: list[str]) -> dict:
    """
    For a polyculture group, use the slowest crop as the group harvest timeline.
    This prevents the plan from assuming the group is ready too early.
    """
    if not main_crops:
        return {"germination_days": 7, "transplant_days": 14, "harvest_days": 60}

    timelines = [get_crop_timeline(crop) for crop in main_crops]

    return {
        "germination_days": max(t["germination_days"] for t in timelines),
        "transplant_days": max(t["transplant_days"] for t in timelines),
        "harvest_days": max(t["harvest_days"] for t in timelines),
    }


def generate_group_timeline(
    start_date: date,
    main_crops: list[str],
    harvest_interval_days: int,
    batch_count: int,
) -> list[dict]:
    timeline = get_group_timeline(main_crops)

    events = []

    for index in range(batch_count):
        batch_number = index + 1
        seed_date = start_date + timedelta(days=index * harvest_interval_days)

        germination_date = seed_date + timedelta(days=timeline["germination_days"])
        transplant_date = seed_date + timedelta(days=timeline["transplant_days"]) if timeline["transplant_days"] > 0 else None
        harvest_date = seed_date + timedelta(days=timeline["harvest_days"])

        events.append(
            {
                "batch_number": batch_number,
                "seed_start_date": seed_date,
                "expected_germination_date": germination_date,
                "expected_transplant_date": transplant_date,
                "expected_harvest_date": harvest_date,
                "timeline_basis": timeline,
            }
        )

    return events
