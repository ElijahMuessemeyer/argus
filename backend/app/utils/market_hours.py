"""Market hours detection utilities."""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

# US Eastern timezone
ET = ZoneInfo("America/New_York")

# Market hours (9:30 AM - 4:00 PM ET)
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)

# Trading days (Monday=0, Friday=4)
TRADING_DAYS = {0, 1, 2, 3, 4}


def get_eastern_now() -> datetime:
    """Get current time in Eastern timezone."""
    return datetime.now(ET)


def is_trading_day(dt: datetime | None = None) -> bool:
    """Check if given datetime is a trading day (Mon-Fri)."""
    if dt is None:
        dt = get_eastern_now()
    return dt.weekday() in TRADING_DAYS


def is_market_hours(dt: datetime | None = None) -> bool:
    """Check if market is currently open."""
    if dt is None:
        dt = get_eastern_now()

    if not is_trading_day(dt):
        return False

    current_time = dt.time()
    return MARKET_OPEN <= current_time <= MARKET_CLOSE


def get_next_market_open(dt: datetime | None = None) -> datetime:
    """Get the next market open time."""
    if dt is None:
        dt = get_eastern_now()

    # If it's a trading day and before market open, return today's open
    if is_trading_day(dt) and dt.time() < MARKET_OPEN:
        return dt.replace(hour=9, minute=30, second=0, microsecond=0)

    # Find next trading day
    next_day = dt.replace(hour=9, minute=30, second=0, microsecond=0)
    while True:
        next_day = next_day + timedelta(days=1)
        if is_trading_day(next_day):
            return next_day


def get_cache_ttl_multiplier() -> int:
    """Get cache TTL multiplier based on market hours."""
    from app.config import get_settings

    settings = get_settings()
    if is_market_hours():
        return 1
    return settings.cache_ttl_off_hours_multiplier


def seconds_until_market_open() -> int | None:
    """Get seconds until market opens, or None if market is open."""
    if is_market_hours():
        return None

    now = get_eastern_now()
    next_open = get_next_market_open(now)
    return int((next_open - now).total_seconds())
