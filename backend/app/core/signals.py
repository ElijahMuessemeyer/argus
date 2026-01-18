"""Signal detection logic."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pandas as pd
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.indicators import IndicatorCalculator, MA_PERIOD_MAP
from app.models.signal import Signal, SignalType, SignalCreate
from app.models.db import SignalRecord
from app.models.stock import OHLCV
from app.services.market_data import market_data_service
from app.utils.logging import get_logger

logger = get_logger("core.signals")


class SignalDetector:
    """Detector for trading signals."""

    @staticmethod
    def detect_ma_crossover(
        ohlcv_list: list[OHLCV],
        ma_period: str,
        lookback: int = 2,
    ) -> SignalType | None:
        """Detect MA crossover signals.

        Args:
            ohlcv_list: OHLCV data
            ma_period: MA period (20W, 50W, etc.)
            lookback: Number of bars to check for crossover

        Returns:
            SignalType if crossover detected, None otherwise
        """
        period = MA_PERIOD_MAP.get(ma_period)
        if not period or len(ohlcv_list) < period + lookback:
            return None

        df = IndicatorCalculator.ohlcv_to_dataframe(ohlcv_list)
        ma = IndicatorCalculator.moving_average(df["close"], period)

        if ma.isna().iloc[-1] or ma.isna().iloc[-2]:
            return None

        # Check for crossover in recent bars
        for i in range(-lookback, 0):
            prev_close = df["close"].iloc[i - 1]
            curr_close = df["close"].iloc[i]
            prev_ma = ma.iloc[i - 1]
            curr_ma = ma.iloc[i]

            # Bullish crossover: price crosses above MA
            if prev_close < prev_ma and curr_close > curr_ma:
                return SignalType.MA_CROSSOVER_BULLISH

            # Bearish crossover: price crosses below MA
            if prev_close > prev_ma and curr_close < curr_ma:
                return SignalType.MA_CROSSOVER_BEARISH

        return None

    @staticmethod
    def detect_rsi_signal(
        ohlcv_list: list[OHLCV],
        oversold_threshold: float = 30,
        overbought_threshold: float = 70,
    ) -> SignalType | None:
        """Detect RSI overbought/oversold signals."""
        if len(ohlcv_list) < 15:
            return None

        df = IndicatorCalculator.ohlcv_to_dataframe(ohlcv_list)
        rsi = IndicatorCalculator.rsi(df["close"])

        if rsi.isna().iloc[-1]:
            return None

        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2] if not rsi.isna().iloc[-2] else current_rsi

        # Detect when RSI crosses threshold
        if prev_rsi >= oversold_threshold and current_rsi < oversold_threshold:
            return SignalType.RSI_OVERSOLD

        if prev_rsi <= overbought_threshold and current_rsi > overbought_threshold:
            return SignalType.RSI_OVERBOUGHT

        return None

    @staticmethod
    def detect_macd_signal(ohlcv_list: list[OHLCV]) -> SignalType | None:
        """Detect MACD crossover signals."""
        if len(ohlcv_list) < 35:  # Need enough data for MACD
            return None

        df = IndicatorCalculator.ohlcv_to_dataframe(ohlcv_list)
        macd_line, signal_line, _ = IndicatorCalculator.macd(df["close"])

        if macd_line.isna().iloc[-1] or signal_line.isna().iloc[-1]:
            return None

        curr_macd = macd_line.iloc[-1]
        prev_macd = macd_line.iloc[-2]
        curr_signal = signal_line.iloc[-1]
        prev_signal = signal_line.iloc[-2]

        # Bullish: MACD crosses above signal line
        if prev_macd < prev_signal and curr_macd > curr_signal:
            return SignalType.MACD_BULLISH_CROSS

        # Bearish: MACD crosses below signal line
        if prev_macd > prev_signal and curr_macd < curr_signal:
            return SignalType.MACD_BEARISH_CROSS

        return None

    @staticmethod
    def detect_52w_signals(
        current_price: float,
        high_52w: float | None,
        low_52w: float | None,
        threshold_pct: float = 5.0,
    ) -> list[SignalType]:
        """Detect 52-week high/low signals."""
        signals = []

        if high_52w:
            pct_from_high = (high_52w - current_price) / high_52w * 100

            if current_price >= high_52w:
                signals.append(SignalType.NEW_52W_HIGH)
            elif pct_from_high <= threshold_pct:
                signals.append(SignalType.NEAR_52W_HIGH)

        if low_52w:
            pct_from_low = (current_price - low_52w) / low_52w * 100

            if current_price <= low_52w:
                signals.append(SignalType.NEW_52W_LOW)
            elif pct_from_low <= threshold_pct:
                signals.append(SignalType.NEAR_52W_LOW)

        return signals

    @classmethod
    async def detect_all_signals(
        cls,
        symbol: str,
        ohlcv_list: list[OHLCV],
        high_52w: float | None = None,
        low_52w: float | None = None,
    ) -> list[SignalCreate]:
        """Detect all signals for a stock.

        Args:
            symbol: Stock symbol
            ohlcv_list: OHLCV data
            high_52w: 52-week high price
            low_52w: 52-week low price

        Returns:
            List of detected signals
        """
        signals = []
        current_price = ohlcv_list[-1].close if ohlcv_list else None

        if not current_price:
            return signals

        # MA crossover signals for each period
        for ma_period in ["20W", "50W", "100W", "200W"]:
            signal_type = cls.detect_ma_crossover(ohlcv_list, ma_period)
            if signal_type:
                signals.append(SignalCreate(
                    symbol=symbol,
                    signal_type=signal_type,
                    price=current_price,
                    details={"ma_period": ma_period},
                ))

        # RSI signals
        rsi_signal = cls.detect_rsi_signal(ohlcv_list)
        if rsi_signal:
            df = IndicatorCalculator.ohlcv_to_dataframe(ohlcv_list)
            rsi = IndicatorCalculator.rsi(df["close"])
            signals.append(SignalCreate(
                symbol=symbol,
                signal_type=rsi_signal,
                price=current_price,
                details={
                    "rsi_value": round(rsi.iloc[-1], 2),
                    "threshold": 30 if rsi_signal == SignalType.RSI_OVERSOLD else 70,
                },
            ))

        # MACD signals
        macd_signal = cls.detect_macd_signal(ohlcv_list)
        if macd_signal:
            df = IndicatorCalculator.ohlcv_to_dataframe(ohlcv_list)
            macd_line, signal_line, _ = IndicatorCalculator.macd(df["close"])
            signals.append(SignalCreate(
                symbol=symbol,
                signal_type=macd_signal,
                price=current_price,
                details={
                    "macd": round(macd_line.iloc[-1], 4),
                    "signal": round(signal_line.iloc[-1], 4),
                },
            ))

        # 52-week signals
        week_signals = cls.detect_52w_signals(current_price, high_52w, low_52w)
        for signal_type in week_signals:
            signals.append(SignalCreate(
                symbol=symbol,
                signal_type=signal_type,
                price=current_price,
                details={
                    "high_52w": high_52w,
                    "low_52w": low_52w,
                    "current": current_price,
                },
            ))

        return signals

    @staticmethod
    async def save_signal(
        db: AsyncSession,
        signal: SignalCreate,
        dedupe_hours: int = 24,
    ) -> Signal | None:
        """Save a signal to the database with deduplication.

        Args:
            db: Database session
            signal: Signal to save
            dedupe_hours: Hours to check for duplicate signals

        Returns:
            Saved signal or None if duplicate
        """
        # Check for recent duplicate
        since = datetime.now(timezone.utc) - timedelta(hours=dedupe_hours)
        result = await db.execute(
            select(SignalRecord).where(
                and_(
                    SignalRecord.symbol == signal.symbol,
                    SignalRecord.signal_type == signal.signal_type.value,
                    SignalRecord.timestamp >= since,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.debug(f"Duplicate signal skipped: {signal.symbol} {signal.signal_type}")
            return None

        # Create new signal
        now = datetime.now(timezone.utc)
        signal_record = SignalRecord(
            id=str(uuid4()),
            symbol=signal.symbol,
            signal_type=signal.signal_type.value,
            timestamp=now,
            price=signal.price,
            details=signal.details,
        )
        db.add(signal_record)
        await db.commit()

        return Signal(
            id=signal_record.id,
            symbol=signal.symbol,
            signal_type=signal.signal_type,
            timestamp=now,
            price=signal.price,
            details=signal.details,
            created_at=now,
        )

    @staticmethod
    async def get_signals(
        db: AsyncSession,
        types: list[SignalType] | None = None,
        symbols: list[str] | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[Signal]:
        """Get signals with optional filters.

        Args:
            db: Database session
            types: Filter by signal types
            symbols: Filter by symbols
            since: Get signals after this time
            limit: Maximum number of signals to return

        Returns:
            List of signals
        """
        query = select(SignalRecord).order_by(SignalRecord.timestamp.desc())

        conditions = []
        if types:
            conditions.append(SignalRecord.signal_type.in_([t.value for t in types]))
        if symbols:
            conditions.append(SignalRecord.symbol.in_([s.upper() for s in symbols]))
        if since:
            conditions.append(SignalRecord.timestamp >= since)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.limit(limit)

        result = await db.execute(query)
        records = result.scalars().all()

        return [
            Signal(
                id=r.id,
                symbol=r.symbol,
                signal_type=SignalType(r.signal_type),
                timestamp=r.timestamp,
                price=float(r.price),
                details=r.details,
                created_at=r.created_at,
            )
            for r in records
        ]
