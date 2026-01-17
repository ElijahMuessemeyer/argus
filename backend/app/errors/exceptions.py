"""Custom exception classes."""

from typing import Any


class ArgusError(Exception):
    """Base exception for Argus application."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        status_code: int = 500,
    ):
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(ArgusError):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            details={"resource": resource, "identifier": identifier},
            status_code=404,
        )


class ValidationError(ArgusError):
    """Input validation error."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(
            message=message,
            details={"field": field} if field else {},
            status_code=400,
        )


class MarketDataError(ArgusError):
    """Market data fetching error."""

    def __init__(self, message: str, symbol: str | None = None):
        super().__init__(
            message=message,
            details={"symbol": symbol} if symbol else {},
            status_code=503,
        )


class CacheError(ArgusError):
    """Cache operation error."""

    def __init__(self, message: str, operation: str | None = None):
        super().__init__(
            message=message,
            details={"operation": operation} if operation else {},
            status_code=500,
        )


class DatabaseError(ArgusError):
    """Database operation error."""

    def __init__(self, message: str, operation: str | None = None):
        super().__init__(
            message=message,
            details={"operation": operation} if operation else {},
            status_code=500,
        )
