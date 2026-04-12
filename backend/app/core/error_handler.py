"""
Logging

"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger("smart_farming")


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    logger.warning(f"HTTP error: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    logger.warning("Validation error occurred")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid input",
            "details": exc.errors()
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
):
    logger.error(f"Unexpected error: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error"
        }
    )
