"""Market data service using yfinance."""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
import yfinance as yf

from app.config import get_settings
from app.models.stock import OHLCV, Quote, StockInfo, Period, TimeFrame
from app.utils.logging import get_logger

logger = get_logger("services.market_data")

# Period to yfinance period mapping
PERIOD_MAP = {
    Period.THREE_MONTHS: "3mo",
    Period.SIX_MONTHS: "6mo",
    Period.ONE_YEAR: "1y",
    Period.TWO_YEARS: "2y",
    Period.FIVE_YEARS: "5y",
    Period.MAX: "max",
}

# For MA calculations we need sufficient history
# 200W MA = 1000 trading days, so we need max period
MA_PERIOD_MAP = {
    "20W": 100,   # 100 trading days
    "50W": 250,   # 250 trading days
    "100W": 500,  # 500 trading days
    "200W": 1000, # 1000 trading days
}


class MarketDataService:
    """Service for fetching market data from yfinance."""

    def __init__(self):
        self.settings = get_settings()

    async def get_quote(self, symbol: str) -> Quote | None:
        """Get real-time quote for a symbol."""
        try:
            timeout = self.settings.market_data_timeout
            return await asyncio.wait_for(
                asyncio.to_thread(self._get_quote_sync, symbol),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Quote timeout for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None

    @staticmethod
    def _get_quote_sync(symbol: str) -> Quote | None:
        """Blocking quote fetch using yfinance."""
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info or "regularMarketPrice" not in info:
            logger.warning(f"No quote data for {symbol}")
            return None

        price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
        prev_close = info.get("regularMarketPreviousClose", price)
        change = price - prev_close if prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0

        return Quote(
            symbol=symbol.upper(),
            price=price,
            change=round(change, 2),
            change_percent=round(change_pct, 2),
            volume=info.get("regularMarketVolume", 0) or 0,
            avg_volume=info.get("averageVolume"),
            market_cap=info.get("marketCap"),
            high_52w=info.get("fiftyTwoWeekHigh"),
            low_52w=info.get("fiftyTwoWeekLow"),
            updated_at=datetime.now(timezone.utc),
        )

    async def get_stock_info(self, symbol: str) -> StockInfo | None:
        """Get basic stock information."""
        try:
            timeout = self.settings.market_data_timeout
            return await asyncio.wait_for(
                asyncio.to_thread(self._get_stock_info_sync, symbol),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Stock info timeout for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            return None

    @staticmethod
    def _get_stock_info_sync(symbol: str) -> StockInfo | None:
        """Blocking stock info fetch using yfinance."""
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info or "shortName" not in info:
            logger.warning(f"No info for {symbol}")
            return None

        return StockInfo(
            symbol=symbol.upper(),
            name=info.get("shortName") or info.get("longName", symbol),
            sector=info.get("sector"),
            industry=info.get("industry"),
            exchange=info.get("exchange"),
            market_cap=info.get("marketCap"),
            currency=info.get("currency", "USD"),
        )

    async def get_ohlcv(
        self,
        symbol: str,
        period: Period = Period.ONE_YEAR,
        timeframe: TimeFrame = TimeFrame.DAILY,
    ) -> list[OHLCV]:
        """Get OHLCV data for a symbol."""
        try:
            timeout = self.settings.market_data_timeout
            return await asyncio.wait_for(
                asyncio.to_thread(self._get_ohlcv_sync, symbol, period, timeframe),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(f"OHLCV timeout for {symbol}")
            return []
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return []

    @staticmethod
    def _get_ohlcv_sync(
        symbol: str,
        period: Period,
        timeframe: TimeFrame,
    ) -> list[OHLCV]:
        """Blocking OHLCV fetch using yfinance."""
        ticker = yf.Ticker(symbol)
        yf_period = PERIOD_MAP.get(period, "1y")

        # Determine interval based on timeframe
        interval = "1d" if timeframe == TimeFrame.DAILY else "1wk"

        history = ticker.history(period=yf_period, interval=interval)

        if history.empty:
            logger.warning(f"No OHLCV data for {symbol}")
            return []

        ohlcv_list = []
        for idx, row in history.iterrows():
            ohlcv_list.append(
                OHLCV(
                    timestamp=idx.to_pydatetime(),
                    open=round(row["Open"], 2),
                    high=round(row["High"], 2),
                    low=round(row["Low"], 2),
                    close=round(row["Close"], 2),
                    volume=int(row["Volume"]),
                )
            )

        return ohlcv_list

    async def get_ohlcv_for_indicators(
        self,
        symbol: str,
        ma_period: str = "200W",
        full_history: bool = False,
    ) -> list[OHLCV]:
        """Get sufficient OHLCV data for indicator calculations."""
        try:
            timeout = self.settings.market_data_timeout
            return await asyncio.wait_for(
                asyncio.to_thread(self._get_ohlcv_for_indicators_sync, symbol, ma_period, full_history),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Indicator OHLCV timeout for {symbol}")
            return []
        except Exception as e:
            logger.error(f"Error fetching OHLCV for indicators for {symbol}: {e}")
            return []

    @staticmethod
    def _get_ohlcv_for_indicators_sync(
        symbol: str,
        ma_period: str,
        full_history: bool,
    ) -> list[OHLCV]:
        """Blocking OHLCV fetch for indicators using yfinance."""
        ticker = yf.Ticker(symbol)

        # Get enough history for the MA period plus buffer
        days_needed = MA_PERIOD_MAP.get(ma_period, 1000) + 50

        # yfinance max is about 10 years of daily data
        history = ticker.history(period="max", interval="1d")

        if history.empty:
            logger.warning(f"No OHLCV data for {symbol}")
            return []

        # Take only what we need unless full history requested
        if not full_history:
            history = history.tail(days_needed)

        ohlcv_list = []
        for idx, row in history.iterrows():
            ohlcv_list.append(
                OHLCV(
                    timestamp=idx.to_pydatetime(),
                    open=round(row["Open"], 2),
                    high=round(row["High"], 2),
                    low=round(row["Low"], 2),
                    close=round(row["Close"], 2),
                    volume=int(row["Volume"]),
                )
            )

        return ohlcv_list
    async def search_symbols(
        self,
        query: str,
        limit: int = 10,
        timeout_seconds: float | None = None,
    ) -> list[dict[str, Any]]:
        """Search for stock symbols."""
        try:
            timeout = timeout_seconds or self.settings.market_data_timeout
            return await asyncio.wait_for(
                asyncio.to_thread(self._search_symbols_sync, query, limit),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Search timeout for {query}")
            return []
        except Exception as e:
            logger.error(f"Error searching for {query}: {e}")
            return []

    @staticmethod
    def _search_symbols_sync(query: str, limit: int) -> list[dict[str, Any]]:
        """Blocking symbol search using yfinance."""
        results = []

        # Try direct symbol lookup first
        ticker = yf.Ticker(query.upper())
        info = ticker.info

        if info and "shortName" in info:
            results.append({
                "symbol": query.upper(),
                "name": info.get("shortName") or info.get("longName", ""),
                "exchange": info.get("exchange", ""),
                "type": info.get("quoteType", ""),
            })

        return results[:limit]

    async def get_batch_quotes(
        self,
        symbols: list[str],
    ) -> dict[str, Quote | None]:
        """Get quotes for multiple symbols efficiently."""
        try:
            timeout = self.settings.market_data_timeout
            return await asyncio.wait_for(
                asyncio.to_thread(self._get_batch_quotes_sync, symbols),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning("Batch quote timeout")
            return {symbol.upper(): None for symbol in symbols}
        except Exception as e:
            logger.error(f"Error fetching batch quotes: {e}")
            return {symbol.upper(): None for symbol in symbols}

    @staticmethod
    def _get_batch_quotes_sync(
        symbols: list[str],
    ) -> dict[str, Quote | None]:
        """Blocking batch quote fetch using yfinance."""
        results: dict[str, Quote | None] = {}

        # yfinance supports batch downloads
        try:
            tickers = yf.Tickers(" ".join(symbols))

            for symbol in symbols:
                try:
                    ticker = tickers.tickers.get(symbol.upper())
                    if ticker:
                        info = ticker.info
                        if info and "regularMarketPrice" in info:
                            price = info.get("regularMarketPrice") or info.get("currentPrice", 0)
                            prev_close = info.get("regularMarketPreviousClose", price)
                            change = price - prev_close if prev_close else 0
                            change_pct = (change / prev_close * 100) if prev_close else 0

                            results[symbol.upper()] = Quote(
                                symbol=symbol.upper(),
                                price=price,
                                change=round(change, 2),
                                change_percent=round(change_pct, 2),
                                volume=info.get("regularMarketVolume", 0) or 0,
                                avg_volume=info.get("averageVolume"),
                                market_cap=info.get("marketCap"),
                                high_52w=info.get("fiftyTwoWeekHigh"),
                                low_52w=info.get("fiftyTwoWeekLow"),
                                updated_at=datetime.now(timezone.utc),
                            )
                        else:
                            results[symbol.upper()] = None
                    else:
                        results[symbol.upper()] = None
                except Exception as e:
                    logger.warning(f"Error getting quote for {symbol}: {e}")
                    results[symbol.upper()] = None

        except Exception as e:
            logger.error(f"Error fetching batch quotes: {e}")
            for symbol in symbols:
                results[symbol.upper()] = None

        return results


# Global service instance
market_data_service = MarketDataService()


async def get_market_data() -> MarketDataService:
    """Dependency for getting market data service."""
    return market_data_service
