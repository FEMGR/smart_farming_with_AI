"""
Service layer for managing file-system based snapshots of species data.

Key Point:
Provides a simple, file-system based caching mechanism for raw API responses
to reduce redundant external API calls and improve response times.

Responsibilities:
- Save raw species data (from external APIs) to local JSON files.
- Load cached species data from local JSON files.
- Implement logic for snapshot expiration based on a maximum age.
- Manage the total number of snapshot files to prevent excessive disk usage.

Architecture Role:
- Acts as a persistent, short-term cache for the `perenual_service`.
- Shields the `perenual_service` from direct file system interaction details for caching.

Layer Interaction:
- Communicates with: Local file system.
- Used by: `perenual_service` to store and retrieve API responses.

Data Flow:
`perenual_service` requests species data
        ↓
Checks for existing snapshot
        ↓
If snapshot exists and is valid, data is loaded from file system
        ↓
If no valid snapshot, `perenual_service` calls external API
        ↓
API response is saved as a new snapshot by this service
        ↓
Data returned to `perenual_service`
"""

# app/services/species_snapshot_service.py
import json
import time
from app.core.logger import setup_logger
from app.core.constants import SNAPSHOT_DIR, SNAPSHOT_MAX_AGE_HOURS, MAX_SNAPSHOT_FILES  # Import constants
from pathlib import Path

# app/services/species_snapshot_service.py
import json
import time
from pathlib import Path

from app.core.constants import SNAPSHOT_DIR, SNAPSHOT_MAX_AGE_HOURS, MAX_SNAPSHOT_FILES  # Import constants
from app.core.logger import setup_logger

logger = setup_logger()
# The directory where species snapshots will be stored. Created if it doesn't exist.
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================
# UTILITY FUNCTIONS
# =====================================


def get_snapshot_path(species_id: int) -> Path:
    """
    Constructs the absolute file path for a given species snapshot.
    Args:species_id: The unique identifier of the species.
    Returns:A Path object representing the snapshot file's location.
    """
    return SNAPSHOT_DIR / f"{species_id}.json"


# =====================================
# SNAPSHOT MANAGEMENT
# =====================================


def save_species_snapshot(species_id: int, data: dict):
    """
    Saves the provided species data as a JSON snapshot file.
    Before saving, it triggers a cleanup of old snapshots to manage disk space.
    Args:species_id amd data: The dictionary containing the species data to be saved.
    """
    try:
        cleanup_old_snapshots()

        path = get_snapshot_path(species_id)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"[SNAPSHOT] Saved species snapshot for ID: {species_id}")

    except Exception as e:
        logger.error(f"[SNAPSHOT] Failed to save species snapshot for ID {species_id}: {e}")


def load_species_snapshot(species_id: int):
    """
    Loads species data from a snapshot file if it exists and is not expired.
    If the snapshot is expired, it is deleted.
    Args:species_id: The unique identifier of the species.
    Returns:The loaded species data as a dictionary if valid, otherwise None.
    """
    try:
        path = get_snapshot_path(species_id)

        if not path.exists():
            logger.debug(f"[SNAPSHOT] No snapshot found for ID: {species_id}")
            return None

        file_age = time.time() - path.stat().st_mtime

        # =====================================
        # EXPIRED SNAPSHOT
        # =====================================

        if file_age > (SNAPSHOT_MAX_AGE_HOURS * 3600):
            logger.info(f"[SNAPSHOT] Expired snapshot for ID {species_id}. Deleting.")
            path.unlink(missing_ok=True)
            return None

        with open(path, "r", encoding="utf-8") as f:
            logger.info(f"[SNAPSHOT] Loaded species snapshot for ID: {species_id}")
            return json.load(f)

    except Exception as e:
        logger.error(f"[SNAPSHOT] Failed to load species snapshot for ID {species_id}: {e}")
        return None


def cleanup_old_snapshots():
    """
    Cleans up old and excessive snapshot files.
    Removes snapshots that exceed `MAX_SNAPSHOT_FILES` by deleting the oldest ones.
    This function is called before saving new snapshots.
    """
    try:
        files = sorted(SNAPSHOT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)

        # =====================================
        # REMOVE OLDEST FILES IF LIMIT EXCEEDED
        # =====================================

        while len(files) > MAX_SNAPSHOT_FILES:
            oldest = files.pop(0)
            logger.info(f"[SNAPSHOT] Removing oldest snapshot due to limit: {oldest.name}")
            oldest.unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"[SNAPSHOT] Cleanup failed: {e}")
