"""Stock universe management."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import StockUniverse
from app.services.cache import cache_service
from app.cache.keys import CacheKeys
from app.cache.ttl import CacheTTL
from app.utils.logging import get_logger

logger = get_logger("core.universe")

# Default large-cap US stocks for initial universe
# These are the S&P 500 top holdings and other major stocks
DEFAULT_UNIVERSE = [
    # Technology
    ("AAPL", "Apple Inc.", "Technology"),
    ("MSFT", "Microsoft Corporation", "Technology"),
    ("GOOGL", "Alphabet Inc.", "Technology"),
    ("AMZN", "Amazon.com Inc.", "Consumer Cyclical"),
    ("NVDA", "NVIDIA Corporation", "Technology"),
    ("META", "Meta Platforms Inc.", "Technology"),
    ("TSLA", "Tesla Inc.", "Consumer Cyclical"),
    ("AVGO", "Broadcom Inc.", "Technology"),
    ("ORCL", "Oracle Corporation", "Technology"),
    ("ADBE", "Adobe Inc.", "Technology"),
    ("CRM", "Salesforce Inc.", "Technology"),
    ("AMD", "Advanced Micro Devices", "Technology"),
    ("CSCO", "Cisco Systems Inc.", "Technology"),
    ("ACN", "Accenture plc", "Technology"),
    ("INTC", "Intel Corporation", "Technology"),
    ("IBM", "IBM Corporation", "Technology"),
    ("QCOM", "Qualcomm Inc.", "Technology"),
    ("TXN", "Texas Instruments", "Technology"),
    ("INTU", "Intuit Inc.", "Technology"),
    ("AMAT", "Applied Materials", "Technology"),
    ("NOW", "ServiceNow Inc.", "Technology"),
    ("MU", "Micron Technology", "Technology"),
    ("LRCX", "Lam Research", "Technology"),
    ("ADI", "Analog Devices", "Technology"),
    ("KLAC", "KLA Corporation", "Technology"),

    # Financials
    ("BRK-B", "Berkshire Hathaway", "Financial Services"),
    ("JPM", "JPMorgan Chase", "Financial Services"),
    ("V", "Visa Inc.", "Financial Services"),
    ("MA", "Mastercard Inc.", "Financial Services"),
    ("BAC", "Bank of America", "Financial Services"),
    ("WFC", "Wells Fargo", "Financial Services"),
    ("GS", "Goldman Sachs", "Financial Services"),
    ("MS", "Morgan Stanley", "Financial Services"),
    ("BLK", "BlackRock Inc.", "Financial Services"),
    ("SPGI", "S&P Global", "Financial Services"),
    ("AXP", "American Express", "Financial Services"),
    ("C", "Citigroup Inc.", "Financial Services"),
    ("SCHW", "Charles Schwab", "Financial Services"),
    ("PGR", "Progressive Corp.", "Financial Services"),
    ("CB", "Chubb Limited", "Financial Services"),

    # Healthcare
    ("UNH", "UnitedHealth Group", "Healthcare"),
    ("JNJ", "Johnson & Johnson", "Healthcare"),
    ("LLY", "Eli Lilly", "Healthcare"),
    ("PFE", "Pfizer Inc.", "Healthcare"),
    ("ABBV", "AbbVie Inc.", "Healthcare"),
    ("MRK", "Merck & Co.", "Healthcare"),
    ("TMO", "Thermo Fisher Scientific", "Healthcare"),
    ("ABT", "Abbott Laboratories", "Healthcare"),
    ("DHR", "Danaher Corporation", "Healthcare"),
    ("BMY", "Bristol-Myers Squibb", "Healthcare"),
    ("AMGN", "Amgen Inc.", "Healthcare"),
    ("GILD", "Gilead Sciences", "Healthcare"),
    ("ISRG", "Intuitive Surgical", "Healthcare"),
    ("VRTX", "Vertex Pharmaceuticals", "Healthcare"),
    ("REGN", "Regeneron Pharmaceuticals", "Healthcare"),

    # Consumer
    ("WMT", "Walmart Inc.", "Consumer Defensive"),
    ("PG", "Procter & Gamble", "Consumer Defensive"),
    ("KO", "Coca-Cola Company", "Consumer Defensive"),
    ("PEP", "PepsiCo Inc.", "Consumer Defensive"),
    ("COST", "Costco Wholesale", "Consumer Defensive"),
    ("HD", "Home Depot", "Consumer Cyclical"),
    ("MCD", "McDonald's Corp.", "Consumer Cyclical"),
    ("NKE", "Nike Inc.", "Consumer Cyclical"),
    ("SBUX", "Starbucks Corp.", "Consumer Cyclical"),
    ("TGT", "Target Corporation", "Consumer Cyclical"),
    ("LOW", "Lowe's Companies", "Consumer Cyclical"),
    ("TJX", "TJX Companies", "Consumer Cyclical"),
    ("BKNG", "Booking Holdings", "Consumer Cyclical"),
    ("CMG", "Chipotle Mexican Grill", "Consumer Cyclical"),
    ("ORLY", "O'Reilly Automotive", "Consumer Cyclical"),

    # Industrials
    ("CAT", "Caterpillar Inc.", "Industrials"),
    ("GE", "General Electric", "Industrials"),
    ("UNP", "Union Pacific", "Industrials"),
    ("RTX", "RTX Corporation", "Industrials"),
    ("HON", "Honeywell International", "Industrials"),
    ("BA", "Boeing Company", "Industrials"),
    ("UPS", "United Parcel Service", "Industrials"),
    ("LMT", "Lockheed Martin", "Industrials"),
    ("DE", "Deere & Company", "Industrials"),
    ("MMM", "3M Company", "Industrials"),
    ("GD", "General Dynamics", "Industrials"),
    ("ETN", "Eaton Corporation", "Industrials"),
    ("ITW", "Illinois Tool Works", "Industrials"),
    ("EMR", "Emerson Electric", "Industrials"),
    ("FDX", "FedEx Corporation", "Industrials"),

    # Energy
    ("XOM", "Exxon Mobil", "Energy"),
    ("CVX", "Chevron Corporation", "Energy"),
    ("COP", "ConocoPhillips", "Energy"),
    ("SLB", "Schlumberger", "Energy"),
    ("EOG", "EOG Resources", "Energy"),
    ("MPC", "Marathon Petroleum", "Energy"),
    ("PSX", "Phillips 66", "Energy"),
    ("VLO", "Valero Energy", "Energy"),
    ("OXY", "Occidental Petroleum", "Energy"),
    ("PXD", "Pioneer Natural Resources", "Energy"),

    # Communications
    ("DIS", "Walt Disney Company", "Communication Services"),
    ("NFLX", "Netflix Inc.", "Communication Services"),
    ("CMCSA", "Comcast Corporation", "Communication Services"),
    ("VZ", "Verizon Communications", "Communication Services"),
    ("T", "AT&T Inc.", "Communication Services"),
    ("TMUS", "T-Mobile US", "Communication Services"),
    ("CHTR", "Charter Communications", "Communication Services"),

    # Utilities & Real Estate
    ("NEE", "NextEra Energy", "Utilities"),
    ("DUK", "Duke Energy", "Utilities"),
    ("SO", "Southern Company", "Utilities"),
    ("D", "Dominion Energy", "Utilities"),
    ("AEP", "American Electric Power", "Utilities"),
    ("PLD", "Prologis Inc.", "Real Estate"),
    ("AMT", "American Tower", "Real Estate"),
    ("EQIX", "Equinix Inc.", "Real Estate"),
    ("CCI", "Crown Castle", "Real Estate"),
    ("SPG", "Simon Property Group", "Real Estate"),

    # Materials
    ("LIN", "Linde plc", "Basic Materials"),
    ("APD", "Air Products", "Basic Materials"),
    ("SHW", "Sherwin-Williams", "Basic Materials"),
    ("ECL", "Ecolab Inc.", "Basic Materials"),
    ("FCX", "Freeport-McMoRan", "Basic Materials"),
    ("NEM", "Newmont Corporation", "Basic Materials"),
    ("DOW", "Dow Inc.", "Basic Materials"),
]


class UniverseManager:
    """Manager for stock universe operations."""

    @staticmethod
    async def get_universe(db: AsyncSession) -> list[dict[str, Any]]:
        """Get all active stocks in the universe."""
        # Try cache first
        cached = await cache_service.get(CacheKeys.universe())
        if cached:
            return cached

        # Query database
        result = await db.execute(
            select(StockUniverse).where(StockUniverse.is_active == True)
        )
        stocks = result.scalars().all()

        universe = [
            {
                "symbol": s.symbol,
                "name": s.name,
                "sector": s.sector,
                "market_cap": s.market_cap,
                "exchange": s.exchange,
            }
            for s in stocks
        ]

        # Cache result
        await cache_service.set(
            CacheKeys.universe(),
            universe,
            CacheTTL.universe(),
        )

        return universe

    @staticmethod
    async def get_symbols(db: AsyncSession) -> list[str]:
        """Get list of all active symbols."""
        universe = await UniverseManager.get_universe(db)
        return [s["symbol"] for s in universe]

    @staticmethod
    async def initialize_universe(db: AsyncSession) -> int:
        """Initialize universe with default stocks."""
        count = 0

        for symbol, name, sector in DEFAULT_UNIVERSE:
            # Check if exists
            result = await db.execute(
                select(StockUniverse).where(StockUniverse.symbol == symbol)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                stock = StockUniverse(
                    symbol=symbol,
                    name=name,
                    sector=sector,
                    is_active=True,
                )
                db.add(stock)
                count += 1

        await db.commit()

        # Invalidate cache
        await cache_service.delete(CacheKeys.universe())

        logger.info(f"Initialized universe with {count} new stocks")
        return count

    @staticmethod
    async def add_stock(
        db: AsyncSession,
        symbol: str,
        name: str,
        sector: str | None = None,
        market_cap: int | None = None,
        exchange: str | None = None,
    ) -> StockUniverse:
        """Add a stock to the universe."""
        stock = StockUniverse(
            symbol=symbol.upper(),
            name=name,
            sector=sector,
            market_cap=market_cap,
            exchange=exchange,
            is_active=True,
        )
        db.add(stock)
        await db.commit()
        await db.refresh(stock)

        # Invalidate cache
        await cache_service.delete(CacheKeys.universe())

        return stock

    @staticmethod
    async def remove_stock(db: AsyncSession, symbol: str) -> bool:
        """Remove (deactivate) a stock from the universe."""
        result = await db.execute(
            select(StockUniverse).where(StockUniverse.symbol == symbol.upper())
        )
        stock = result.scalar_one_or_none()

        if not stock:
            return False

        stock.is_active = False
        await db.commit()

        # Invalidate cache
        await cache_service.delete(CacheKeys.universe())

        return True

    @staticmethod
    async def update_market_caps(
        db: AsyncSession,
        market_caps: dict[str, int],
    ) -> int:
        """Update market caps for multiple stocks."""
        count = 0

        for symbol, market_cap in market_caps.items():
            result = await db.execute(
                select(StockUniverse).where(StockUniverse.symbol == symbol.upper())
            )
            stock = result.scalar_one_or_none()

            if stock:
                stock.market_cap = market_cap
                count += 1

        await db.commit()

        # Invalidate cache
        await cache_service.delete(CacheKeys.universe())

        return count
