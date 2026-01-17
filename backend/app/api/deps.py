"""Dependency injection for API endpoints."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.services.cache import CacheService, cache_service
from app.services.market_data import MarketDataService, market_data_service


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_cache() -> CacheService:
    """Get cache service dependency."""
    return cache_service


async def get_market_data() -> MarketDataService:
    """Get market data service dependency."""
    return market_data_service
