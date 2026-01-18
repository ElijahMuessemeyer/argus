"""Background task for detecting trading signals."""

import asyncio
from datetime import datetime, timezone

from app.core.universe import UniverseManager
from app.core.signals import SignalDetector
from app.services.market_data import market_data_service
from app.db.session import AsyncSessionLocal
from app.utils.logging import get_logger

logger = get_logger("tasks.detect_signals")


async def detect_all_signals() -> None:
    """Detect trading signals for all stocks in the universe.

    This task runs every 5 minutes during market hours.
    It checks for MA crossovers, RSI signals, MACD signals, and 52W highs/lows.
    """
    start_time = datetime.now(timezone.utc)
    logger.info("Starting signal detection")

    try:
        # Get universe (uses its own session)
        async with AsyncSessionLocal() as db:
            universe = await UniverseManager.get_universe(db)

        if not universe:
            logger.warning("No stocks in universe for signal detection")
            return

        signals_detected = 0
        signals_saved = 0
        errors = 0

        # Process stocks with rate limiting
        # Each task creates its own session for DB writes
        semaphore = asyncio.Semaphore(5)

        async def process_stock(stock: dict) -> tuple[int, int]:
            async with semaphore:
                return await detect_signals_for_stock(stock["symbol"])

        tasks = [process_stock(stock) for stock in universe]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                errors += 1
            else:
                detected, saved = result
                signals_detected += detected
                signals_saved += saved

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(
            "Signal detection completed",
            extra={
                "extra_data": {
                    "stocks_processed": len(universe),
                    "signals_detected": signals_detected,
                    "signals_saved": signals_saved,
                    "errors": errors,
                    "duration_seconds": round(duration, 2),
                }
            },
        )

    except Exception as e:
        logger.exception(f"Signal detection failed: {e}")


async def detect_signals_for_stock(symbol: str) -> tuple[int, int]:
    """Detect and save signals for a single stock.

    Creates its own database session to avoid concurrent session issues.

    Args:
        symbol: Stock symbol

    Returns:
        Tuple of (signals_detected, signals_saved)
    """
    try:
        # Get OHLCV data
        ohlcv = await market_data_service.get_ohlcv_for_indicators(symbol, "200W")
        if not ohlcv:
            return 0, 0

        # Get quote for 52W data
        quote = await market_data_service.get_quote(symbol)
        high_52w = quote.high_52w if quote else None
        low_52w = quote.low_52w if quote else None

        # Detect signals
        signals = await SignalDetector.detect_all_signals(
            symbol, ohlcv, high_52w, low_52w
        )

        detected = len(signals)
        saved = 0

        # Save signals with deduplication - use per-task session
        if signals:
            async with AsyncSessionLocal() as db:
                for signal in signals:
                    result = await SignalDetector.save_signal(db, signal)
                    if result:
                        saved += 1
                        logger.info(
                            f"New signal: {symbol} - {signal.signal_type.value}",
                            extra={"extra_data": {"symbol": symbol, "signal": signal.model_dump()}},
                        )

        return detected, saved

    except Exception as e:
        logger.warning(f"Error detecting signals for {symbol}: {e}")
        return 0, 0
