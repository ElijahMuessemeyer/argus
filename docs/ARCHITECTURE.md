# Argus Architecture Documentation

## Overview

Argus is a full-stack stock screening web application built with a clear separation between backend (FastAPI/Python) and frontend (React/TypeScript). This document explains the system architecture, design decisions, and how components interact.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  CLIENT                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     React Frontend (Vite)                            │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │    │
│  │  │  Pages   │  │Components│  │  Stores  │  │   React Query    │    │    │
│  │  │          │  │          │  │ (Zustand)│  │   (Data Cache)   │    │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP/REST
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  SERVER                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      FastAPI Application                             │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                      API Layer (v1)                           │   │    │
│  │  │  /screener  │  /stock  │  /signals  │  /search  │  /health   │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                              │                                       │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                      Core Layer                               │   │    │
│  │  │  IndicatorCalculator │ ScreenerService │ SignalDetector      │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │                              │                                       │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │                    Service Layer                              │   │    │
│  │  │  MarketDataService  │  CacheService  │  Scheduler            │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                    │                          │
│                              ▼                    ▼                          │
│                    ┌──────────────┐      ┌──────────────┐                   │
│                    │   SQLite/    │      │    Redis     │                   │
│                    │  PostgreSQL  │      │    Cache     │                   │
│                    └──────────────┘      └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP
                                      ▼
                            ┌──────────────────┐
                            │    yfinance      │
                            │  (Market Data)   │
                            └──────────────────┘
```

## Backend Architecture

### Layer Overview

The backend follows a layered architecture pattern:

```
┌─────────────────────────────────────────────┐
│              API Layer (api/v1/)            │  ← HTTP endpoints, request/response handling
├─────────────────────────────────────────────┤
│              Core Layer (core/)             │  ← Business logic, calculations
├─────────────────────────────────────────────┤
│            Service Layer (services/)        │  ← External integrations, caching
├─────────────────────────────────────────────┤
│              Data Layer (db/, models/)      │  ← Database, schemas
└─────────────────────────────────────────────┘
```

### Directory Structure Explained

```
backend/app/
├── main.py              # Application entry point, lifespan management
├── config.py            # Pydantic Settings configuration
│
├── api/                 # API Layer
│   ├── deps.py          # Dependency injection (get_db, get_cache, etc.)
│   ├── middleware.py    # Request logging, timing
│   └── v1/              # API version 1
│       ├── router.py    # Main router combining all endpoints
│       ├── health.py    # Health check endpoint
│       ├── screener.py  # Screener endpoint
│       ├── stock.py     # Stock data endpoints
│       ├── signals.py   # Signals endpoint
│       └── search.py    # Search endpoint
│
├── core/                # Business Logic Layer
│   ├── indicators.py    # Technical indicator calculations (MA, RSI, MACD)
│   ├── screener.py      # Stock screening logic
│   ├── signals.py       # Signal detection algorithms
│   └── universe.py      # Stock universe management
│
├── services/            # External Services Layer
│   ├── market_data.py   # yfinance wrapper
│   ├── cache.py         # Redis abstraction
│   └── scheduler.py     # APScheduler configuration
│
├── models/              # Data Models
│   ├── stock.py         # Stock, Quote, OHLCV schemas
│   ├── indicator.py     # Indicator result schemas
│   ├── signal.py        # Signal schemas
│   ├── screener.py      # Screener request/response schemas
│   └── db.py            # SQLAlchemy ORM models
│
├── db/                  # Database
│   ├── session.py       # Session management
│   └── migrations/      # Alembic migrations
│
├── cache/               # Cache Configuration
│   ├── keys.py          # Cache key patterns
│   └── ttl.py           # TTL configuration
│
├── tasks/               # Background Tasks
│   ├── refresh_data.py  # Market data refresh task
│   └── detect_signals.py# Signal detection task
│
├── errors/              # Error Handling
│   ├── exceptions.py    # Custom exception classes
│   └── handlers.py      # FastAPI exception handlers
│
└── utils/               # Utilities
    ├── logging.py       # Structured JSON logging
    └── market_hours.py  # Market hours detection
```

### Data Flow

#### Screener Request Flow

```
1. Client Request: GET /api/v1/screener?ma_filter=20W&distance_pct=5

2. API Layer (screener.py):
   - Parse query parameters into ScreenerRequest
   - Call ScreenerService.screen()

3. Core Layer (screener.py):
   - Check cache for existing results
   - If miss: Get stock universe from UniverseManager
   - For each stock (concurrent with semaphore):
     a. Fetch OHLCV data from MarketDataService
     b. Calculate MA using IndicatorCalculator
     c. Get current quote
     d. Calculate distance from MA
   - Filter results based on criteria
   - Sort and paginate
   - Cache results

4. Service Layer:
   - MarketDataService: Fetch from yfinance
   - CacheService: Store/retrieve from Redis

5. Response: ScreenerResponse with filtered stocks
```

#### Signal Detection Flow

```
1. Scheduler triggers detect_all_signals() every 5 minutes

2. Get all symbols from UniverseManager

