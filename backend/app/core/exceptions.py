"""
Core exceptions module.

Key Point:
Defines custom application-level exceptions for consistent error handling.

Responsibilities:
- Provide reusable exception classes
- Standardize error signaling across services
- Improve clarity and maintainability of error handling

Architecture Role:
- Acts as a shared error definition layer
- Enables separation between business logic and HTTP error responses

Layer Interaction:
- Used by: Services, Core modules
- Handled by: Error Handler (error_handler.py)

Data Flow:
Service detects error condition (e.g., resource not found)
        ↓
Custom exception raised (e.g., NotFoundError)
        ↓
Error handler catches exception
        ↓
Converted into HTTP response
        ↓
Returned to client

Notes:
- Keeps services independent of HTTP-specific logic
- Promotes consistent error responses across the system
"""


#app.core.exceptions.py

class NotFoundError(Exception):
    """Raised when a resource is not found."""
    pass

class PermissionDeniedError(Exception):
    """Raised when user is not allowed to access resource."""
    pass
