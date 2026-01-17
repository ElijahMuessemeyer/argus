"""Search API endpoint."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_cache, get_market_data
from app.models.db import StockUniverse
from app.services.cache import CacheService
from app.services.market_data import MarketDataService
from app.cache.keys import CacheKeys
from app.cache.ttl import CacheTTL

router = APIRouter()


class SearchResult(BaseModel):
    """Single search result."""

    symbol: str
    name: str
    sector: str | None = None
    exchange: str | None = None
    in_universe: bool = False


class SearchResponse(BaseModel):
    """Search API response."""

    results: list[SearchResult]
    query: str
    total: int


@router.get("", response_model=SearchResponse)
async def search_stocks(
    q: str = Query(min_length=1, max_length=20, description="Search query"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results"),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
    market_data: MarketDataService = Depends(get_market_data),
) -> SearchResponse:
    """Search for stocks by symbol or name.

    **Parameters:**
    - **q**: Search query (symbol or company name)
    - **limit**: Maximum results to return

    **Returns:**
    List of matching stocks with symbol, name, and sector.
    """
    query = q.strip().upper()

    # Check cache
    cache_key = CacheKeys.search(query)
    cached = await cache.get(cache_key)

    if cached:
        return SearchResponse(
            results=[SearchResult(**r) for r in cached["results"]],
            query=q,
            total=cached["total"],
        )

    results: list[SearchResult] = []

    # First, search in our universe (faster)
    stmt = select(StockUniverse).where(
        StockUniverse.is_active == True,
        (
            StockUniverse.symbol.ilike(f"%{query}%") |
            StockUniverse.name.ilike(f"%{query}%")
        )
    ).limit(limit)

    db_result = await db.execute(stmt)
    stocks = db_result.scalars().all()

    for stock in stocks:
        results.append(SearchResult(
            symbol=stock.symbol,
            name=stock.name,
            sector=stock.sector,
            exchange=stock.exchange,
            in_universe=True,
        ))

    # If we need more results, try external search
    if len(results) < limit:
        # Check if exact symbol match exists
        if query not in [r.symbol for r in results]:
            external = await market_data.search_symbols(query, limit - len(results))
            for item in external:
                if item["symbol"] not in [r.symbol for r in results]:
                    results.append(SearchResult(
                        symbol=item["symbol"],
                        name=item.get("name", ""),
                        exchange=item.get("exchange"),
                        in_universe=False,
                    ))

    # Sort: exact matches first, then alphabetically
    results.sort(key=lambda r: (
        0 if r.symbol == query else 1,
        0 if r.symbol.startswith(query) else 1,
        r.symbol,
    ))

    results = results[:limit]

    # Cache results
    cache_data = {
        "results": [r.model_dump() for r in results],
        "total": len(results),
    }
    await cache.set(cache_key, cache_data, CacheTTL.search())

    return SearchResponse(
        results=results,
        query=q,
        total=len(results),
    )
