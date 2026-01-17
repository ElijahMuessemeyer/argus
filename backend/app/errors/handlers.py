"""Exception handlers for FastAPI."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors.exceptions import ArgusError
from app.utils.logging import get_logger

logger = get_logger("errors")


async def argus_exception_handler(request: Request, exc: ArgusError) -> JSONResponse:
    """Handle Argus custom exceptions."""
    logger.error(
        exc.message,
        extra={
            "extra_data": {
                "error_type": type(exc).__name__,
                "details": exc.details,
                "path": str(request.url),
                "method": request.method,
            }
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception(
        f"Unexpected error: {exc}",
        extra={
            "extra_data": {
                "path": str(request.url),
                "method": request.method,
            }
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {},
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers with the app."""
    app.add_exception_handler(ArgusError, argus_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
