"""Signals API endpoint."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.deps import get_db
from app.core.signals import SignalDetector
from app.models.signal import Signal, SignalType

router = APIRouter()


class SignalsResponse(BaseModel):
    """Signals API response."""

    signals: list[Signal]
    total: int
    filters: dict


@router.get("", response_model=SignalsResponse)
async def get_signals(
    types: Optional[str] = Query(
        default=None,
        description="Comma-separated signal types to filter"
    ),
    symbols: Optional[str] = Query(
        default=None,
        description="Comma-separated symbols to filter"
    ),
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Get signals from last N hours"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Maximum signals to return"
    ),
    db: AsyncSession = Depends(get_db),
) -> SignalsResponse:
    """Get trading signals with optional filters.

    **Parameters:**
    - **types**: Filter by signal types (comma-separated)
      - ma_crossover_bullish, ma_crossover_bearish
      - rsi_oversold, rsi_overbought
      - macd_bullish_cross, macd_bearish_cross
      - near_52w_high, near_52w_low
      - new_52w_high, new_52w_low
    - **symbols**: Filter by stock symbols (comma-separated)
    - **hours**: Get signals from last N hours (default 24)
    - **limit**: Maximum signals to return

    **Returns:**
    List of signals with type, symbol, price, and details.
    """
    # Parse types
    type_list = None
    if types:
        try:
            type_list = [SignalType(t.strip()) for t in types.split(",")]
        except ValueError:
            pass  # Invalid types are ignored

    # Parse symbols
    symbol_list = None
    if symbols:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]

    # Calculate since timestamp
    since = datetime.utcnow() - timedelta(hours=hours)

    # Get signals
    signals = await SignalDetector.get_signals(
        db,
        types=type_list,
        symbols=symbol_list,
        since=since,
        limit=limit,
    )

    return SignalsResponse(
        signals=signals,
        total=len(signals),
        filters={
            "types": [t.value for t in type_list] if type_list else None,
            "symbols": symbol_list,
            "hours": hours,
        },
    )


@router.get("/types")
async def get_signal_types() -> dict:
    """Get all available signal types with descriptions.

    **Returns:**
    Dictionary of signal types and their descriptions.
    """
    return {
        "signal_types": [
            {
                "type": SignalType.MA_CROSSOVER_BULLISH.value,
                "name": "MA Crossover Bullish",
                "description": "Price crosses above a moving average",
                "sentiment": "bullish",
            },
            {
                "type": SignalType.MA_CROSSOVER_BEARISH.value,
                "name": "MA Crossover Bearish",
                "description": "Price crosses below a moving average",
                "sentiment": "bearish",
            },
            {
                "type": SignalType.RSI_OVERSOLD.value,
                "name": "RSI Oversold",
                "description": "RSI drops below 30",
                "sentiment": "bullish",
            },
            {
                "type": SignalType.RSI_OVERBOUGHT.value,
                "name": "RSI Overbought",
                "description": "RSI rises above 70",
                "sentiment": "bearish",
            },
            {
                "type": SignalType.MACD_BULLISH_CROSS.value,
                "name": "MACD Bullish Cross",
                "description": "MACD line crosses above signal line",
                "sentiment": "bullish",
            },
            {
                "type": SignalType.MACD_BEARISH_CROSS.value,
                "name": "MACD Bearish Cross",
                "description": "MACD line crosses below signal line",
                "sentiment": "bearish",
            },
            {
                "type": SignalType.NEAR_52W_HIGH.value,
                "name": "Near 52W High",
                "description": "Within 5% of 52-week high",
                "sentiment": "neutral",
            },
            {
                "type": SignalType.NEAR_52W_LOW.value,
                "name": "Near 52W Low",
                "description": "Within 5% of 52-week low",
                "sentiment": "neutral",
            },
            {
                "type": SignalType.NEW_52W_HIGH.value,
                "name": "New 52W High",
                "description": "New 52-week high",
                "sentiment": "bullish",
            },
            {
                "type": SignalType.NEW_52W_LOW.value,
                "name": "New 52W Low",
                "description": "New 52-week low",
                "sentiment": "bearish",
            },
        ]
    }
