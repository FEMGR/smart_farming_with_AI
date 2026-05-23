from types import SimpleNamespace

from app.services.grouping_service import generate_groups_internal
from app.services.positioning_service import generate_layout


def _layout_plant(
    plant_id,
    name,
    group_id=None,
    bed_x=None,
    bed_y=None,
    location_width_m=None,
    location_length_m=None,
):
    return {
        "id": plant_id,
        "name": name,
        "group_id": group_id,
        "bed_x": bed_x,
        "bed_y": bed_y,
        "sunlight": "full_sun",
        "watering": "medium",
        "watering_interval_days": 3,
        "soil": "well_drained",
        "max_height_ft": 2,
        "max_width_ft": 1,
        "location_width_m": location_width_m,
        "location_length_m": location_length_m,
    }


def _model_plant(
    plant_id,
    name,
    group_id=None,
    bed_x=None,
    bed_y=None,
    location_width_m=None,
    location_length_m=None,
):
    species = SimpleNamespace(
        common_name=name,
        scientific_name=name,
        sunlight_requirement="full_sun",
        watering="medium",
        recommended_soil="well_drained",
        max_height_ft=2,
        max_width_ft=1,
    )
    location = SimpleNamespace(width_m=location_width_m, length_m=location_length_m)

    return SimpleNamespace(
        id=plant_id,
        name=name,
        plant_type="vegetable",
        species=species,
        species_id=plant_id * 100,
        group_id=group_id,
        bed_x=bed_x,
        bed_y=bed_y,
        watering_interval_days=3,
        location_id=1,
        location=location,
    )


def test_generate_layout_reserves_saved_positions_before_generated_positions():
    groups = [
        {
            "group_id": 1,
            "plants": [
                _layout_plant(1, "Garlic"),
            ],
        },
        {
            "group_id": 2,
            "plants": [
                _layout_plant(2, "Chive", group_id=2, bed_x=0, bed_y=0),
            ],
        },
    ]

    layout = generate_layout(groups, recommended_pairs=[], avoid_pairs=[], grid_width=3, grid_height=3)
    placements = {placement["plant_id"]: placement for placement in layout["placements"]}

    assert layout["warnings"] == []
    assert placements[2]["name"] == "Chive"
    assert placements[2]["saved_position"] is True
    assert (placements[2]["x"], placements[2]["y"]) == (0, 0)
    assert (placements[1]["x"], placements[1]["y"]) != (0, 0)


def test_generate_layout_uses_saved_plant_group_id_for_saved_position():
    groups = [
        {
            "group_id": 1,
            "plants": [
                _layout_plant(1, "Asparagus", group_id=3, bed_x=2, bed_y=1),
            ],
        }
    ]

    layout = generate_layout(groups, recommended_pairs=[], avoid_pairs=[], grid_width=4, grid_height=4)
    asparagus = layout["placements"][0]

    assert asparagus["plant_id"] == 1
    assert asparagus["group_id"] == 3
    assert asparagus["saved_position"] is True
    assert (asparagus["x"], asparagus["y"]) == (2, 1)


def test_generate_groups_internal_includes_saved_layout_fields():
    plants = [
        _model_plant(1, "Tomato", group_id=2, bed_x=4, bed_y=1, location_width_m=5, location_length_m=3),
        _model_plant(2, "Basil"),
    ]

    groups = generate_groups_internal(plants, valid_pairs=["tomato-basil"], avoid_pairs=[])
    tomato = next(plant for group in groups for plant in group["plants"] if plant["name"] == "Tomato")

    assert tomato["group_id"] == 2
    assert tomato["bed_x"] == 4
    assert tomato["bed_y"] == 1
    assert tomato["location_width_m"] == 5.0
    assert tomato["location_length_m"] == 3.0
