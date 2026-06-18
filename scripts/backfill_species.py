import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database.db import SessionLocal  # noqa: E402
from backend.app.models.plant import Plant  # noqa: E402
from backend.app.services.plant_service import resolve_species  # noqa: E402


def backfill_species():
    db = SessionLocal()

    try:
        plants = db.query(Plant).filter(Plant.species_id.is_(None)).all()

        print(f"Found {len(plants)} plants to backfill")

        for plant in plants:
            print(f"Processing: {plant.name}")

            # Use resolve_species directly, which handles searching, matching, and caching
            species_internal_id = resolve_species(db, plant.name, plant_type=plant.plant_type)

            if not species_internal_id:
                print(f"  ❌ No confident match or failed to resolve species for '{plant.name}'")
                continue

            plant.species_id = species_internal_id

            print(f"  ✅ Linked '{plant.name}' to species_id={species_internal_id}")

        db.commit()
        print("🎉 Backfill complete")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during backfill: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    backfill_species()
