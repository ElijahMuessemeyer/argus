"""Stock data API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_cache, get_market_data
from app.core.indicators import IndicatorCalculator
from app.models.stock import Quote, StockInfo, StockData, ChartData, TimeFrame, Period
from app.models.indicator import IndicatorData
from app.services.cache import CacheService
from app.services.market_data import MarketDataService
from app.cache.keys import CacheKeys
from app.cache.ttl import CacheTTL
from app.errors.exceptions import NotFoundError

router = APIRouter()


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
    OHLCV data with requested indicators.
    """
    symbol = symbol.upper()

    # Get OHLCV data (need max history for MAs)
    ohlcv = await market_data.get_ohlcv_for_indicators(symbol, "200W")

    if not ohlcv:
        raise NotFoundError("Chart data", symbol)

    # Calculate indicators
    indicators: dict[str, Any] = {}

    if include_ma or include_rsi or include_macd:
        indicator_data = IndicatorCalculator.calculate_all_indicators(
            symbol,
            ohlcv,
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

    return ChartData(
        symbol=symbol,
        timeframe=timeframe,
        period=period,
        ohlcv=ohlcv,
        indicators=indicators,
    )


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
