# app/scripts/backfill_species.py

from app.database.db import SessionLocal
from app.models.plant import Plant
from app.services.plant_service import (
    get_or_create_species_cache,
    search_species
)
from app.utils.species_matching import select_best_match


def backfill_species():
    db = SessionLocal()

    try:
        plants = db.query(Plant).filter(Plant.species_id == None).all()

        print(f"Found {len(plants)} plants to backfill")

        for plant in plants:
            print(f"Processing: {plant.name}")

            results = search_species(plant.name)

            best_match = select_best_match(plant.name, results)

            if not best_match:
                print("  ❌ No confident match")
                continue

            species_id = best_match["id"]

            species = get_or_create_species_cache(db, species_id)

            plant.species_id = species.id

            print(f"  ✅ Linked to species_id={species.id}")

        db.commit()
        print("🎉 Backfill complete")

    finally:
        db.close()


if __name__ == "__main__":
    backfill_species()
