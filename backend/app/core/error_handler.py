"""
Centralized error handling + logging for the application.
"""

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
    logger.error(f"Unexpected error: {str(exc)}")

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
