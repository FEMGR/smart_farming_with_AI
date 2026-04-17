"""
Custom application exceptions.
Used to standardize error handling across services.
"""


class NotFoundError(Exception):
    """Raised when a resource is not found."""
    pass


class PermissionDeniedError(Exception):
    """Raised when user is not allowed to access resource."""
    pass
