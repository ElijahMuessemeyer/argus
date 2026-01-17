"""Tests for indicator calculations."""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from app.core.indicators import IndicatorCalculator, MA_PERIOD_MAP
from app.models.stock import OHLCV
from app.models.indicator import MAType


class TestMovingAverage:
    """Tests for moving average calculations."""

    def test_sma_basic(self):
        """Test basic SMA calculation."""
        prices = pd.Series([10, 20, 30, 40, 50])
        ma = IndicatorCalculator.moving_average(prices, period=3, ma_type=MAType.SMA)

        # First 2 values should be NaN (not enough data)
        assert pd.isna(ma.iloc[0])
        assert pd.isna(ma.iloc[1])
        # SMA(3) at index 2 = (10+20+30)/3 = 20
        assert ma.iloc[2] == 20
        # SMA(3) at index 3 = (20+30+40)/3 = 30
        assert ma.iloc[3] == 30
        # SMA(3) at index 4 = (30+40+50)/3 = 40
        assert ma.iloc[4] == 40

    def test_ema_basic(self):
        """Test basic EMA calculation."""
        prices = pd.Series([10, 20, 30, 40, 50])
        ma = IndicatorCalculator.moving_average(prices, period=3, ma_type=MAType.EMA)

        # EMA should have values after minimum period
        assert pd.notna(ma.iloc[2])
        assert pd.notna(ma.iloc[4])

    def test_ma_with_ohlcv(self, sample_ohlcv):
        """Test MA calculation with OHLCV data."""
        df = IndicatorCalculator.ohlcv_to_dataframe(sample_ohlcv)
        result = IndicatorCalculator.calculate_ma_result(df, period=20)

        assert result.period == 20
        assert result.current_value is not None
        assert result.current_price is not None
        assert result.distance_percent is not None
        assert len(result.values) == len(sample_ohlcv)

    def test_ma_period_mapping(self):
        """Test that MA periods are correctly mapped."""
        assert MA_PERIOD_MAP["20W"] == 100
        assert MA_PERIOD_MAP["50W"] == 250
        assert MA_PERIOD_MAP["100W"] == 500
        assert MA_PERIOD_MAP["200W"] == 1000


class TestRSI:
    """Tests for RSI calculations."""

    def test_rsi_range(self, sample_ohlcv):
        """Test that RSI values are within 0-100 range."""
        df = IndicatorCalculator.ohlcv_to_dataframe(sample_ohlcv)
        rsi = IndicatorCalculator.rsi(df["close"])

        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert all(0 <= v <= 100 for v in valid_rsi)

    def test_rsi_result_structure(self, sample_ohlcv):
        """Test RSI result structure."""
        df = IndicatorCalculator.ohlcv_to_dataframe(sample_ohlcv)
        result = IndicatorCalculator.calculate_rsi_result(df)

        assert result.period == 14
        assert result.current_value is not None
        assert isinstance(result.is_overbought, bool)
        assert isinstance(result.is_oversold, bool)

    def test_rsi_overbought_detection(self):
        """Test RSI overbought detection."""
        # Create data with strong uptrend (should have high RSI)
        data = []
        base = datetime(2024, 1, 1)
        for i in range(50):
            data.append(OHLCV(
                timestamp=base + timedelta(days=i),
                open=100 + i * 5,
                high=105 + i * 5,
                low=98 + i * 5,
                close=103 + i * 5,
                volume=1000000,
            ))

        df = IndicatorCalculator.ohlcv_to_dataframe(data)
        result = IndicatorCalculator.calculate_rsi_result(df)

        # Strong uptrend should lead to high RSI
        assert result.current_value is not None
        assert result.current_value > 50


class TestMACD:
    """Tests for MACD calculations."""

    def test_macd_components(self, sample_ohlcv):
        """Test that MACD returns all three components."""
        df = IndicatorCalculator.ohlcv_to_dataframe(sample_ohlcv)
        macd_line, signal_line, histogram = IndicatorCalculator.macd(df["close"])

        assert len(macd_line) == len(sample_ohlcv)
        assert len(signal_line) == len(sample_ohlcv)
        assert len(histogram) == len(sample_ohlcv)

    def test_macd_result_structure(self, sample_ohlcv):
        """Test MACD result structure."""
        df = IndicatorCalculator.ohlcv_to_dataframe(sample_ohlcv)
        result = IndicatorCalculator.calculate_macd_result(df)

        assert result.fast_period == 12
        assert result.slow_period == 26
        assert result.signal_period == 9
        assert len(result.macd_line) > 0
        assert len(result.signal_line) > 0
        assert len(result.histogram) > 0

    def test_histogram_equals_difference(self, sample_ohlcv):
        """Test that histogram equals MACD line minus signal line."""
        df = IndicatorCalculator.ohlcv_to_dataframe(sample_ohlcv)
        macd_line, signal_line, histogram = IndicatorCalculator.macd(df["close"])

        # Check at a point where all values are valid
        idx = -1
        while pd.isna(macd_line.iloc[idx]) or pd.isna(signal_line.iloc[idx]):
            idx -= 1

        expected = macd_line.iloc[idx] - signal_line.iloc[idx]
        assert abs(histogram.iloc[idx] - expected) < 0.0001


class TestAllIndicators:
    """Tests for combined indicator calculation."""

    def test_calculate_all_indicators(self, sample_ohlcv):
        """Test calculating all indicators at once."""
        result = IndicatorCalculator.calculate_all_indicators(
            "TEST",
            sample_ohlcv,
            include_ma=True,
            include_rsi=True,
            include_macd=True,
        )

        assert result.symbol == "TEST"
        assert result.ma_20w is not None
        assert result.rsi is not None
        assert result.macd is not None

    def test_calculate_selective_indicators(self, sample_ohlcv):
        """Test selective indicator calculation."""
        result = IndicatorCalculator.calculate_all_indicators(
            "TEST",
            sample_ohlcv,
            include_ma=True,
            include_rsi=False,
            include_macd=False,
        )

        assert result.ma_20w is not None
        assert result.rsi is None
        assert result.macd is None
