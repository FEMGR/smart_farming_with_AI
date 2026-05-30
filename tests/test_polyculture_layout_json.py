import json
from datetime import date
from decimal import Decimal

from app.models.production.crop_plan_group import CropPlanGroup
from app.models.production.crop_plan import CropPlan
from app.models.production.production_batch import ProductionBatch
from app.services.planning import polyculture_planner
from app.services.planning.polyculture_planner import _build_layout_json, _recommended_additions, _remaining_plant_slots


def test_build_layout_json_groups_placements_by_group_and_section():
    groups = [
        {
            "group_id": 1,
            "section_id": 10,
            "section_name": "Section A",
        },
        {
            "group_id": 2,
            "section_id": 20,
            "section_name": "Section B",
        },
    ]
    layout = {
        "grid_width": 10,
        "grid_height": 10,
        "sections": [
            {"section_id": 10, "section_name": "Section A", "grid_width": 2, "grid_height": 3},
            {"section_id": 20, "section_name": "Section B", "grid_width": 4, "grid_height": 5},
        ],
        "placements": [
            {
                "plant_id": 1,
                "name": "Tomato",
                "group_id": 1,
                "section_id": 10,
                "x": 0,
                "y": 0,
                "section_width_m": Decimal("2.50"),
            },
            {
                "plant_id": 2,
                "name": "Basil",
                "group_id": 2,
                "section_id": 20,
                "x": 1,
                "y": 0,
            },
        ],
        "warnings": ["Group 1 has 3 crop(s), but section Section A only has 2 layout cell(s)."],
    }

    layout_json = _build_layout_json(groups, layout)

    assert layout_json["groups"][0]["section_id"] == 10
    assert layout_json["groups"][0]["grid_width"] == 2
    assert layout_json["groups"][0]["placements"] == [
        {
            "plant_id": 1,
            "name": "Tomato",
            "group_id": 1,
            "section_id": 10,
            "x": 0,
            "y": 0,
            "section_width_m": 2.5,
        }
    ]
    assert layout_json["groups"][1]["placements"][0]["name"] == "Basil"
    json.dumps(layout_json)


def test_recommended_additions_respect_remaining_group_slots():
    companions = [
        {"plant": "Basil"},
        {"plant": "Nasturtium"},
        {"plant": "Marigold"},
    ]

    remaining_slots = _remaining_plant_slots(["Tomato", "Carrot"], plant_variations_per_group=4)

    assert remaining_slots == 2
    assert _recommended_additions(companions, remaining_slots) == companions[:2]
    assert _recommended_additions(companions, 0) == []
    assert _recommended_additions(companions, None) == companions


class _FakeDb:
    def __init__(self):
        self.items = []
        self.next_id = 1

    def add(self, item):
        self.items.append(item)

    def flush(self):
        for item in self.items:
            if getattr(item, "id", None) is None:
                item.id = self.next_id
                self.next_id += 1

    def commit(self):
        pass

    def refresh(self, _item):
        pass


class _FakeQuery:
    def __init__(self, result):
        self.result = result

    def filter(self, *_filters):
        return self

    def first(self):
        return self.result


class _FakeDeleteDb(_FakeDb):
    def __init__(self, result):
        super().__init__()
        self.result = result
        self.deleted_item = None

    def query(self, _model):
        return _FakeQuery(self.result)

    def delete(self, item):
        self.deleted_item = item


def test_confirm_polyculture_plan_saves_group_layout_json(monkeypatch):
    preview = {
        "groups": [
            {
                "group_id": 1,
                "section_id": 10,
                "main_crops": ["Tomato", "Basil"],
                "suggested_companions": [],
                "warnings": [],
                "allocated_area_m2": Decimal("4.00"),
                "layout": {
                    "group_id": 1,
                    "section_id": 10,
                    "section_name": "Section A",
                    "grid_width": 2,
                    "grid_height": 2,
                    "placements": [{"plant_id": 1, "name": "Tomato", "group_id": 1, "section_id": 10, "x": 0, "y": 0}],
                    "warnings": [],
                },
                "timeline": [
                    {
                        "batch_number": 1,
                        "seed_start_date": date(2026, 6, 1),
                        "expected_germination_date": date(2026, 6, 8),
                        "expected_transplant_date": date(2026, 6, 15),
                        "expected_harvest_date": date(2026, 7, 15),
                    }
                ],
            }
        ]
    }
    monkeypatch.setattr(polyculture_planner, "generate_polyculture_preview", lambda **_kwargs: preview)

    db = _FakeDb()
    polyculture_planner.confirm_polyculture_plan(
        db=db,
        user_id=1,
        location_id=5,
        section_ids=[10],
        intended_crops=["Tomato", "Basil"],
        start_date=date(2026, 6, 1),
        harvest_interval_days=14,
    )

    saved_group = next(item for item in db.items if isinstance(item, CropPlanGroup))

    assert saved_group.section_id == 10
    assert saved_group.layout_json == preview["groups"][0]["layout"]


def test_plan_to_dict_includes_saved_group_layout_and_batches():
    plan = CropPlan(
        id=1,
        user_id=1,
        location_id=5,
        name="Saved Plan",
        plan_type="polyculture",
        planned_start_date=date(2026, 6, 1),
        desired_harvest_interval_days=14,
        status="active",
    )
    group = CropPlanGroup(
        id=2,
        user_id=1,
        crop_plan_id=1,
        section_id=10,
        group_number=1,
        group_name="Group 1",
        main_crops=["Tomato"],
        suggested_companions=[],
        layout_json={"group_id": 1, "section_id": 10, "placements": [{"plant_id": 1, "name": "Tomato"}]},
        warnings=[],
    )
    batch = ProductionBatch(
        id=3,
        user_id=1,
        crop_plan_id=1,
        crop_plan_group_id=2,
        section_id=10,
        batch_number=1,
        seed_start_date=date(2026, 6, 1),
        status="planned",
    )

    plan.groups = [group]
    group.batches = [batch]

    result = polyculture_planner._plan_to_dict(plan)

    assert result["groups"][0]["layout"] == group.layout_json
    assert result["groups"][0]["batches"][0]["batch_number"] == 1


def test_delete_saved_polyculture_plan_deletes_owned_plan():
    plan = CropPlan(id=1, user_id=1, plan_type="polyculture", planned_start_date=date(2026, 6, 1))
    db = _FakeDeleteDb(plan)

    deleted = polyculture_planner.delete_saved_polyculture_plan(db, user_id=1, crop_plan_id=1)

    assert deleted is True
    assert db.deleted_item is plan


def test_delete_saved_polyculture_plan_returns_false_when_missing():
    db = _FakeDeleteDb(None)

    deleted = polyculture_planner.delete_saved_polyculture_plan(db, user_id=1, crop_plan_id=999)

    assert deleted is False
    assert db.deleted_item is None
