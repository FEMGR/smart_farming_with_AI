"""
config.py

This file centralizes all configuration settings for the Smart Urban Farming system to
make the project easier to maintain, secure, and support scalability.

Purpose:
- Load environment variables
- Store database settings
- Store API keys
- Store security configuration
- Provide a single source of truth
"""

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
