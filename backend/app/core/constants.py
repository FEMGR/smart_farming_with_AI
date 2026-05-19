"""
Core constants for application-wide configuration.

Key Point:
Defines reusable static values to ensure consistency across the system.

Responsibilities:
- Store allowed plant types for validation and classification
- Provide default values for plant attributes (e.g., watering interval)
- Centralize configuration to avoid hardcoding in multiple places

Architecture Role:
- Shared configuration layer used across services, models, and routes
- Ensures consistency and reduces duplication of static values

Layer Interaction:
- Communicates with: Services, Schemas, Models
- Used by: Validation logic, default assignments, business rules

Data Flow:
Application logic requires predefined values
        ↓
Constants referenced from central module
        ↓
Values applied in validation or default assignment
        ↓
Consistent behavior across system
"""

# app/core/constants.py
from pathlib import Path
import os

# Determine the absolute path to the project root
# This assumes constants.py is in backend/app/core/
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # smart-farming-system/

# =========================================
# PLANT TYPES
# =========================================

PLANT_TYPES = ["fruit", "vegetable", "flower", "herb", "evergreen", "succulent"]

DEFAULT_PLANT_TYPE = "vegetable"

DEFAULT_WATERING_INTERVAL = 4

# =========================================
# API SETTINGS
# =========================================

COOLDOWN_SECONDS = 7  # Cooldown between API calls for rate limiting
API_REQUEST_TIMEOUT_SECONDS = 60  # Timeout for a single API request

# =========================================
# IN-MEMORY CACHE
# =========================================

DEFAULT_TTL = 60 * 60  # 1 hour
MAX_CACHE_SIZE = 500

# =========================================
# SPECIES SNAPSHOT SETTINGS
# =========================================

SNAPSHOT_DIR = BASE_DIR / "backend" / "cache" / "species_snapshots"
SNAPSHOT_MAX_AGE_HOURS = 5
MAX_SNAPSHOT_FILES = 10

# =========================================
# SPECIES SUGGESTION CACHE SETTINGS
# =========================================

SUGGESTION_CACHE_FILE = BASE_DIR / "backend" / "temp" / "species_suggestions.json"
SUGGESTION_MAX_AGE_SECONDS = 60 * 60 * 24
MAX_SUGGESTION_ENTRIES = 15
