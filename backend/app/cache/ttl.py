"""Cache TTL configuration."""

from app.config import get_settings
from app.utils.market_hours import is_market_hours


class CacheTTL:
    """Cache TTL utilities with market hours awareness."""

    @classmethod
    def _get_multiplier(cls) -> int:
        """Get TTL multiplier based on market hours."""
        settings = get_settings()
        if is_market_hours():
            return 1
        return settings.cache_ttl_off_hours_multiplier

    @classmethod
    def quote(cls) -> int:
        """TTL for stock quotes."""
        settings = get_settings()
        return settings.cache_ttl_quote * cls._get_multiplier()

    @classmethod
    def ohlcv_daily(cls) -> int:
        """TTL for daily OHLCV data."""
        settings = get_settings()
        return settings.cache_ttl_ohlcv_daily

    @classmethod
    def ohlcv_weekly(cls) -> int:
        """TTL for weekly OHLCV data."""
        settings = get_settings()
        return settings.cache_ttl_ohlcv_weekly

    @classmethod
    def indicators(cls) -> int:
        """TTL for indicator data."""
        settings = get_settings()
        return settings.cache_ttl_indicators * cls._get_multiplier()

    @classmethod
    def screener(cls) -> int:
        """TTL for screener results."""
        settings = get_settings()
        return settings.cache_ttl_screener * cls._get_multiplier()

    @classmethod
    def universe(cls) -> int:
        """TTL for stock universe."""
        settings = get_settings()
        return settings.cache_ttl_universe

    @classmethod
    def stock_info(cls) -> int:
        """TTL for stock info."""
        return 86400  # 24 hours

    @classmethod
    def search(cls) -> int:
        """TTL for search results."""
        return 3600  # 1 hour
