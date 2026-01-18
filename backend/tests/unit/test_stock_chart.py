"""Tests for chart slicing and resampling utilities."""

from datetime import datetime, timedelta

from app.api.v1.stock import (
    _resample_to_weekly,
    _resample_indicator_payload,
    _slice_indicator_payload,
)
from app.models.stock import OHLCV


def _make_ohlcv(start: datetime, days: int) -> list[OHLCV]:
    data = []
    for i in range(days):
        date = start + timedelta(days=i)
        base = 100 + i
        data.append(
            OHLCV(
                timestamp=date,
                open=base,
                high=base + 2,
                low=base - 1,
                close=base + 1,
                volume=1000 + i,
            )
        )
    return data


def test_resample_to_weekly_groups_and_aggregates():
    data = _make_ohlcv(datetime(2024, 1, 1), 10)
    weekly = _resample_to_weekly(data)

    assert len(weekly) == 2

    first_week = weekly[0]
    assert first_week.open == data[0].open
    assert first_week.close == data[6].close
    assert first_week.high == max(bar.high for bar in data[:7])
    assert first_week.low == min(bar.low for bar in data[:7])
    assert first_week.volume == sum(bar.volume for bar in data[:7])


def test_slice_indicator_payload_slices_all_series():
    base = datetime(2024, 1, 1)
    series = [(base + timedelta(days=i), float(i)) for i in range(5)]
    indicators = {
        "ma_20w": {"values": series},
        "rsi": {"values": series},
        "macd": {
            "macd_line": series,
            "signal_line": series,
            "histogram": series,
        },
    }

    sliced = _slice_indicator_payload(indicators, 2)

    assert len(sliced["ma_20w"]["values"]) == 2
    assert len(sliced["rsi"]["values"]) == 2
    assert len(sliced["macd"]["macd_line"]) == 2
    assert len(sliced["macd"]["signal_line"]) == 2
    assert len(sliced["macd"]["histogram"]) == 2


def test_resample_indicator_payload_aligns_with_weekly_bars():
    daily = _make_ohlcv(datetime(2024, 1, 1), 10)
    weekly = _resample_to_weekly(daily)

    series = [(bar.timestamp, bar.close) for bar in daily]
    indicators = {
        "ma_20w": {"values": series},
        "macd": {"macd_line": series, "signal_line": series, "histogram": series},
    }

    resampled = _resample_indicator_payload(indicators, weekly)

    assert len(resampled["ma_20w"]["values"]) == len(weekly)
    assert len(resampled["macd"]["macd_line"]) == len(weekly)

    # Last value of week should align to weekly timestamp
    assert resampled["ma_20w"]["values"][0][0] == weekly[0].timestamp
    assert resampled["ma_20w"]["values"][1][0] == weekly[1].timestamp
