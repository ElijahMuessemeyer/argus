"""Screener-related Pydantic models."""

from enum import Enum

from pydantic import BaseModel, Field


class MAFilter(str, Enum):
    """Moving average filter options."""

    MA_20W = "20W"
    MA_50W = "50W"
    MA_100W = "100W"
    MA_200W = "200W"


class SortField(str, Enum):
    """Screener sort field options."""

    SYMBOL = "symbol"
    NAME = "name"
    PRICE = "price"
    DISTANCE = "distance"
    MARKET_CAP = "market_cap"
    CHANGE = "change"


class SortOrder(str, Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class ScreenerRequest(BaseModel):
    """Screener filter request."""

    ma_filter: MAFilter = MAFilter.MA_20W
    distance_pct: float = Field(default=5.0, ge=0, le=100)
    include_below: bool = True
    include_above: bool = True
    sort_by: SortField = SortField.DISTANCE
    sort_order: SortOrder = SortOrder.ASC
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class ScreenerResult(BaseModel):
    """Single screener result row."""

    symbol: str
    name: str
    sector: str | None = None
    price: float
    change: float
    change_percent: float
    market_cap: int | None = None
    ma_value: float
    ma_period: str
    distance: float  # Actual distance (can be negative)
    distance_percent: float
    position: str  # "above", "below", or "at"


class ScreenerResponse(BaseModel):
    """Screener API response."""

    results: list[ScreenerResult]
    total: int
    filters: ScreenerRequest
    cached: bool = False
    cache_timestamp: str | None = None
