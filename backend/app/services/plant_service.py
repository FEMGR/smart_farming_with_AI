"""
Plant service layer contains business logic related to plants.
Routes --> call services--> talk to database.
"""

from sqlalchemy.orm import Session
from app.models.plant import Plant
from app.schemas.plant_schema import PlantCreate, PlantUpdate


# Create plant
def create_plant(db: Session, plant: PlantCreate):
    new_plant = Plant(
        name=plant.name,
        species=plant.species,
        location=plant.location
    )

    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return new_plant


# Get all plants
def get_all_plants(db: Session):
    return db.query(Plant).all()


# Get plant by id
def get_plant_by_id(db: Session, plant_id: int):
    return db.query(Plant).filter(Plant.id == plant_id).first()


# Update plant
def update_plant(db: Session, plant_id: int, plant_update: PlantUpdate):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()

    if not plant:
        return None

    if plant_update.name is not None:
        plant.name = plant_update.name

    if plant_update.species is not None:
        plant.species = plant_update.species

    if plant_update.location is not None:
        plant.location = plant_update.location

    db.commit()
    db.refresh(plant)

    return plant


# Delete plant
def delete_plant(db: Session, plant_id: int):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()

    if not plant:
        return False

    db.delete(plant)
    db.commit()

    return True
