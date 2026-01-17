"""Screener API endpoint."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.screener import ScreenerService
from app.models.screener import (
    ScreenerRequest,
    ScreenerResponse,
    MAFilter,
    SortField,
    SortOrder,
)

router = APIRouter()


@router.get("", response_model=ScreenerResponse)
async def get_screener_results(
    ma_filter: MAFilter = Query(default=MAFilter.MA_20W, description="Moving average filter"),
    distance_pct: float = Query(default=5.0, ge=0, le=100, description="Max % distance from MA"),
    include_below: bool = Query(default=True, description="Include stocks below MA"),
    include_above: bool = Query(default=True, description="Include stocks at/above MA"),
    sort_by: SortField = Query(default=SortField.DISTANCE, description="Sort field"),
    sort_order: SortOrder = Query(default=SortOrder.ASC, description="Sort order"),
    limit: int = Query(default=100, ge=1, le=500, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
) -> ScreenerResponse:
    """Screen stocks based on moving average criteria.

    Find large-cap US stocks trading near or below specified moving averages.

    **Parameters:**
    - **ma_filter**: Which moving average to use (20W, 50W, 100W, 200W)
    - **distance_pct**: Maximum percentage distance from the MA (default 5%)
    - **include_below**: Include stocks trading below the MA
    - **include_above**: Include stocks trading at or above the MA
    - **sort_by**: Field to sort results by
    - **sort_order**: Ascending or descending sort

    **Returns:**
    List of stocks matching the criteria with price, MA value, and distance.
    """
    request = ScreenerRequest(
        ma_filter=ma_filter,
        distance_pct=distance_pct,
        include_below=include_below,
        include_above=include_above,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )

    return await ScreenerService.screen(db, request)
