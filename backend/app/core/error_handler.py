"""
Core error handling module.

Key Point:
Provides centralized exception handling and logging for the application.

Responsibilities:
- Handle application-specific exceptions (e.g., NotFoundError, PermissionDeniedError)
- Handle FastAPI and validation errors
- Provide a catch-all handler for unexpected exceptions
- Log errors consistently across the system

Architecture Role:
- Acts as the bridge between internal exceptions and HTTP responses
- Ensures services remain independent of HTTP-specific logic

Layer Interaction:
- Communicates with: Core (exceptions), Logger
- Used by: Main application (main.py) during startup
- Handles errors from: Routes, Services, Dependencies
- Does NOT depend on: Business logic, Database

Data Flow:
Exception raised in service or route
        ↓
Exception intercepted by FastAPI
        ↓
Mapped to appropriate handler
        ↓
Error logged using logger
        ↓
Converted into standardized JSON response
        ↓
Returned to client

"""

#app.core.error_handler.py
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import NotFoundError, PermissionDeniedError

logger = logging.getLogger("smart_farming")


# ===============================
# HTTP EXCEPTION (FastAPI / Starlette)
# ===============================
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP error: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# ===============================
# VALIDATION ERROR (Pydantic)
# ===============================
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error occurred")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid input",
            "details": exc.errors()
        }
    )


# ===============================
# UNEXPECTED ERROR (Catch-all)
# ===============================
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unexpected error occurred")

    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"}
    )


# ===============================
# REGISTER ALL HANDLERS
# ===============================
def add_exception_handlers(app):
    """
    Register ALL global exception handlers.
    """

    # -----------------------------
    # Custom domain errors
    # -----------------------------
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        logger.warning(f"NotFoundError: {str(exc)}")
        return JSONResponse(
            status_code=404,
            content={"error": str(exc)}
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_handler(request: Request, exc: PermissionDeniedError):
        logger.warning(f"PermissionDenied: {str(exc)}")
        return JSONResponse(
            status_code=403,
            content={"error": str(exc)}
        )

    # -----------------------------
    # FastAPI / Starlette errors
    # -----------------------------
    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler
    )

    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler
    )

    # -----------------------------
    # Catch-all fallback
    # -----------------------------
    app.add_exception_handler(
        Exception,
        general_exception_handler
    )
