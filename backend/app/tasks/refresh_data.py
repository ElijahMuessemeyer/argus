"""Background task for refreshing market data."""

import asyncio
from datetime import datetime

from app.core.universe import UniverseManager
from app.services.market_data import market_data_service
from app.services.cache import cache_service
from app.cache.keys import CacheKeys
from app.cache.ttl import CacheTTL
from app.db.session import AsyncSessionLocal
from app.utils.logging import get_logger

logger = get_logger("tasks.refresh_data")


async def refresh_market_data() -> None:
    """Refresh market data for all stocks in the universe.

    This task runs every 5 minutes during market hours.
    It updates quotes and invalidates stale cache entries.
    """
    start_time = datetime.utcnow()
    logger.info("Starting market data refresh")

    async with AsyncSessionLocal() as db:
        try:
            # Get universe symbols
            symbols = await UniverseManager.get_symbols(db)

            if not symbols:
                logger.warning("No symbols in universe to refresh")
                return

            # Batch process quotes
            batch_size = 20
            updated = 0
            failed = 0

            for i in range(0, len(symbols), batch_size):
                batch = symbols[i : i + batch_size]

                try:
                    quotes = await market_data_service.get_batch_quotes(batch)

                    for symbol, quote in quotes.items():
                        if quote:
                            # Cache the quote
                            await cache_service.set(
                                CacheKeys.quote(symbol),
                                quote.model_dump(),
                                CacheTTL.quote(),
                            )
                            updated += 1
                        else:
                            failed += 1

                except Exception as e:
                    logger.error(f"Error refreshing batch {i}-{i+batch_size}: {e}")
                    failed += len(batch)

                # Small delay between batches to avoid rate limiting
                await asyncio.sleep(0.5)

            # Invalidate screener cache to force recalculation
            await cache_service.delete_pattern("argus:screener:*")

            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"Market data refresh completed",
                extra={
                    "extra_data": {
                        "updated": updated,
                        "failed": failed,
                        "total": len(symbols),
                        "duration_seconds": round(duration, 2),
                    }
                },
            )

        except Exception as e:
            logger.exception(f"Market data refresh failed: {e}")


async def refresh_single_stock(symbol: str) -> bool:
    """Refresh data for a single stock.

    Args:
        symbol: Stock symbol to refresh

    Returns:
        True if successful, False otherwise
    """
    try:
        quote = await market_data_service.get_quote(symbol)
        if quote:
            await cache_service.set(
                CacheKeys.quote(symbol),
                quote.model_dump(),
                CacheTTL.quote(),
            )
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to refresh {symbol}: {e}")
        return False
