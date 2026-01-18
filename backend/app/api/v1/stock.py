"""Stock data API endpoints."""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_cache, get_market_data
from app.core.indicators import IndicatorCalculator
from app.models.stock import Quote, StockInfo, StockData, ChartData, TimeFrame, Period, OHLCV
from app.models.indicator import IndicatorData
from app.services.cache import CacheService
from app.services.market_data import MarketDataService
from app.cache.keys import CacheKeys
from app.cache.ttl import CacheTTL
from app.errors.exceptions import NotFoundError

router = APIRouter()


# Period to trading days mapping (approximate)
PERIOD_DAYS = {
    Period.THREE_MONTHS: 63,   # ~3 months of trading days
    Period.SIX_MONTHS: 126,    # ~6 months
    Period.ONE_YEAR: 252,      # ~1 year
    Period.TWO_YEARS: 504,     # ~2 years
    Period.FIVE_YEARS: 1260,   # ~5 years
}


@router.get("/{symbol}", response_model=StockData)
async def get_stock(
    symbol: str,
    timeframe: TimeFrame = Query(default=TimeFrame.DAILY, description="Chart timeframe"),
    period: Period = Query(default=Period.ONE_YEAR, description="Historical period"),
    market_data: MarketDataService = Depends(get_market_data),
    cache: CacheService = Depends(get_cache),
) -> StockData:
    """Get complete stock data including quote and OHLCV.

    **Parameters:**
    - **symbol**: Stock ticker symbol (e.g., AAPL)
    - **timeframe**: Chart timeframe (1D = daily, 1W = weekly)
    - **period**: Historical data period (3M, 6M, 1Y, 2Y)

    **Returns:**
    Stock info, current quote, and OHLCV data.
    """
    symbol = symbol.upper()

    # Get stock info
    info = await market_data.get_stock_info(symbol)
    if not info:
        raise NotFoundError("Stock", symbol)

    # Get quote (with cache)
    cache_key = CacheKeys.quote(symbol)
    cached_quote = await cache.get(cache_key)

    if cached_quote:
        quote = Quote(**cached_quote)
    else:
        quote = await market_data.get_quote(symbol)
        if not quote:
            raise NotFoundError("Quote", symbol)
        await cache.set(cache_key, quote.model_dump(), CacheTTL.quote())

    # Get OHLCV data (with cache)
    ohlcv_key = CacheKeys.ohlcv(symbol, timeframe.value, period.value)
    cached_ohlcv = await cache.get(ohlcv_key)

    if cached_ohlcv:
        from app.models.stock import OHLCV
        ohlcv = [OHLCV(**o) for o in cached_ohlcv]
    else:
        ohlcv = await market_data.get_ohlcv(symbol, period, timeframe)
        if ohlcv:
            ttl = CacheTTL.ohlcv_daily() if timeframe == TimeFrame.DAILY else CacheTTL.ohlcv_weekly()
            await cache.set(ohlcv_key, [o.model_dump() for o in ohlcv], ttl)

    return StockData(info=info, quote=quote, ohlcv=ohlcv)


@router.get("/{symbol}/quote", response_model=Quote)
async def get_stock_quote(
    symbol: str,
    market_data: MarketDataService = Depends(get_market_data),
    cache: CacheService = Depends(get_cache),
) -> Quote:
    """Get real-time stock quote.

    **Parameters:**
    - **symbol**: Stock ticker symbol

    **Returns:**
    Current price, change, volume, and 52-week range.
    """
    symbol = symbol.upper()

    # Check cache
    cache_key = CacheKeys.quote(symbol)
    cached = await cache.get(cache_key)

    if cached:
        return Quote(**cached)

    # Fetch fresh quote
    quote = await market_data.get_quote(symbol)
    if not quote:
        raise NotFoundError("Quote", symbol)

    # Cache result
    await cache.set(cache_key, quote.model_dump(), CacheTTL.quote())

    return quote


