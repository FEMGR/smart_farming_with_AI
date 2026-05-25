"""
Frontend configuration settings for the Streamlit application.

Key Point:
Centralizes configuration variables, such as the backend API URL and predefined lists
used for UI elements (e.g., select boxes).

Responsibilities:
- Define the base URL for the FastAPI backend, allowing for environment-specific overrides.
- Provide static lists for plant types and environment types to ensure consistency across the UI.

Architecture Role:
- Acts as a single source of truth for application-wide configuration.
- Decouples hardcoded values from the application logic, making it easier to manage and update.

Layer Interaction:
- Communicates with: Environment variables (`os.getenv`), various frontend components
  that require configuration data.
- Called by: Any part of the frontend application that needs to access these settings.

Data Flow:
Application startup
        ↓
`config.py` loaded
        ↓
`API_BASE_URL` determined from environment variable or default
        ↓
`PLANT_TYPES` and `ENVIRONMENT_TYPES` lists are defined
        ↓
Frontend components access these variables as needed (e.g., to populate dropdowns)
"""

# frontend/config.py

import os

# ===============================
# API CONFIGURATION
# ===============================

API_BASE_URL = os.getenv("SMART_FARMING_API_URL", "http://127.0.0.1:8000").rstrip("/")
PLANT_TYPES = ["vegetable", "fruit", "flower", "herb", "evergreen", "succulent", "spice", "onion"]
ENVIRONMENT_TYPES = ["outdoor", "indoor", "greenhouse"]
