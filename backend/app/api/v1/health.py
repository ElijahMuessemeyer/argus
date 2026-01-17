"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import get_settings, Settings
from app.services.cache import CacheService, get_cache
from app.utils.market_hours import is_market_hours

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str
    timestamp: str
    market_open: bool
    redis_connected: bool


@router.get("/health", response_model=HealthResponse)
async def health_check(
    cache: CacheService = Depends(get_cache),
) -> HealthResponse:
    """Check application health status."""
    settings = get_settings()

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.utcnow().isoformat(),
        market_open=is_market_hours(),
        redis_connected=cache.is_connected,
    )
