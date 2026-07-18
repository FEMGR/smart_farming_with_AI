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
import os
from pathlib import Path

# Determine the absolute path to the project root
# This assumes constants.py is in backend/app/core/
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # smart-farming-system/

# =========================================
# PLANT TYPES
# =========================================

PLANT_TYPES = ["fruit", "vegetable", "flower", "herb", "evergreen", "succulent", "spice", "onion", "berries"]

DEFAULT_PLANT_TYPE = "vegetable"

DEFAULT_WATERING_INTERVAL = 4

# =========================================
# DATA SOURCES
# =========================================

DATA_SOURCE_MANUAL = "manual"
DATA_SOURCE_PERENUAL = "perenual"
DATA_SOURCE_KNOWLEDGE_BASE = "knowledge_base"
DATA_SOURCE_IMPORT = "import"
DATA_SOURCE_SENSOR = "sensor"
DATA_SOURCE_AI = "ai"

PLANT_DATA_SOURCES = [
    DATA_SOURCE_MANUAL,
    DATA_SOURCE_PERENUAL,
    DATA_SOURCE_KNOWLEDGE_BASE,
    DATA_SOURCE_IMPORT,
    DATA_SOURCE_SENSOR,
    DATA_SOURCE_AI,
]

# =========================================
# API SETTINGS
# =========================================

COOLDOWN_SECONDS = 7  # Cooldown between API calls for rate limiting
API_REQUEST_TIMEOUT_SECONDS = 60  # Timeout for a single API request

# =========================================
# PERENUAL API SETTINGS
# =========================================

PERENUAL_BASE_URL = "https://perenual.com/api/v2"
PERENUAL_DAILY_REQUEST_LIMIT = int(os.getenv("PERENUAL_DAILY_REQUEST_LIMIT", "100"))
PERENUAL_DAILY_SOFT_LIMIT = min(int(os.getenv("PERENUAL_DAILY_SOFT_LIMIT", "90")), PERENUAL_DAILY_REQUEST_LIMIT)
PERENUAL_429_DEFAULT_BACKOFF_SECONDS = int(os.getenv("PERENUAL_429_DEFAULT_BACKOFF_SECONDS", "60"))
PERENUAL_429_MAX_BACKOFF_SECONDS = int(os.getenv("PERENUAL_429_MAX_BACKOFF_SECONDS", str(60 * 60)))
# 0 means "do not pre-block by ID"; let Perenual decide via the HTTP response.
PERENUAL_SPECIES_DETAILS_MAX_ID = int(os.getenv("PERENUAL_SPECIES_DETAILS_MAX_ID", "0"))
PERENUAL_MAX_DETAIL_FALLBACK_ATTEMPTS = 3
PERENUAL_RATE_LIMIT_STATE_FILE = BASE_DIR / "backend" / "temp" / "perenual_rate_limit.json"

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
MAX_SNAPSHOT_FILES = 500

# =========================================
# SPECIES SUGGESTION CACHE SETTINGS
# =========================================

SUGGESTION_CACHE_FILE = BASE_DIR / "backend" / "temp" / "species_suggestions.json"
SUGGESTION_MAX_AGE_SECONDS = 60 * 60 * 24
MAX_SUGGESTION_ENTRIES = 500
