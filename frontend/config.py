# frontend/config.py
# Shared frontend configuration.
# - API_BASE_URL selects the FastAPI backend.
# - Lists below drive select boxes used by forms.
import os

API_BASE_URL = os.getenv("SMART_FARMING_API_URL", "http://127.0.0.1:8000").rstrip("/")
PLANT_TYPES = ["vegetable", "fruit", "flower", "herb", "evergreen", "succulent", "spice", "onion"]
ENVIRONMENT_TYPES = ["outdoor", "indoor", "greenhouse"]
