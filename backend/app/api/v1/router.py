"""Main API v1 router."""

from fastapi import APIRouter

from app.api.v1 import health, screener, stock, signals, search

router = APIRouter()

# Include all endpoint routers
router.include_router(health.router, tags=["Health"])
router.include_router(screener.router, prefix="/screener", tags=["Screener"])
router.include_router(stock.router, prefix="/stock", tags=["Stock"])
router.include_router(signals.router, prefix="/signals", tags=["Signals"])
router.include_router(search.router, prefix="/search", tags=["Search"])
