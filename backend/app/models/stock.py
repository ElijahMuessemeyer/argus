"""Stock-related Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TimeFrame(str, Enum):
    """Chart timeframe options."""

    DAILY = "1D"
    WEEKLY = "1W"


class Period(str, Enum):
    """Historical data period options."""

    THREE_MONTHS = "3M"
    SIX_MONTHS = "6M"
    ONE_YEAR = "1Y"
    TWO_YEARS = "2Y"
    FIVE_YEARS = "5Y"


class OHLCV(BaseModel):
    """Open-High-Low-Close-Volume data point."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class Quote(BaseModel):
    """Real-time stock quote."""

    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    avg_volume: int | None = None
    market_cap: int | None = None
    high_52w: float | None = None
    low_52w: float | None = None
    updated_at: datetime


class StockInfo(BaseModel):
    """Basic stock information."""

    symbol: str
    name: str
    sector: str | None = None
    industry: str | None = None
    exchange: str | None = None
    market_cap: int | None = None
    currency: str = "USD"


class StockData(BaseModel):
    """Complete stock data response."""

    info: StockInfo
    quote: Quote
    ohlcv: list[OHLCV]


class ChartData(BaseModel):
    """Chart data with OHLCV and indicators."""

    symbol: str
    timeframe: TimeFrame
    period: Period
    ohlcv: list[OHLCV]
    indicators: dict[str, Any] = Field(default_factory=dict)