@router.get("/{symbol}/chart", response_model=ChartData)
async def get_stock_chart(
    symbol: str,
    timeframe: TimeFrame = Query(default=TimeFrame.DAILY),
    period: Period = Query(default=Period.ONE_YEAR),
    include_ma: bool = Query(default=True, description="Include moving averages"),
    include_rsi: bool = Query(default=False, description="Include RSI"),
    include_macd: bool = Query(default=False, description="Include MACD"),
    market_data: MarketDataService = Depends(get_market_data),
    cache: CacheService = Depends(get_cache),
) -> ChartData:
    """Get chart data with OHLCV and optional indicators.

    **Parameters:**
    - **symbol**: Stock ticker symbol
    - **timeframe**: Chart timeframe (1D or 1W)
    - **period**: Historical period
    - **include_ma**: Include moving average lines
    - **include_rsi**: Include RSI indicator
    - **include_macd**: Include MACD indicator

    **Returns:**
    OHLCV data with requested indicators, filtered to the requested period.
    Indicators are calculated on full history but sliced to match the period.
    """
    symbol = symbol.upper()

    # Check cache
    cache_key = CacheKeys.chart(
        symbol=symbol,
        timeframe=timeframe.value,
        period=period.value,
        include_ma=include_ma,
        include_rsi=include_rsi,
        include_macd=include_macd,
    )
    cached = await cache.get(cache_key)
    if cached:
        return ChartData(**cached)

    # Get OHLCV data (need max history for MA calculations)
    full_ohlcv = await market_data.get_ohlcv_for_indicators(symbol, "200W")

    if not full_ohlcv:
        raise NotFoundError("Chart data", symbol)

    # Calculate indicators on full history (needed for accurate MA values)
    indicators: dict[str, Any] = {}

    if include_ma or include_rsi or include_macd:
        indicator_data = IndicatorCalculator.calculate_all_indicators(
            symbol,
            full_ohlcv,
            include_ma=include_ma,
            include_rsi=include_rsi,
            include_macd=include_macd,
        )

        if include_ma:
            if indicator_data.ma_20w:
                indicators["ma_20w"] = indicator_data.ma_20w.model_dump()
            if indicator_data.ma_50w:
                indicators["ma_50w"] = indicator_data.ma_50w.model_dump()
            if indicator_data.ma_100w:
                indicators["ma_100w"] = indicator_data.ma_100w.model_dump()
            if indicator_data.ma_200w:
                indicators["ma_200w"] = indicator_data.ma_200w.model_dump()

        if include_rsi and indicator_data.rsi:
            indicators["rsi"] = indicator_data.rsi.model_dump()

        if include_macd and indicator_data.macd:
            indicators["macd"] = indicator_data.macd.model_dump()

    # Filter OHLCV to requested period
    period_days = PERIOD_DAYS.get(period, 252)
    sliced_ohlcv = full_ohlcv[-period_days:] if len(full_ohlcv) > period_days else full_ohlcv

    # Slice indicator values to match the period
    indicators = _slice_indicator_payload(indicators, len(sliced_ohlcv))

    # Handle weekly timeframe by resampling
    if timeframe == TimeFrame.WEEKLY:
        weekly_ohlcv = _resample_to_weekly(sliced_ohlcv)
        indicators = _resample_indicator_payload(indicators, weekly_ohlcv)
        ohlcv = weekly_ohlcv
    else:
        ohlcv = sliced_ohlcv

    chart = ChartData(
        symbol=symbol,
        timeframe=timeframe,
        period=period,
        ohlcv=ohlcv,
        indicators=indicators,
    )

    await cache.set(cache_key, chart.model_dump(), CacheTTL.chart())

    return chart


def _slice_indicator_payload(
    indicators: dict[str, Any],
    length: int,
) -> dict[str, Any]:
    """Slice indicator series to match OHLCV length."""
    if length <= 0:
        return indicators

    for payload in indicators.values():
        if isinstance(payload, dict):
            for field, series in payload.items():
                if isinstance(series, list):
                    payload[field] = series[-length:]
    return indicators


