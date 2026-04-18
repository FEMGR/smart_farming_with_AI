"""
Core configuration module.

Key Point:
Centralizes all application settings and environment variables.

Responsibilities:
- Load environment variables from .env file
- Store database configuration
- Store security settings (JWT)
- Store external API keys
- Provide a single source of truth for application settings

Architecture Role:
- System-level configuration provider
- Ensures consistency and scalability across all layers

Layer Interaction:
- Used by: Core modules, Services, Database layer
- Communicates with: Environment variables (.env)

Data Flow:
Application starts
        ↓
Environment variables loaded from .env
        ↓
Configuration values initialized
        ↓
Other modules import config values
        ↓
System operates using centralized settings

Notes:
- Sensitive values (e.g., SECRET_KEY, DATABASE_URL) must be stored securely
- Missing critical variables will raise errors at startup
- Supports environment-based configuration (development vs production)
"""

#app.core.config.py


import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")


# --------------------------------------------------
# JWT SECURITY CONFIGURATION
# --------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in .env file")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
)


# --------------------------------------------------
# EXTERNAL API CONFIGURATION
# --------------------------------------------------

PERENUAL_API_KEY = os.getenv("PERENUAL_API_KEY", "")
TREFLE_API_KEY = os.getenv("TREFLE_API_KEY", "")


# --------------------------------------------------
# APPLICATION SETTINGS
# --------------------------------------------------

DEBUG = os.getenv("DEBUG", "True") == "True"

APP_NAME = os.getenv(
    "APP_NAME",
    "Smart Urban Farming System"
)

API_VERSION = os.getenv("API_VERSION", "v1")


# --------------------------------------------------
# CONFIG SUMMARY
# --------------------------------------------------

if DEBUG:
    print("Configuration Loaded")
    print("Database: Connected")
    print("Debug Mode:", DEBUG)
    print("App:", APP_NAME)
