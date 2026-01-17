"""Cache key patterns."""

import hashlib
import json
from typing import Any


class CacheKeys:
    """Cache key generation utilities."""

    PREFIX = "argus"

    @classmethod
    def quote(cls, symbol: str) -> str:
        """Cache key for stock quote."""
        return f"{cls.PREFIX}:quote:{symbol.upper()}"

    @classmethod
    def ohlcv(cls, symbol: str, timeframe: str, period: str) -> str:
        """Cache key for OHLCV data."""
        return f"{cls.PREFIX}:ohlcv:{symbol.upper()}:{timeframe}:{period}"

    @classmethod
    def indicators(cls, symbol: str, timeframe: str) -> str:
        """Cache key for indicator data."""
        return f"{cls.PREFIX}:indicators:{symbol.upper()}:{timeframe}"

    @classmethod
    def screener(cls, filters: dict[str, Any]) -> str:
        """Cache key for screener results."""
        # Create hash of filter parameters for unique key
        filters_str = json.dumps(filters, sort_keys=True)
        filters_hash = hashlib.md5(filters_str.encode()).hexdigest()[:12]
        return f"{cls.PREFIX}:screener:{filters_hash}"

    @classmethod
    def universe(cls) -> str:
        """Cache key for stock universe."""
        return f"{cls.PREFIX}:universe"

    @classmethod
    def stock_info(cls, symbol: str) -> str:
        """Cache key for stock info."""
        return f"{cls.PREFIX}:info:{symbol.upper()}"

    @classmethod
    def search(cls, query: str) -> str:
        """Cache key for search results."""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()[:12]
        return f"{cls.PREFIX}:search:{query_hash}"
