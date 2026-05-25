"""
API client for plant species lookup and suggestions in the Smart Urban Farming application.

Key Point:
Provides a function to query the backend for plant species suggestions based on a search query,
primarily used for autocomplete or search functionalities.

Responsibilities:
- Abstract the API endpoint path and HTTP method for species suggestions.
- Facilitate data exchange for searching plant species.

Architecture Role:
- Acts as a dedicated interface for the frontend to retrieve species data from the backend.
- Simplifies API calls for species lookup.

Layer Interaction:
- Communicates with: `api.client.api_request` (for underlying HTTP requests).
- Called by: Frontend components that require species search/autocomplete functionality.

Data Flow:
User types into a species search input field
        ↓
`suggest_species()` is called with the user's query
        ↓
`api_request()` sends a GET request to the backend `/species/suggest` endpoint with the query
        ↓
Backend processes the query and returns a list of matching species suggestions
        ↓
List of species suggestions is returned to the frontend UI for display
"""

# frontend/api/species.py

from typing import Any

from api.client import api_request


def suggest_species(query: str) -> list[dict[str, Any]]:
    return api_request("GET", "/species/suggest", params={"query": query}) or []