def _resample_indicator_payload(
    indicators: dict[str, Any],
    weekly_ohlcv: list[OHLCV],
) -> dict[str, Any]:
    """Resample indicator series to weekly cadence aligned with OHLCV."""
    if not weekly_ohlcv:
        return indicators

    week_keys = []
    week_dates = []
    for bar in weekly_ohlcv:
        iso = bar.timestamp.isocalendar()
        week_keys.append((iso.year, iso.week))
        week_dates.append(bar.timestamp)

    for payload in indicators.values():
        if not isinstance(payload, dict):
            continue
        for field, series in payload.items():
            if isinstance(series, list) and series:
                payload[field] = _resample_series_to_week(series, week_keys, week_dates)

    return indicators


def _resample_to_weekly(ohlcv: list[OHLCV]) -> list[OHLCV]:
    """Resample daily OHLCV data to weekly.

    Groups data by ISO week and aggregates:
    - open: first day's open
    - high: max high of the week
    - low: min low of the week
    - close: last day's close
    - volume: sum of daily volumes
    """
    if not ohlcv:
        return []

    weekly: dict[tuple[int, int], list[OHLCV]] = {}

    for bar in ohlcv:
        iso = bar.timestamp.isocalendar()
        key = (iso.year, iso.week)
        if key not in weekly:
            weekly[key] = []
        weekly[key].append(bar)

    result = []
    for key in sorted(weekly.keys()):
        bars = weekly[key]
        result.append(
            OHLCV(
                timestamp=bars[-1].timestamp,  # Use last day of week
                open=bars[0].open,
                high=max(b.high for b in bars),
                low=min(b.low for b in bars),
                close=bars[-1].close,
                volume=sum(b.volume for b in bars),
            )
        )

    return result


def _resample_series_to_week(
    series: list[tuple[Any, Any]],
    week_keys: list[tuple[int, int]],
    week_dates: list[datetime],
) -> list[tuple[datetime, Any]]:
    """Resample a time series to weekly values aligned to week end dates."""
    grouped: dict[tuple[int, int], tuple[datetime, Any]] = {}

    for item in series:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        ts, value = item[0], item[1]
        dt = _to_datetime(ts)
        if dt is None:
            continue
        iso = dt.isocalendar()
        grouped[(iso.year, iso.week)] = (dt, value)

    result: list[tuple[datetime, Any]] = []
    for key, week_date in zip(week_keys, week_dates):
        if key in grouped:
            _, value = grouped[key]
            result.append((week_date, value))
        else:
            result.append((week_date, None))

    return result


def _to_datetime(value: Any) -> datetime | None:
    """Normalize timestamps for indicator resampling."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


@router.get("/{symbol}/indicators", response_model=IndicatorData)
async def get_stock_indicators(
    symbol: str,
    market_data: MarketDataService = Depends(get_market_data),
    cache: CacheService = Depends(get_cache),
) -> IndicatorData:
    """Get all technical indicators for a stock.

    **Parameters:**
    - **symbol**: Stock ticker symbol

    **Returns:**
    Moving averages (20W, 50W, 100W, 200W), RSI, and MACD.
    """
    symbol = symbol.upper()

    # Check cache
    cache_key = CacheKeys.indicators(symbol, "1D")
    cached = await cache.get(cache_key)

    if cached:
        return IndicatorData(**cached)

    # Get OHLCV data
    ohlcv = await market_data.get_ohlcv_for_indicators(symbol, "200W")

    if not ohlcv:
        raise NotFoundError("Indicator data", symbol)

    # Calculate all indicators
    indicators = IndicatorCalculator.calculate_all_indicators(symbol, ohlcv)

    # Cache result
    await cache.set(cache_key, indicators.model_dump(), CacheTTL.indicators())

    return indicators
