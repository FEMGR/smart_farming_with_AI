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

# Central list of allowed plant types
PLANT_TYPES = ["fruit", "vegetable", "flower", "herb", "evergreen", "succulent"]

# Default values
DEFAULT_PLANT_TYPE = "vegetable"
DEFAULT_WATERING_INTERVAL = 4
