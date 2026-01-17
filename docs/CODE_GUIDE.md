# Argus Code Guide

This document provides detailed explanations of key code patterns, algorithms, and implementation details. Use this as a reference when making changes to the codebase.

---

## Table of Contents

1. [Backend Code Guide](#backend-code-guide)
   - [Indicator Calculations](#indicator-calculations)
   - [Screener Logic](#screener-logic)
   - [Signal Detection](#signal-detection)
   - [Caching](#caching)
   - [API Endpoints](#api-endpoints)
2. [Frontend Code Guide](#frontend-code-guide)
   - [Component Patterns](#component-patterns)
   - [State Management](#state-management)
   - [Chart Implementation](#chart-implementation)
   - [API Integration](#api-integration)
3. [Common Tasks](#common-tasks)

---

## Backend Code Guide

### Indicator Calculations

**File**: `backend/app/core/indicators.py`

#### Moving Average Calculation

```python
# The MA period mapping converts weekly MAs to trading days
# 20 weeks × 5 trading days = 100 days
MA_PERIOD_MAP = {
    "20W": 100,
    "50W": 250,
    "100W": 500,
    "200W": 1000,
}

@staticmethod
def moving_average(
    prices: pd.Series,
    period: int,
    ma_type: MAType = MAType.SMA,
) -> pd.Series:
    """
    Calculate moving average.

    Args:
        prices: Pandas Series of prices (typically close prices)
        period: Lookback period in trading days
        ma_type: SMA (Simple) or EMA (Exponential)

    Returns:
        Series with MA values. First (period-1) values will be NaN.

    Example:
        >>> prices = pd.Series([100, 101, 102, 103, 104])
        >>> ma = IndicatorCalculator.moving_average(prices, 3, MAType.SMA)
        >>> ma.iloc[-1]  # (102 + 103 + 104) / 3 = 103
    """
    if ma_type == MAType.SMA:
        return prices.rolling(window=period, min_periods=period).mean()
    else:  # EMA
        return prices.ewm(span=period, adjust=False, min_periods=period).mean()
```

#### RSI Calculation

```python
@staticmethod
def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index.

    Formula:
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss

    The standard period is 14 days. Values:
        - Above 70: Overbought (potential sell signal)
        - Below 30: Oversold (potential buy signal)

    Implementation notes:
        - Uses simple moving average for initial RS
        - Handles division by zero (all gains or all losses)
    """
    delta = prices.diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    # Calculate average gain/loss
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss.replace(0, np.inf)  # Avoid division by zero
    rsi = 100 - (100 / (1 + rs))

    return rsi
```

#### MACD Calculation

```python
@staticmethod
def macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Components:
        1. MACD Line = Fast EMA - Slow EMA
        2. Signal Line = EMA of MACD Line
        3. Histogram = MACD Line - Signal Line

    Interpretation:
        - MACD crosses above Signal: Bullish
        - MACD crosses below Signal: Bearish
        - Histogram shows momentum strength

    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
    slow_ema = prices.ewm(span=slow_period, adjust=False).mean()

    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram
```

#### Distance from MA Calculation

```python
@classmethod
def get_ma_distance(
    cls,
    ohlcv_list: list[OHLCV],
    ma_period: str,
) -> tuple[float | None, float | None, float | None]:
    """
    Calculate how far current price is from a moving average.

    Returns:
        (current_price, ma_value, distance_percent)

        distance_percent is calculated as:
        ((current_price - ma_value) / ma_value) * 100

        - Positive: Price is above MA
        - Negative: Price is below MA
        - Near zero: Price is at MA

    Example:
        Price = 105, MA = 100
        Distance = ((105 - 100) / 100) * 100 = 5%
    """
```

---

### Screener Logic

**File**: `backend/app/core/screener.py`

#### Screening Algorithm

```python
@classmethod
async def screen(cls, db: AsyncSession, request: ScreenerRequest) -> ScreenerResponse:
    """
    Screen stocks based on MA criteria.

    Algorithm:
    1. Check cache for existing results (same filters)
    2. If cache miss:
       a. Get all stocks from universe
       b. For each stock (concurrently, max 10 at a time):
          - Fetch OHLCV data with enough history for MA
          - Calculate MA distance
          - Get current quote
       c. Filter results:
          - Distance within threshold
          - Position matches (above/below MA)
       d. Sort and paginate
       e. Cache results
    3. Return ScreenerResponse

    Concurrency control:
        Uses asyncio.Semaphore(10) to prevent overwhelming yfinance API
    """
```

#### Position Classification

```python
# A stock's position relative to its MA
def classify_position(distance_percent: float) -> str:
    """
    Classify stock position relative to MA.

    Rules:
        - Within ±0.5%: "at" (essentially at the MA)
        - Above +0.5%: "above"
        - Below -0.5%: "below"
    """
    if abs(distance_percent) < 0.5:
        return "at"
    elif distance_percent > 0:
        return "above"
    else:
        return "below"
```

---

### Signal Detection

**File**: `backend/app/core/signals.py`

#### MA Crossover Detection

```python
@staticmethod
def detect_ma_crossover(
    ohlcv_list: list[OHLCV],
    ma_period: str,
    lookback: int = 2,
) -> SignalType | None:
    """
    Detect MA crossover signals.

    Algorithm:
    1. Calculate MA for the data
    2. Look at recent bars (lookback period)
    3. Check if price crossed above or below MA

    Crossover logic:
        - Bullish: Previous close < Previous MA AND Current close > Current MA
        - Bearish: Previous close > Previous MA AND Current close < Current MA

    Args:
        ohlcv_list: Price history
        ma_period: "20W", "50W", "100W", or "200W"
        lookback: How many bars back to check (default 2)

    Returns:
        SignalType.MA_CROSSOVER_BULLISH, MA_CROSSOVER_BEARISH, or None
    """
```

#### RSI Signal Detection

```python
@staticmethod
def detect_rsi_signal(
    ohlcv_list: list[OHLCV],
    oversold_threshold: float = 30,
    overbought_threshold: float = 70,
) -> SignalType | None:
    """
    Detect RSI crossing threshold levels.

    Signal triggers when RSI CROSSES the threshold, not just when it's
    above/below. This prevents repeated signals.

    Detection logic:
        - Oversold: Previous RSI >= 30 AND Current RSI < 30
        - Overbought: Previous RSI <= 70 AND Current RSI > 70
    """
```

#### Signal Deduplication

```python
@staticmethod
async def save_signal(
    db: AsyncSession,
    signal: SignalCreate,
    dedupe_hours: int = 24,
) -> Signal | None:
    """
    Save signal with deduplication.

    Prevents duplicate signals for the same stock/type within a time window.

    Deduplication logic:
        Check if a signal with same (symbol, signal_type) exists
        within the last `dedupe_hours`. If so, skip saving.

    This prevents:
        - Repeated signals during volatile periods
        - Signal spam in the UI
    """
```

---

### Caching

**File**: `backend/app/services/cache.py`

#### Cache-Aside Pattern

```python
async def get_or_set(
    self,
    key: str,
    factory: Callable[[], Awaitable[T]],
    ttl: int,
) -> tuple[T, bool]:
    """
    Cache-aside pattern implementation.

    Flow:
    1. Try to get from cache
    2. If hit: return cached value with was_cached=True
    3. If miss:
       a. Call factory function to generate value
       b. Store in cache with TTL
       c. Return value with was_cached=False

    Usage:
        data, was_cached = await cache.get_or_set(
            key="argus:quote:AAPL",
            factory=lambda: fetch_quote("AAPL"),
            ttl=300
        )
    """
```

#### Market-Hours-Aware TTL

```python
# backend/app/cache/ttl.py

class CacheTTL:
    @classmethod
    def _get_multiplier(cls) -> int:
        """
        During market hours: return 1 (normal TTL)
        Outside market hours: return 12 (12x longer TTL)

        This reduces unnecessary API calls when market is closed
        since prices aren't changing.
        """
        if is_market_hours():
            return 1
        return settings.cache_ttl_off_hours_multiplier  # Default: 12
```

---

### API Endpoints

**File**: `backend/app/api/v1/`

#### Dependency Injection Pattern

```python
# backend/app/api/deps.py

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency.

    Usage in endpoint:
        @router.get("/endpoint")
        async def handler(db: AsyncSession = Depends(get_db)):
            # db is automatically managed
            result = await db.execute(query)
            return result

    The session is automatically closed after the request.
    """

async def get_cache() -> CacheService:
    """Returns the global cache service instance."""
    return cache_service

async def get_market_data() -> MarketDataService:
    """Returns the global market data service instance."""
    return market_data_service
```

#### Endpoint Structure

```python
# Standard endpoint pattern

@router.get("/{symbol}", response_model=StockData)
async def get_stock(
    symbol: str,                                        # Path parameter
    timeframe: TimeFrame = Query(default=TimeFrame.DAILY),  # Query with default
    period: Period = Query(default=Period.ONE_YEAR),
    market_data: MarketDataService = Depends(get_market_data),  # Injected
    cache: CacheService = Depends(get_cache),
) -> StockData:
    """
    Docstring becomes OpenAPI description.

    **Parameters:**
    - **symbol**: Stock ticker (e.g., AAPL)

    **Returns:**
    Stock data with quote and OHLCV.
    """
    symbol = symbol.upper()  # Normalize input

    # Business logic...

    return StockData(...)
```

---

## Frontend Code Guide

### Component Patterns

#### UI Component Pattern

```tsx
// frontend/src/components/ui/Button.tsx

import { ButtonHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

// 1. Define props interface extending HTML attributes
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

// 2. Use forwardRef for ref forwarding
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
    return (
      <button
        ref={ref}
        // 3. Use clsx for conditional classes
        className={clsx(
          'base-classes',
          {
            'variant-primary': variant === 'primary',
            'variant-secondary': variant === 'secondary',
          },
          className  // Allow override
        )}
        {...props}  // Spread remaining props
      />
    );
  }
);

// 4. Set displayName for debugging
Button.displayName = 'Button';
```

#### Page Component Pattern

```tsx
// frontend/src/pages/ScreenerPage.tsx

import { MainLayout } from '../components/layout/MainLayout';
import { ScreenerFilters } from '../components/screener/ScreenerFilters';
import { ScreenerResults } from '../components/screener/ScreenerResults';

export function ScreenerPage() {
  // Pages compose layout and feature components
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header section */}
        <div>
          <h1>Stock Screener</h1>
          <p>Description...</p>
        </div>

        {/* Feature components */}
        <ScreenerFilters />
        <ScreenerResults />
      </div>
    </MainLayout>
  );
}
```

#### Feature Component Pattern

```tsx
// frontend/src/components/screener/ScreenerResults.tsx

import { useScreener } from '../../hooks/useScreener';
import { LoadingState } from '../ui/Spinner';

export function ScreenerResults() {
  // 1. Use custom hook for data
  const { data, isLoading, error } = useScreener();

  // 2. Handle loading state
  if (isLoading) {
    return <LoadingState message="Loading..." />;
  }

  // 3. Handle error state
  if (error) {
    return <div className="error">Error loading data</div>;
  }

  // 4. Handle empty state
  if (!data || data.results.length === 0) {
    return <div>No results found</div>;
  }

  // 5. Render data
  return (
    <div>
      {data.results.map((item) => (
        <Row key={item.symbol} data={item} />
      ))}
    </div>
  );
}
```

---

### State Management

#### Zustand Store Pattern

```typescript
// frontend/src/stores/screenerStore.ts

import { create } from 'zustand';

// 1. Define state interface
interface ScreenerFilters {
  ma_filter: MAFilter;
  distance_pct: number;
  include_below: boolean;
  include_above: boolean;
}

// 2. Define store interface (state + actions)
interface ScreenerState {
  filters: ScreenerFilters;
  setFilter: <K extends keyof ScreenerFilters>(key: K, value: ScreenerFilters[K]) => void;
  resetFilters: () => void;
}

// 3. Define defaults
const defaultFilters: ScreenerFilters = {
  ma_filter: '20W',
  distance_pct: 5,
  include_below: true,
  include_above: true,
};

// 4. Create store
export const useScreenerStore = create<ScreenerState>((set) => ({
  filters: defaultFilters,

  // Generic setter for any filter key
  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    })),

  // Reset to defaults
  resetFilters: () => set({ filters: defaultFilters }),
}));

// 5. Usage in components
function Component() {
  const filters = useScreenerStore((state) => state.filters);
  const setFilter = useScreenerStore((state) => state.setFilter);

  return (
    <select
      value={filters.ma_filter}
      onChange={(e) => setFilter('ma_filter', e.target.value)}
    />
  );
}
```

#### React Query Hook Pattern

```typescript
// frontend/src/hooks/useScreener.ts

import { useQuery } from '@tanstack/react-query';
import { fetchScreenerResults } from '../api/screener';
import { useScreenerStore } from '../stores/screenerStore';

export function useScreener() {
  // 1. Get filter state from Zustand
  const filters = useScreenerStore((state) => state.filters);

  // 2. Create React Query hook
  return useQuery({
    // Query key includes filters for automatic refetch on change
    queryKey: ['screener', filters],

    // Query function
    queryFn: () => fetchScreenerResults(filters),

    // Refetch interval (5 minutes)
    refetchInterval: 300000,

    // Consider data fresh for half the interval
    staleTime: 150000,
  });
}

// Usage in component
function Component() {
  const { data, isLoading, error, refetch } = useScreener();
  // ...
}
```

---

### Chart Implementation

**File**: `frontend/src/components/charts/StockChart.tsx`

#### Lightweight Charts Integration

```tsx
import { useEffect, useRef } from 'react';
import { createChart, IChartApi } from 'lightweight-charts';

export function StockChart({ data }: { data: ChartData }) {
  // 1. Refs for DOM element and chart instance
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  // 2. Initialize chart on mount
  useEffect(() => {
    if (!containerRef.current) return;

    // Create chart
    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: '#1f2937' },
        textColor: '#e5e7eb',
      },
      // ... other options
    });

    chartRef.current = chart;

    // Add candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
    });

    // Handle resize
    const handleResize = () => {
      chart.applyOptions({
        width: containerRef.current!.clientWidth,
      });
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // 3. Update data when it changes
  useEffect(() => {
    if (!chartRef.current || !data.ohlcv) return;

    // Format data for Lightweight Charts
    const candleData = data.ohlcv.map((d) => ({
      time: d.timestamp.split('T')[0],  // YYYY-MM-DD format required
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    // Update series data
    candleSeriesRef.current?.setData(candleData);
  }, [data.ohlcv]);

  return <div ref={containerRef} className="w-full h-[500px]" />;
}
```

#### Adding MA Lines

```tsx
// Add MA line to chart
const addMALine = (
  chart: IChartApi,
  maData: MovingAverageResult,
  color: string
) => {
  const series = chart.addLineSeries({
    color,
    lineWidth: 2,
    priceLineVisible: false,
  });

  // Filter out null values and format
  const lineData = maData.values
    .filter((v): v is [string, number] => v[1] !== null)
    .map((v) => ({
      time: v[0].split('T')[0],
      value: v[1],
    }));

  series.setData(lineData);
  return series;
};
```

---

### API Integration

#### API Client Setup

```typescript
// frontend/src/api/client.ts

import axios from 'axios';

export const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL || ''}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Error interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log errors
    console.error('API Error:', error.response?.data?.message);
    return Promise.reject(error);
  }
);
```

#### API Function Pattern

```typescript
// frontend/src/api/screener.ts

import apiClient from './client';
import type { ScreenerResponse, ScreenerParams } from '../types/screener';

export async function fetchScreenerResults(
  params: ScreenerParams = {}
): Promise<ScreenerResponse> {
  const response = await apiClient.get<ScreenerResponse>('/screener', {
    params,
  });
  return response.data;
}
```

---

## Common Tasks

### Adding a New Technical Indicator

1. **Backend calculation** (`backend/app/core/indicators.py`):
```python
@staticmethod
def new_indicator(prices: pd.Series, period: int) -> pd.Series:
    """Calculate new indicator."""
    # Implementation
    return result

@staticmethod
def calculate_new_indicator_result(df: pd.DataFrame) -> NewIndicatorResult:
    """Calculate and return structured result."""
    # Call new_indicator(), format result
    return NewIndicatorResult(...)
```

2. **Backend model** (`backend/app/models/indicator.py`):
```python
class NewIndicatorResult(BaseModel):
    period: int
    values: list[tuple[datetime, float | None]]
    current_value: float | None
```

3. **Update IndicatorData** (`backend/app/models/indicator.py`):
```python
class IndicatorData(BaseModel):
    # ... existing
    new_indicator: NewIndicatorResult | None = None
```

4. **Update calculate_all_indicators** (`backend/app/core/indicators.py`):
```python
if include_new_indicator:
    result.new_indicator = cls.calculate_new_indicator_result(df)
```

5. **Frontend type** (`frontend/src/types/indicator.ts`):
```typescript
export interface NewIndicatorResult {
  period: number;
  values: [string, number | null][];
  current_value: number | null;
}
```

6. **Frontend visualization** (`frontend/src/components/charts/NewIndicatorPane.tsx`):
```tsx
export function NewIndicatorPane({ data }: { data: NewIndicatorResult }) {
  // Chart implementation
}
```

### Adding a New API Endpoint

1. **Create endpoint file** (`backend/app/api/v1/new_endpoint.py`):
```python
from fastapi import APIRouter, Depends
from app.api.deps import get_db

router = APIRouter()

@router.get("")
async def get_new_data(db = Depends(get_db)):
    return {"data": "..."}
```

2. **Register in router** (`backend/app/api/v1/router.py`):
```python
from app.api.v1 import new_endpoint
router.include_router(new_endpoint.router, prefix="/new", tags=["New"])
```

3. **Frontend API function** (`frontend/src/api/new.ts`):
```typescript
export async function fetchNewData(): Promise<NewResponse> {
  const response = await apiClient.get('/new');
  return response.data;
}
```

4. **Frontend hook** (`frontend/src/hooks/useNew.ts`):
```typescript
export function useNew() {
  return useQuery({
    queryKey: ['new'],
    queryFn: fetchNewData,
  });
}
```

### Adding a New Signal Type

1. **Add to enum** (`backend/app/models/signal.py`):
```python
class SignalType(str, Enum):
    # ... existing
    NEW_SIGNAL = "new_signal"
```

2. **Implement detection** (`backend/app/core/signals.py`):
```python
@staticmethod
def detect_new_signal(ohlcv_list: list[OHLCV]) -> SignalType | None:
    # Detection logic
    if condition:
        return SignalType.NEW_SIGNAL
    return None
```

3. **Add to detect_all_signals** (`backend/app/core/signals.py`):
```python
new_signal = cls.detect_new_signal(ohlcv_list)
if new_signal:
    signals.append(SignalCreate(...))
```

4. **Frontend type** (`frontend/src/types/signal.ts`):
```typescript
export type SignalType =
  | 'existing_signal'
  | 'new_signal';

export const SIGNAL_TYPE_INFO: Record<SignalType, SignalTypeInfo> = {
  // ... existing
  new_signal: {
    type: 'new_signal',
    name: 'New Signal',
    description: 'Description...',
    sentiment: 'bullish',
  },
};
```
