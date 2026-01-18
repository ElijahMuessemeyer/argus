"""Screener core logic."""

import asyncio
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.indicators import IndicatorCalculator, MA_PERIOD_MAP
from app.core.universe import UniverseManager
from app.models.screener import (
    ScreenerRequest,
    ScreenerResult,
    ScreenerResponse,
    MAFilter,
    SortField,
    SortOrder,
)
from app.services.market_data import market_data_service
from app.services.cache import cache_service
from app.cache.keys import CacheKeys
from app.cache.ttl import CacheTTL
from app.utils.logging import get_logger

logger = get_logger("core.screener")


class ScreenerService:
    """Service for screening stocks based on MA criteria."""

    @staticmethod
    def _get_ma_period_days(ma_filter: MAFilter) -> int:
        """Get the number of trading days for an MA filter."""
        return MA_PERIOD_MAP.get(ma_filter.value, 100)

    @staticmethod
    async def _process_stock(
        symbol: str,
        name: str,
        sector: str | None,
        ma_filter: MAFilter,
    ) -> ScreenerResult | None:
        """Process a single stock for screening."""
        try:
            # Get OHLCV data with enough history
            ohlcv = await market_data_service.get_ohlcv_for_indicators(
                symbol,
                ma_filter.value,
            )

            if not ohlcv:
                return None

            # Calculate MA distance
            current_price, ma_value, distance_pct = IndicatorCalculator.get_ma_distance(
                ohlcv,
                ma_filter.value,
            )

            if current_price is None or ma_value is None or distance_pct is None:
                return None

            # Get quote for change data
            quote = await market_data_service.get_quote(symbol)
            if not quote:
                return None

            # Determine position relative to MA
            if abs(distance_pct) < 0.5:
                position = "at"
            elif distance_pct > 0:
                position = "above"
            else:
                position = "below"

            return ScreenerResult(
                symbol=symbol,
                name=name,
                sector=sector,
                price=current_price,
                change=quote.change,
                change_percent=quote.change_percent,
                market_cap=quote.market_cap,
                ma_value=ma_value,
                ma_period=ma_filter.value,
                distance=round(current_price - ma_value, 2),
                distance_percent=distance_pct,
                position=position,
            )
        except Exception as e:
            logger.warning(f"Error processing {symbol}: {e}")
            return None

    @classmethod
    async def screen(
        cls,
        db: AsyncSession,
        request: ScreenerRequest,
    ) -> ScreenerResponse:
        """Screen stocks based on MA criteria.

        Args:
            db: Database session
            request: Screener filter parameters

        Returns:
            ScreenerResponse with filtered and sorted results
        """
        # Check cache first
        cache_key = CacheKeys.screener(request.model_dump())
        cached = await cache_service.get(cache_key)
        if cached:
            return ScreenerResponse(
                results=[ScreenerResult(**r) for r in cached["results"]],
                total=cached["total"],
                filters=request,
                cached=True,
                cache_timestamp=cached.get("timestamp"),
            )

        # Get universe
        universe = await UniverseManager.get_universe(db)
        if not universe:
            # Initialize if empty
            await UniverseManager.initialize_universe(db)
            universe = await UniverseManager.get_universe(db)

        # Process stocks concurrently with rate limiting
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests

        async def process_with_limit(stock: dict[str, Any]) -> ScreenerResult | None:
            async with semaphore:
                return await cls._process_stock(
                    stock["symbol"],
                    stock["name"],
                    stock.get("sector"),
                    request.ma_filter,
                )

        tasks = [process_with_limit(stock) for stock in universe]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None values and exceptions
        valid_results: list[ScreenerResult] = []
        for r in results:
            if isinstance(r, ScreenerResult):
                valid_results.append(r)

        # Apply distance filter
        filtered_results = []
        for r in valid_results:
            abs_distance = abs(r.distance_percent)
            if abs_distance > request.distance_pct:
                continue

            if r.position == "below" and not request.include_below:
                continue
            if r.position in ("above", "at") and not request.include_above:
                continue

            filtered_results.append(r)

        # Sort results
        sort_key = cls._get_sort_key(request.sort_by)
        reverse = request.sort_order == SortOrder.DESC

        sorted_results = sorted(
            filtered_results,
            key=sort_key,
            reverse=reverse,
        )

        # Apply pagination
        total = len(sorted_results)
        paginated = sorted_results[request.offset : request.offset + request.limit]

        # Cache result
        from datetime import datetime, timezone
        cache_data = {
            "results": [r.model_dump() for r in paginated],
            "total": total,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await cache_service.set(cache_key, cache_data, CacheTTL.screener())

        return ScreenerResponse(
            results=paginated,
            total=total,
            filters=request,
            cached=False,
        )

    @staticmethod
    def _get_sort_key(sort_by: SortField):
        """Get sort key function for a field."""
        if sort_by == SortField.SYMBOL:
            return lambda r: r.symbol
        elif sort_by == SortField.NAME:
            return lambda r: r.name
        elif sort_by == SortField.PRICE:
            return lambda r: r.price
        elif sort_by == SortField.DISTANCE:
            return lambda r: abs(r.distance_percent)
        elif sort_by == SortField.MARKET_CAP:
            return lambda r: r.market_cap or 0
        elif sort_by == SortField.CHANGE:
            return lambda r: r.change_percent
        else:
            return lambda r: abs(r.distance_percent)
