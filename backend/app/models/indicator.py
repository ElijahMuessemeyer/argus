"""Indicator-related Pydantic models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MAType(str, Enum):
    """Moving average type."""

    SMA = "SMA"
    EMA = "EMA"


class MovingAverageResult(BaseModel):
    """Moving average calculation result."""

    period: int
    ma_type: MAType
    values: list[tuple[datetime, float | None]]  # (timestamp, value)
    current_value: float | None = None
    current_price: float | None = None
    distance_percent: float | None = None  # % distance from current price


class RSIResult(BaseModel):
    """RSI calculation result."""

    period: int
    values: list[tuple[datetime, float | None]]  # (timestamp, value)
    current_value: float | None = None
    is_overbought: bool = False
    is_oversold: bool = False


class MACDResult(BaseModel):
    """MACD calculation result."""

    fast_period: int
    slow_period: int
    signal_period: int
    macd_line: list[tuple[datetime, float | None]]
    signal_line: list[tuple[datetime, float | None]]
    histogram: list[tuple[datetime, float | None]]
    current_macd: float | None = None
    current_signal: float | None = None
    current_histogram: float | None = None


class IndicatorData(BaseModel):
    """Combined indicator data for a stock."""

    symbol: str
    ma_20w: MovingAverageResult | None = None
    ma_50w: MovingAverageResult | None = None
    ma_100w: MovingAverageResult | None = None
    ma_200w: MovingAverageResult | None = None
    rsi: RSIResult | None = None
    macd: MACDResult | None = None