3. For each symbol (concurrent):
   a. Fetch OHLCV data
   b. Fetch current quote (for 52W data)
   c. Run SignalDetector.detect_all_signals():
      - Check MA crossovers (20W, 50W, 100W, 200W)
      - Check RSI oversold/overbought
      - Check MACD crossovers
      - Check 52W high/low proximity
   d. Save new signals with deduplication

4. Log summary of detected signals
```

### Key Design Patterns

#### 1. Dependency Injection

```python
# backend/app/api/deps.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Usage in endpoints
@router.get("/screener")
async def get_screener(db: AsyncSession = Depends(get_db)):
    ...
```

#### 2. Cache-Aside Pattern

```python
# backend/app/services/cache.py
async def get_or_set(self, key: str, factory: Callable, ttl: int) -> tuple[T, bool]:
    # Try cache first
    cached = await self.get(key)
    if cached is not None:
        return cached, True  # Cache hit

    # Generate value
    value = await factory()

    # Store in cache
    await self.set(key, value, ttl)

    return value, False  # Cache miss
```

#### 3. Repository Pattern (Universe Manager)

```python
# backend/app/core/universe.py
class UniverseManager:
    @staticmethod
    async def get_universe(db: AsyncSession) -> list[dict]:
        # Abstract database access
        ...

    @staticmethod
    async def add_stock(db: AsyncSession, symbol: str, ...):
        ...
```

#### 4. Strategy Pattern (Indicator Calculations)

```python
# backend/app/core/indicators.py
class IndicatorCalculator:
    @staticmethod
    def moving_average(prices: pd.Series, period: int, ma_type: MAType) -> pd.Series:
        if ma_type == MAType.SMA:
            return prices.rolling(window=period).mean()
        else:  # EMA
            return prices.ewm(span=period).mean()
```

---

## Frontend Architecture

### Directory Structure Explained

```
frontend/src/
├── main.tsx             # Application entry point
├── App.tsx              # Root component with routing
│
├── api/                 # API Client Layer
│   ├── client.ts        # Axios instance configuration
│   ├── screener.ts      # Screener API calls
│   ├── stock.ts         # Stock API calls
│   ├── signals.ts       # Signals API calls
│   └── search.ts        # Search API calls
│
├── components/          # React Components
│   ├── ui/              # Reusable UI primitives
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Toggle.tsx
│   │   ├── Badge.tsx
│   │   └── Spinner.tsx
│   ├── layout/          # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── MainLayout.tsx
│   ├── charts/          # Chart components
│   │   ├── StockChart.tsx    # Main candlestick chart
│   │   ├── ChartControls.tsx
│   │   ├── RSIPane.tsx
│   │   └── MACDPane.tsx
│   ├── screener/        # Screener components
│   │   ├── ScreenerFilters.tsx
│   │   ├── ScreenerResults.tsx
│   │   └── StockRow.tsx
│   ├── signals/         # Signal components
│   │   ├── SignalFeed.tsx
│   │   └── SignalCard.tsx
│   └── search/          # Search components
│       └── StockSearch.tsx
│
├── pages/               # Page Components
│   ├── ScreenerPage.tsx
│   ├── StockDetailPage.tsx
│   └── SignalsPage.tsx
│
├── hooks/               # Custom React Hooks
│   ├── useScreener.ts   # Screener data hook
│   ├── useStock.ts      # Stock data hooks
│   ├── useSignals.ts    # Signals data hook
│   └── useSearch.ts     # Search hook
│
├── stores/              # Zustand State Stores
│   ├── screenerStore.ts # Screener filter state
│   ├── chartStore.ts    # Chart settings state
│   └── signalStore.ts   # Signal filter state
│
├── types/               # TypeScript Types
│   ├── stock.ts         # Stock-related types
│   ├── indicator.ts     # Indicator types
│   ├── signal.ts        # Signal types
│   └── screener.ts      # Screener types
│
├── utils/               # Utility Functions
│   ├── formatters.ts    # Number/date formatting
│   └── constants.ts     # App constants
│
└── styles/
    └── globals.css      # Tailwind imports and global styles
```

### State Management

```
┌─────────────────────────────────────────────────────────────────┐
│                        State Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │  React Query     │    │  Zustand Stores  │                   │
│  │  (Server State)  │    │  (Client State)  │                   │
│  ├──────────────────┤    ├──────────────────┤                   │
│  │ • API responses  │    │ • Filter values  │                   │
│  │ • Caching        │    │ • Chart settings │                   │
│  │ • Refetching     │    │ • UI preferences │                   │
│  │ • Loading states │    │                  │                   │
│  └──────────────────┘    └──────────────────┘                   │
│           │                       │                              │
│           └───────────┬───────────┘                              │
│                       │                                          │
│                       ▼                                          │
│              ┌──────────────────┐                                │
│              │    Components    │                                │
│              └──────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
App
├── QueryClientProvider (React Query)
└── BrowserRouter
    └── Routes
        ├── ScreenerPage
        │   └── MainLayout
        │       ├── Header
        │       │   └── StockSearch
        │       ├── ScreenerFilters
        │       └── ScreenerResults
        │           └── StockRow (×n)
        │
        ├── StockDetailPage
        │   └── MainLayout
        │       ├── Header
        │       ├── Sidebar (chart controls)
        │       ├── ChartControls
        │       ├── StockChart
        │       ├── RSIPane (conditional)
        │       └── MACDPane (conditional)
        │
        └── SignalsPage
            └── MainLayout
                ├── Header
                └── SignalFeed
                    └── SignalCard (×n)
