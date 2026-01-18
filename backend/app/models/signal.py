"""Signal-related Pydantic models."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    """Types of trading signals."""

    MA_CROSSOVER_BULLISH = "ma_crossover_bullish"
    MA_CROSSOVER_BEARISH = "ma_crossover_bearish"
    RSI_OVERSOLD = "rsi_oversold"
    RSI_OVERBOUGHT = "rsi_overbought"
    MACD_BULLISH_CROSS = "macd_bullish_cross"
    MACD_BEARISH_CROSS = "macd_bearish_cross"
    NEAR_52W_HIGH = "near_52w_high"
    NEAR_52W_LOW = "near_52w_low"
    NEW_52W_HIGH = "new_52w_high"
    NEW_52W_LOW = "new_52w_low"


class SignalCreate(BaseModel):
    """Schema for creating a new signal."""

    symbol: str
    signal_type: SignalType
    price: float
    details: dict[str, Any] = Field(default_factory=dict)


class Signal(BaseModel):
    """Complete signal with metadata."""

    id: UUID = Field(default_factory=uuid4)
    symbol: str
    signal_type: SignalType
    timestamp: datetime
    price: float
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_bullish(self) -> bool:
        """Check if signal is bullish."""
        return self.signal_type in {
            SignalType.MA_CROSSOVER_BULLISH,
            SignalType.MACD_BULLISH_CROSS,
            SignalType.RSI_OVERSOLD,
            SignalType.NEAR_52W_LOW,
            SignalType.NEW_52W_HIGH,
        }

    @property
    def is_bearish(self) -> bool:
        """Check if signal is bearish."""
        return self.signal_type in {
            SignalType.MA_CROSSOVER_BEARISH,
            SignalType.MACD_BEARISH_CROSS,
            SignalType.RSI_OVERBOUGHT,
            SignalType.NEAR_52W_HIGH,
            SignalType.NEW_52W_LOW,
        }
