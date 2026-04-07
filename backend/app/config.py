"""
config.py

This file centralizes all configuration settings for the Smart Urban Farming system to
make the project easier to maintain, secure, and support scalability.


Purpose:
- Store database connection settings
- Store API keys
- Store environment configuration
- Provide a single source of truth for system settings

"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This reads variables like DATABASE_URL and PERENUAL_API_KEY
load_dotenv()


# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

# DATABASE_URL is read from the .env file
# If it does not exist, a default local PostgreSQL connection is used
# Format:
# postgresql://username:password@host:port/database

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:SmartFarm2026Secure@localhost:5432/smart_farming" #default
)


# --------------------------------------------------
# EXTERNAL API CONFIGURATION
# --------------------------------------------------

# API key for Perenual plant database
# Used later in plant search and plant data integration
PERENUAL_API_KEY = os.getenv("PERENUAL_API_KEY", "")


# --------------------------------------------------
# APPLICATION SETTINGS
# --------------------------------------------------

# Debug mode
# True = development mode
# False = production mode
DEBUG = os.getenv("DEBUG", "True") == "True"


# --------------------------------------------------
# OPTIONAL FUTURE SETTINGS
# --------------------------------------------------

# Trefle API key (future integration)
TREFLE_API_KEY = os.getenv("TREFLE_API_KEY", "")

# App name
APP_NAME = "Smart Urban Farming System"

# API version
API_VERSION = "v1"


# --------------------------------------------------
# CONFIG SUMMARY (for debugging)
# --------------------------------------------------

# This helps verify that config is loaded correctly
if DEBUG:
    print("Configuration Loaded")
    print("Database:", DATABASE_URL)
    print("Debug Mode:", DEBUG)
