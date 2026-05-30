import pytest
from fastapi import HTTPException

from app.models.location import Location
from app.models.user import User
from app.schemas.location_schema import LocationUpdate
from app.schemas.planning_schema import FarmSectionCreate, FarmSectionUpdate
from app.services.location_service import delete_location, update_location
from app.services.planning.planning_service import create_farm_section, delete_farm_section, update_farm_section


def _create_user(db):
    user = User(email="section-user@example.com", password_hash="test")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_location(db, user_id, width_m=5, length_m=4):
    location = Location(
        user_id=user_id,
        name="Backyard",
        description="Test growing area",
        environment_type="outdoor",
        width_m=width_m,
        length_m=length_m,
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def test_create_section_requires_existing_sized_location(db):
    user = _create_user(db)
    data = FarmSectionCreate(
        location_id=999999,
        name="Section A",
        section_type="production",
        width_m=2,
        length_m=2,
    )

    with pytest.raises(HTTPException) as exc:
        create_farm_section(db, data, user.id)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Location not found or not owned by user"


def test_create_section_rejects_dimensions_larger_than_location(db):
    user = _create_user(db)
    location = _create_location(db, user.id, width_m=3, length_m=3)
    data = FarmSectionCreate(
        location_id=location.id,
        name="Oversized Section",
        section_type="production",
        width_m=4,
        length_m=2,
    )

    with pytest.raises(HTTPException) as exc:
        create_farm_section(db, data, user.id)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Section dimensions cannot be larger than the location dimensions"


def test_create_sections_cannot_exceed_location_total_area(db):
    user = _create_user(db)
    location = _create_location(db, user.id, width_m=4, length_m=4)

    first = FarmSectionCreate(
        location_id=location.id,
        name="Section A",
        section_type="production",
        width_m=3,
        length_m=3,
    )
    create_farm_section(db, first, user.id)

    second = FarmSectionCreate(
        location_id=location.id,
        name="Section B",
        section_type="production",
        width_m=3,
        length_m=3,
    )

    with pytest.raises(HTTPException) as exc:
        create_farm_section(db, second, user.id)

    assert exc.value.status_code == 400
    assert "remaining location capacity" in exc.value.detail


def test_update_section_revalidates_location_capacity(db):
    user = _create_user(db)
    location = _create_location(db, user.id, width_m=4, length_m=4)
    first = create_farm_section(
        db,
        FarmSectionCreate(
            location_id=location.id,
            name="Section A",
            section_type="production",
            width_m=3,
            length_m=3,
        ),
        user.id,
    )
    create_farm_section(
        db,
        FarmSectionCreate(
            location_id=location.id,
            name="Section B",
            section_type="production",
            width_m=2,
            length_m=2,
        ),
        user.id,
    )

    with pytest.raises(HTTPException) as exc:
        update_farm_section(
            db,
            first.id,
            FarmSectionUpdate(width_m=4, length_m=4),
            user.id,
        )

    assert exc.value.status_code == 400
    assert "remaining location capacity" in exc.value.detail


def test_delete_section_marks_section_inactive(db):
    user = _create_user(db)
    location = _create_location(db, user.id)
    section = create_farm_section(
        db,
        FarmSectionCreate(
            location_id=location.id,
            name="Section A",
            section_type="production",
            width_m=2,
            length_m=2,
        ),
        user.id,
    )

    assert delete_farm_section(db, section.id, user.id) is True

    db.refresh(section)
    assert section.is_active is False


def test_location_cannot_shrink_below_active_sections(db):
    user = _create_user(db)
    location = _create_location(db, user.id, width_m=5, length_m=5)
    create_farm_section(
        db,
        FarmSectionCreate(
            location_id=location.id,
            name="Section A",
            section_type="production",
            width_m=4,
            length_m=2,
        ),
        user.id,
    )

    with pytest.raises(HTTPException) as exc:
        update_location(db, location.id, LocationUpdate(width_m=3), user.id)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Location dimensions cannot be smaller than an existing active section"


def test_location_cannot_delete_with_active_sections(db):
    user = _create_user(db)
    location = _create_location(db, user.id)
    create_farm_section(
        db,
        FarmSectionCreate(
            location_id=location.id,
            name="Section A",
            section_type="production",
            width_m=2,
            length_m=2,
        ),
        user.id,
    )

    with pytest.raises(HTTPException) as exc:
        delete_location(db, location.id, user.id)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Cannot delete location with existing farm sections"
