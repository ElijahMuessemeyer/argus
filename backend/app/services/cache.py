"""Redis cache abstraction service."""

import json
from datetime import datetime
from typing import Any, TypeVar, Callable
from collections.abc import Awaitable

import redis.asyncio as redis

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("services.cache")

T = TypeVar("T")


class CacheService:
    """Redis cache service with async support."""

    _instance: "CacheService | None" = None
    _redis: redis.Redis | None = None

    def __new__(cls) -> "CacheService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """Connect to Redis."""
        settings = get_settings()
        if not settings.redis_enabled:
            logger.info("Redis disabled, using in-memory fallback")
            return

        try:
            self._redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}, using in-memory fallback")
            self._redis = None

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._redis is not None

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self._redis:
            return None

        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL."""
        if not self._redis:
            return False

        try:
            serialized = json.dumps(value, default=self._json_serializer)
            await self._redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._redis:
            return False

        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self._redis:
            return 0

        try:
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
        ttl: int,
    ) -> tuple[T, bool]:
        """Get from cache or set using factory function.

        Returns (value, was_cached).
        """
        # Try to get from cache
        cached = await self.get(key)
        if cached is not None:
            return cached, True

        # Generate value
        value = await factory()

        # Store in cache
        await self.set(key, value, ttl)

        return value, False

    @staticmethod
    def _json_serializer(obj: Any) -> Any:
        """JSON serializer for objects not serializable by default."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# Global cache instance
cache_service = CacheService()


async def get_cache() -> CacheService:
    """Dependency for getting cache service."""
    return cache_service
