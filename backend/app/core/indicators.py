"""Technical indicator calculations."""

from datetime import datetime
from typing import Any

import pandas as pd
import numpy as np

from app.models.stock import OHLCV
from app.models.indicator import (
    MovingAverageResult,
    RSIResult,
    MACDResult,
    IndicatorData,
    MAType,
)
from app.utils.logging import get_logger

logger = get_logger("core.indicators")

# Weekly MA to daily period mapping
MA_PERIOD_MAP = {
    "20W": 100,   # 20 weeks × 5 trading days
    "50W": 250,   # 50 weeks × 5 trading days
    "100W": 500,  # 100 weeks × 5 trading days
    "200W": 1000, # 200 weeks × 5 trading days
}


class IndicatorCalculator:
    """Calculator for technical indicators."""

    @staticmethod
    def ohlcv_to_dataframe(ohlcv_list: list[OHLCV]) -> pd.DataFrame:
        """Convert OHLCV list to pandas DataFrame."""
        if not ohlcv_list:
            return pd.DataFrame()

        data = {
            "timestamp": [o.timestamp for o in ohlcv_list],
            "open": [o.open for o in ohlcv_list],
            "high": [o.high for o in ohlcv_list],
            "low": [o.low for o in ohlcv_list],
            "close": [o.close for o in ohlcv_list],
            "volume": [o.volume for o in ohlcv_list],
        }
        df = pd.DataFrame(data)
        df.set_index("timestamp", inplace=True)
        df.sort_index(inplace=True)
        return df

    @staticmethod
    def moving_average(
        prices: pd.Series,
        period: int,
        ma_type: MAType = MAType.SMA,
    ) -> pd.Series:
        """Calculate moving average.

        Args:
            prices: Price series (typically close prices)
            period: Number of periods for the MA
            ma_type: SMA or EMA

        Returns:
            Series with MA values
        """
        if ma_type == MAType.SMA:
            return prices.rolling(window=period, min_periods=period).mean()
        else:  # EMA
            return prices.ewm(span=period, adjust=False, min_periods=period).mean()

    @staticmethod
    def calculate_ma_result(
        df: pd.DataFrame,
        period: int,
        ma_type: MAType = MAType.SMA,
    ) -> MovingAverageResult:
        """Calculate MA and return structured result."""
        if df.empty or len(df) < period:
            return MovingAverageResult(
                period=period,
                ma_type=ma_type,
                values=[],
                current_value=None,
                current_price=None,
                distance_percent=None,
            )

        ma_series = IndicatorCalculator.moving_average(df["close"], period, ma_type)

        # Convert to list of tuples
        values = [
            (idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else idx,
             round(val, 2) if pd.notna(val) else None)
            for idx, val in ma_series.items()
        ]

        current_ma = ma_series.iloc[-1] if pd.notna(ma_series.iloc[-1]) else None
        current_price = df["close"].iloc[-1]

        distance_pct = None
        if current_ma and current_price:
            distance_pct = round((current_price - current_ma) / current_ma * 100, 2)

        return MovingAverageResult(
            period=period,
            ma_type=ma_type,
            values=values,
            current_value=round(current_ma, 2) if current_ma else None,
            current_price=round(current_price, 2) if current_price else None,
            distance_percent=distance_pct,
        )

    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI).

        Args:
            prices: Price series (typically close prices)
            period: RSI period (default 14)

        Returns:
            Series with RSI values (0-100)
        """
        delta = prices.diff()

        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)

        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()

        # Allow division by zero: avg_loss=0 yields RS=inf -> RSI=100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Flat periods (no gains and no losses) should be neutral
        flat_mask = (avg_gain == 0) & (avg_loss == 0)
        rsi = rsi.mask(flat_mask, 50)

        return rsi

    @staticmethod
    def calculate_rsi_result(
        df: pd.DataFrame,
        period: int = 14,
    ) -> RSIResult:
        """Calculate RSI and return structured result."""
        if df.empty or len(df) < period + 1:
            return RSIResult(
                period=period,
                values=[],
                current_value=None,
                is_overbought=False,
                is_oversold=False,
            )

        rsi_series = IndicatorCalculator.rsi(df["close"], period)

        values = [
            (idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else idx,
             round(val, 2) if pd.notna(val) else None)
            for idx, val in rsi_series.items()
        ]

        current_rsi = rsi_series.iloc[-1] if pd.notna(rsi_series.iloc[-1]) else None

        return RSIResult(
            period=period,
            values=values,
            current_value=round(current_rsi, 2) if current_rsi is not None else None,
            is_overbought=current_rsi > 70 if current_rsi is not None else False,
            is_oversold=current_rsi < 30 if current_rsi is not None else False,
        )

    @staticmethod
    def macd(
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence).

        Args:
            prices: Price series
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line period (default 9)

        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
        slow_ema = prices.ewm(span=slow_period, adjust=False).mean()

        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def calculate_macd_result(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> MACDResult:
        """Calculate MACD and return structured result."""
        min_periods = slow_period + signal_period
        if df.empty or len(df) < min_periods:
            return MACDResult(
                fast_period=fast_period,
                slow_period=slow_period,
                signal_period=signal_period,
                macd_line=[],
                signal_line=[],
                histogram=[],
            )

        macd_line, signal_line, histogram = IndicatorCalculator.macd(
            df["close"], fast_period, slow_period, signal_period
        )

        def series_to_tuples(s: pd.Series) -> list[tuple[datetime, float | None]]:
            return [
                (idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else idx,
                 round(val, 4) if pd.notna(val) else None)
                for idx, val in s.items()
            ]

        return MACDResult(
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period,
            macd_line=series_to_tuples(macd_line),
            signal_line=series_to_tuples(signal_line),
            histogram=series_to_tuples(histogram),
            current_macd=round(macd_line.iloc[-1], 4) if pd.notna(macd_line.iloc[-1]) else None,
            current_signal=round(signal_line.iloc[-1], 4) if pd.notna(signal_line.iloc[-1]) else None,
            current_histogram=round(histogram.iloc[-1], 4) if pd.notna(histogram.iloc[-1]) else None,
        )

    @classmethod
    def calculate_all_indicators(
        cls,
        symbol: str,
        ohlcv_list: list[OHLCV],
        include_ma: bool = True,
        include_rsi: bool = True,
        include_macd: bool = True,
    ) -> IndicatorData:
        """Calculate all indicators for a stock.

        Args:
            symbol: Stock symbol
            ohlcv_list: List of OHLCV data
            include_ma: Include moving averages
            include_rsi: Include RSI
            include_macd: Include MACD

        Returns:
            IndicatorData with all requested indicators
        """
        df = cls.ohlcv_to_dataframe(ohlcv_list)

        result = IndicatorData(symbol=symbol)

        if include_ma:
            result.ma_20w = cls.calculate_ma_result(df, MA_PERIOD_MAP["20W"])
            result.ma_50w = cls.calculate_ma_result(df, MA_PERIOD_MAP["50W"])
            result.ma_100w = cls.calculate_ma_result(df, MA_PERIOD_MAP["100W"])
            result.ma_200w = cls.calculate_ma_result(df, MA_PERIOD_MAP["200W"])

        if include_rsi:
            result.rsi = cls.calculate_rsi_result(df)

        if include_macd:
            result.macd = cls.calculate_macd_result(df)

        return result

    @classmethod
    def get_ma_distance(
        cls,
        ohlcv_list: list[OHLCV],
        ma_period: str,
    ) -> tuple[float | None, float | None, float | None]:
        """Get distance from a specific MA.

        Args:
            ohlcv_list: OHLCV data
            ma_period: MA period string (20W, 50W, 100W, 200W)

        Returns:
            Tuple of (current_price, ma_value, distance_percent)
        """
        period = MA_PERIOD_MAP.get(ma_period)
        if not period:
            return None, None, None

        df = cls.ohlcv_to_dataframe(ohlcv_list)
        if df.empty or len(df) < period:
            return None, None, None

        ma_result = cls.calculate_ma_result(df, period)

        return (
            ma_result.current_price,
            ma_result.current_value,
            ma_result.distance_percent,
        )