```

---

## Data Models

### Backend Models (Pydantic)

```python
# Core stock data
class OHLCV(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class Quote(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    avg_volume: int | None
    market_cap: int | None
    high_52w: float | None
    low_52w: float | None
    updated_at: datetime

# Indicator results
class MovingAverageResult(BaseModel):
    period: int
    ma_type: MAType
    values: list[tuple[datetime, float | None]]
    current_value: float | None
    distance_percent: float | None

# Screener
class ScreenerResult(BaseModel):
    symbol: str
    name: str
    price: float
    ma_value: float
    distance_percent: float
    position: Literal["above", "below", "at"]
```

### Frontend Types (TypeScript)

```typescript
// Mirrors backend models
interface OHLCV {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface Quote {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  // ...
}

// Screener types
type MAFilter = '20W' | '50W' | '100W' | '200W';
type SortField = 'symbol' | 'distance' | 'price' | 'change';
```

---

## Caching Strategy

### Cache Keys

```
Pattern                              Example
─────────────────────────────────────────────────────────────
argus:quote:{symbol}                 argus:quote:AAPL
argus:ohlcv:{symbol}:{tf}:{period}   argus:ohlcv:AAPL:1D:1Y
argus:indicators:{symbol}:{tf}       argus:indicators:AAPL:1D
argus:chart:{symbol}:{params_hash}   argus:chart:AAPL:a1b2c3d4
argus:screener:{filters_hash}        argus:screener:a1b2c3d4
argus:universe                       argus:universe
argus:search:{query_hash}            argus:search:e5f6g7h8
```

### TTL Configuration

```
Data Type          Market Hours    Off Hours
───────────────────────────────────────────────
Quotes             5 minutes       1 hour
OHLCV (daily)      1 hour          1 hour
OHLCV (weekly)     24 hours        24 hours
Indicators         5 minutes       1 hour
Chart data         5 minutes       1 hour
Screener results   5 minutes       1 hour
Stock universe     24 hours        24 hours
Search results     1 hour          1 hour
```

---

## Background Tasks

### Scheduler Configuration

```python
# Runs during market hours: Mon-Fri, 9:30 AM - 4:00 PM ET

Jobs:
├── refresh_market_data (every 5 min)
│   └── Updates quotes for all universe stocks
│
├── refresh_market_data_open (9:30 AM)
│   └── Fresh data at market open
│
├── detect_signals (every 5 min)
│   └── Scans for new trading signals
│
└── detect_signals_close (4:05 PM)
    └── Final signal check after close
```

---

## Error Handling

### Exception Hierarchy

```
ArgusError (base)
├── NotFoundError (404)
│   └── "Stock not found: XYZ"
├── ValidationError (400)
│   └── "Invalid MA filter: 30W"
├── MarketDataError (503)
│   └── "Failed to fetch data from yfinance"
├── CacheError (500)
│   └── "Redis connection failed"
└── DatabaseError (500)
    └── "Database query failed"
```

### Error Response Format

```json
{
  "error": "NotFoundError",
  "message": "Stock not found: XYZ",
  "details": {
    "resource": "Stock",
    "identifier": "XYZ"
  }
}
```

---

## Security Considerations

1. **CORS**: Configured for specific origins only
2. **Input Validation**: All inputs validated via Pydantic
3. **SQL Injection**: Prevented via SQLAlchemy ORM
4. **Rate Limiting**: yfinance has built-in limits; consider adding API rate limiting for production
5. **No Authentication**: Current version is for personal use; add auth for multi-user deployment

---

## Performance Considerations

1. **Concurrent Processing**: Screener uses asyncio.Semaphore(10) to limit concurrent yfinance calls
2. **Caching**: Redis cache with market-hours-aware TTLs
3. **Batch Operations**: Quotes fetched in batches of 20
4. **Database Indexing**: Indexes on symbol, timestamp, signal_type
5. **Frontend Optimization**: React Query caching, component memoization

---

## Extensibility Points

### Adding New Indicators

1. Add calculation method to `IndicatorCalculator`
2. Create Pydantic model in `models/indicator.py`
3. Update `calculate_all_indicators()` method
4. Add to chart endpoint response
5. Create frontend visualization component

### Adding New Signal Types

1. Add to `SignalType` enum
2. Implement detection method in `SignalDetector`
3. Update `detect_all_signals()` to call new method
4. Add to `SIGNAL_TYPE_INFO` in frontend

### Adding New Data Sources

1. Create new service in `services/`
2. Implement same interface as `MarketDataService`
3. Update dependency injection in `deps.py`
