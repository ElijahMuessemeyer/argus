# Backend Reference

Complete reference for all backend modules, classes, and functions.

---

## API Endpoints (`app/api/v1/`)

### Health Check

```python
# GET /api/v1/health
# Returns application health status

Response:
{
    "status": "healthy",
    "version": "0.1.0",
    "environment": "development",
    "timestamp": "2024-01-15T10:30:00Z",
    "market_open": true,
    "redis_connected": true
}
```

### Screener

```python
# GET /api/v1/screener
# Screen stocks based on MA criteria

Parameters:
    ma_filter: str = "20W"      # 20W, 50W, 100W, 200W
    distance_pct: float = 5.0   # 0-100
    include_below: bool = True
    include_above: bool = True
    sort_by: str = "distance"   # symbol, name, price, distance, market_cap, change
    sort_order: str = "asc"     # asc, desc
    limit: int = 100            # 1-500
    offset: int = 0

Response: ScreenerResponse
    results: list[ScreenerResult]
    total: int
    filters: ScreenerRequest
    cached: bool
```

### Stock Data

```python
# GET /api/v1/stock/{symbol}
# Get complete stock data

Parameters:
    symbol: str (path)
    timeframe: str = "1D"  # 1D, 1W
    period: str = "1Y"     # 3M, 6M, 1Y, 2Y, 5Y

Response: StockData
    info: StockInfo
    quote: Quote
    ohlcv: list[OHLCV]

# GET /api/v1/stock/{symbol}/quote
# Get real-time quote only

Response: Quote

# GET /api/v1/stock/{symbol}/chart
# Get chart data with indicators

Parameters:
    timeframe: str = "1D"
    period: str = "1Y"
    include_ma: bool = True
    include_rsi: bool = False
    include_macd: bool = False

Response: ChartData
    symbol: str
    timeframe: str
    period: str
    ohlcv: list[OHLCV]
    indicators: dict

# GET /api/v1/stock/{symbol}/indicators
# Get all technical indicators

Response: IndicatorData
```

### Signals

```python
# GET /api/v1/signals
# Get trading signals

Parameters:
    types: str = None     # Comma-separated signal types
    symbols: str = None   # Comma-separated symbols
    hours: int = 24       # 1-168
    limit: int = 100      # 1-500

Response: SignalsResponse
    signals: list[Signal]
    total: int
    filters: dict

# GET /api/v1/signals/types
# Get all signal type definitions

Response: dict with signal_types list
```

### Search

```python
# GET /api/v1/search
# Search for stocks

Parameters:
    q: str (required)  # Search query (1-20 chars)
    limit: int = 10    # 1-50

Response: SearchResponse
    results: list[SearchResult]
    query: str
    total: int
```

---

## Core Modules (`app/core/`)

### IndicatorCalculator

```python
from app.core.indicators import IndicatorCalculator

# Class with static methods for technical indicator calculations.
# All methods are pure functions with no side effects.

# Convert OHLCV list to DataFrame
df = IndicatorCalculator.ohlcv_to_dataframe(ohlcv_list)

# Calculate moving average
ma_series = IndicatorCalculator.moving_average(
    prices=df["close"],  # pd.Series
    period=100,          # int
    ma_type=MAType.SMA,  # SMA or EMA
)
# Returns: pd.Series with MA values

# Calculate MA with structured result
ma_result = IndicatorCalculator.calculate_ma_result(
    df=df,      # DataFrame with OHLCV
    period=100,
    ma_type=MAType.SMA,
)
# Returns: MovingAverageResult
#   .period: int
#   .ma_type: MAType
#   .values: list[tuple[datetime, float | None]]
#   .current_value: float | None
#   .distance_percent: float | None

# Calculate RSI
rsi_series = IndicatorCalculator.rsi(
    prices=df["close"],
    period=14,
)
# Returns: pd.Series with RSI values (0-100)

# Calculate RSI with structured result
rsi_result = IndicatorCalculator.calculate_rsi_result(
    df=df,
    period=14,
)
# Returns: RSIResult
#   .period: int
#   .values: list[tuple]
#   .current_value: float | None
#   .is_overbought: bool
#   .is_oversold: bool

# Calculate MACD
macd_line, signal_line, histogram = IndicatorCalculator.macd(
    prices=df["close"],
    fast_period=12,
    slow_period=26,
    signal_period=9,
)
# Returns: tuple of 3 pd.Series

# Calculate all indicators at once
indicators = IndicatorCalculator.calculate_all_indicators(
    symbol="AAPL",
    ohlcv_list=ohlcv_list,
    include_ma=True,
    include_rsi=True,
    include_macd=True,
)
# Returns: IndicatorData
#   .symbol: str
#   .ma_20w: MovingAverageResult | None
#   .ma_50w: MovingAverageResult | None
#   .ma_100w: MovingAverageResult | None
#   .ma_200w: MovingAverageResult | None
#   .rsi: RSIResult | None
#   .macd: MACDResult | None

# Get distance from specific MA
current_price, ma_value, distance_pct = IndicatorCalculator.get_ma_distance(
    ohlcv_list=ohlcv_list,
    ma_period="20W",  # 20W, 50W, 100W, 200W
)
# Returns: tuple of 3 floats or Nones
```

### ScreenerService

```python
from app.core.screener import ScreenerService

# Main screener logic
response = await ScreenerService.screen(
    db=db,                    # AsyncSession
    request=ScreenerRequest(  # Filter parameters
        ma_filter=MAFilter.MA_20W,
        distance_pct=5.0,
        include_below=True,
        include_above=True,
        sort_by=SortField.DISTANCE,
        sort_order=SortOrder.ASC,
        limit=100,
        offset=0,
    ),
)
# Returns: ScreenerResponse
#   .results: list[ScreenerResult]
#   .total: int
#   .filters: ScreenerRequest
#   .cached: bool
```

### SignalDetector

```python
from app.core.signals import SignalDetector

# Detect MA crossover
signal_type = SignalDetector.detect_ma_crossover(
    ohlcv_list=ohlcv_list,
    ma_period="20W",
    lookback=2,  # Check last N bars
)
# Returns: SignalType.MA_CROSSOVER_BULLISH, MA_CROSSOVER_BEARISH, or None

# Detect RSI signal
signal_type = SignalDetector.detect_rsi_signal(
    ohlcv_list=ohlcv_list,
    oversold_threshold=30,
    overbought_threshold=70,
)
# Returns: SignalType.RSI_OVERSOLD, RSI_OVERBOUGHT, or None

# Detect MACD signal
signal_type = SignalDetector.detect_macd_signal(ohlcv_list)
# Returns: SignalType.MACD_BULLISH_CROSS, MACD_BEARISH_CROSS, or None

# Detect 52-week signals
signals = SignalDetector.detect_52w_signals(
    current_price=185.50,
    high_52w=199.62,
    low_52w=124.17,
    threshold_pct=5.0,
)
# Returns: list[SignalType] - can contain multiple signals

# Detect all signals for a stock
signals = await SignalDetector.detect_all_signals(
    symbol="AAPL",
    ohlcv_list=ohlcv_list,
    high_52w=199.62,
    low_52w=124.17,
)
# Returns: list[SignalCreate]

# Save signal with deduplication
signal = await SignalDetector.save_signal(
    db=db,
    signal=SignalCreate(...),
    dedupe_hours=24,  # Skip if same signal in last 24h
)
# Returns: Signal | None (None if duplicate)

# Get signals with filters
signals = await SignalDetector.get_signals(
    db=db,
    types=[SignalType.MA_CROSSOVER_BULLISH],  # Optional
    symbols=["AAPL", "MSFT"],                  # Optional
    since=datetime.utcnow() - timedelta(hours=24),  # Optional
    limit=100,
)
# Returns: list[Signal]
```

### UniverseManager

```python
from app.core.universe import UniverseManager

# Get all active stocks in universe
universe = await UniverseManager.get_universe(db)
# Returns: list[dict] with symbol, name, sector, market_cap, exchange

# Get just symbols
symbols = await UniverseManager.get_symbols(db)
# Returns: list[str]

# Initialize with default stocks (first run)
count = await UniverseManager.initialize_universe(db)
# Returns: int (number of stocks added)

# Add a stock
stock = await UniverseManager.add_stock(
    db=db,
    symbol="NEW",
    name="New Stock Inc.",
    sector="Technology",
    market_cap=1000000000,
    exchange="NASDAQ",
)
# Returns: StockUniverse

# Remove (deactivate) a stock
success = await UniverseManager.remove_stock(db, "OLD")
# Returns: bool

# Update market caps
count = await UniverseManager.update_market_caps(
    db=db,
    market_caps={"AAPL": 2850000000000, "MSFT": 2700000000000},
)
# Returns: int (number updated)
```

---

## Services (`app/services/`)

### MarketDataService

```python
from app.services.market_data import MarketDataService, market_data_service

# Global instance available
service = market_data_service

# Get real-time quote
quote = await service.get_quote("AAPL")
# Returns: Quote | None

# Get stock info
info = await service.get_stock_info("AAPL")
# Returns: StockInfo | None

# Get OHLCV data
ohlcv = await service.get_ohlcv(
    symbol="AAPL",
    period=Period.ONE_YEAR,      # 3M, 6M, 1Y, 2Y, 5Y
    timeframe=TimeFrame.DAILY,   # DAILY, WEEKLY
)
# Returns: list[OHLCV]

# Get OHLCV with enough history for indicators
ohlcv = await service.get_ohlcv_for_indicators(
    symbol="AAPL",
    ma_period="200W",  # Gets enough data for 200W MA
)
# Returns: list[OHLCV]

# Search symbols
results = await service.search_symbols(
    query="AAPL",
    limit=10,
)
# Returns: list[dict] with symbol, name, exchange, type

# Batch get quotes (more efficient for multiple stocks)
quotes = await service.get_batch_quotes(["AAPL", "MSFT", "GOOGL"])
# Returns: dict[str, Quote | None]
```

### CacheService

```python
from app.services.cache import CacheService, cache_service

# Global instance available
cache = cache_service

# Connect to Redis (called at startup)
await cache.connect()

# Disconnect (called at shutdown)
await cache.disconnect()

# Check connection
if cache.is_connected:
    ...

# Get value
value = await cache.get("argus:quote:AAPL")
# Returns: Any | None (deserialized from JSON)

# Set value with TTL
success = await cache.set(
    key="argus:quote:AAPL",
    value={"price": 185.50, ...},
    ttl=300,  # seconds
)
# Returns: bool

# Delete key
success = await cache.delete("argus:quote:AAPL")
# Returns: bool

# Delete by pattern
count = await cache.delete_pattern("argus:screener:*")
# Returns: int (number of keys deleted)

# Get or set (cache-aside pattern)
value, was_cached = await cache.get_or_set(
    key="argus:quote:AAPL",
    factory=lambda: fetch_quote("AAPL"),  # Async callable
    ttl=300,
)
# Returns: tuple[T, bool]
```

### Scheduler

```python
from app.services.scheduler import scheduler, setup_scheduler, start_scheduler, shutdown_scheduler

# Configure scheduler (called at startup)
setup_scheduler()

# Start scheduler
start_scheduler()

# Shutdown gracefully
shutdown_scheduler()

# Jobs configured:
# - refresh_market_data: Every 5 min, Mon-Fri, 9:30 AM - 4:00 PM ET
# - refresh_market_data_open: 9:30 AM ET, Mon-Fri
# - detect_signals: Every 5 min, Mon-Fri, 9:30 AM - 4:00 PM ET
# - detect_signals_close: 4:05 PM ET, Mon-Fri
```

---

## Models (`app/models/`)

### Stock Models

```python
from app.models.stock import OHLCV, Quote, StockInfo, StockData, ChartData

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

class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: str | None
    industry: str | None
    exchange: str | None
    market_cap: int | None
    currency: str = "USD"

class StockData(BaseModel):
    info: StockInfo
    quote: Quote
    ohlcv: list[OHLCV]

class ChartData(BaseModel):
    symbol: str
    timeframe: TimeFrame
    period: Period
    ohlcv: list[OHLCV]
    indicators: dict[str, Any]
```

### Indicator Models

```python
from app.models.indicator import MovingAverageResult, RSIResult, MACDResult, IndicatorData, MAType

class MAType(str, Enum):
    SMA = "SMA"
    EMA = "EMA"

class MovingAverageResult(BaseModel):
    period: int
    ma_type: MAType
    values: list[tuple[datetime, float | None]]
    current_value: float | None
    current_price: float | None
    distance_percent: float | None

class RSIResult(BaseModel):
    period: int
    values: list[tuple[datetime, float | None]]
    current_value: float | None
    is_overbought: bool
    is_oversold: bool

class MACDResult(BaseModel):
    fast_period: int
    slow_period: int
    signal_period: int
    macd_line: list[tuple[datetime, float | None]]
    signal_line: list[tuple[datetime, float | None]]
    histogram: list[tuple[datetime, float | None]]
    current_macd: float | None
    current_signal: float | None
    current_histogram: float | None

class IndicatorData(BaseModel):
    symbol: str
    ma_20w: MovingAverageResult | None
    ma_50w: MovingAverageResult | None
    ma_100w: MovingAverageResult | None
    ma_200w: MovingAverageResult | None
    rsi: RSIResult | None
    macd: MACDResult | None
```

### Signal Models

```python
from app.models.signal import Signal, SignalType, SignalCreate

class SignalType(str, Enum):
    MA_CROSSOVER_BULLISH = "ma_crossover_bullish"
    MA_CROSSOVER_BEARISH = "ma_crossover_bearish"
    RSI_OVERSOLD = "rsi_oversold"
    RSI_OVERBOUGHT = "rsi_overbought"
    MACD_BULLISH_CROSS = "macd_bullish_cross"
    MACD_BEARISH_CROSS = "macd_bearish_cross"
    NEAR_52W_HIGH = "near_52w_high"
    NEAR_52W_LOW = "near_52w_low"
    NEW_52W_HIGH = "new_52w_high"
    NEW_52W_LOW = "new_52w_low"

class SignalCreate(BaseModel):
    symbol: str
    signal_type: SignalType
    price: float
    details: dict[str, Any] = {}

class Signal(BaseModel):
    id: UUID
    symbol: str
    signal_type: SignalType
    timestamp: datetime
    price: float
    details: dict[str, Any]
    created_at: datetime

    @property
    def is_bullish(self) -> bool: ...
    @property
    def is_bearish(self) -> bool: ...
```

### Screener Models

```python
from app.models.screener import ScreenerRequest, ScreenerResult, ScreenerResponse, MAFilter

class MAFilter(str, Enum):
    MA_20W = "20W"
    MA_50W = "50W"
    MA_100W = "100W"
    MA_200W = "200W"

class SortField(str, Enum):
    SYMBOL = "symbol"
    NAME = "name"
    PRICE = "price"
    DISTANCE = "distance"
    MARKET_CAP = "market_cap"
    CHANGE = "change"

class ScreenerRequest(BaseModel):
    ma_filter: MAFilter = MAFilter.MA_20W
    distance_pct: float = Field(default=5.0, ge=0, le=100)
    include_below: bool = True
    include_above: bool = True
    sort_by: SortField = SortField.DISTANCE
    sort_order: SortOrder = SortOrder.ASC
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)

class ScreenerResult(BaseModel):
    symbol: str
    name: str
    sector: str | None
    price: float
    change: float
    change_percent: float
    market_cap: int | None
    ma_value: float
    ma_period: str
    distance: float
    distance_percent: float
    position: str  # "above", "below", "at"

class ScreenerResponse(BaseModel):
    results: list[ScreenerResult]
    total: int
    filters: ScreenerRequest
    cached: bool = False
    cache_timestamp: str | None = None
```

### Database Models (ORM)

```python
from app.models.db import Base, StockUniverse, SignalRecord, ErrorLog

class StockUniverse(Base):
    __tablename__ = "stock_universe"

    symbol: str          # Primary key
    name: str
    sector: str | None
    industry: str | None
    market_cap: int | None
    exchange: str | None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class SignalRecord(Base):
    __tablename__ = "signals"

    id: str              # Primary key (UUID)
    symbol: str          # Indexed
    signal_type: str     # Indexed
    timestamp: datetime  # Indexed
    price: Decimal
    details: dict        # JSON
    created_at: datetime

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id: int              # Primary key (auto)
    timestamp: datetime  # Indexed
    level: str
    component: str       # Indexed
    message: str
    details: dict | None # JSON
    stack_trace: str | None
```

---

## Utilities (`app/utils/`)

### Logging

```python
from app.utils.logging import setup_logging, get_logger, LogContext

# Initialize logging (called at startup)
setup_logging()

# Get logger for a module
logger = get_logger("my_module")
# Creates logger named "argus.my_module"

# Standard logging
logger.info("Message")
logger.warning("Warning")
logger.error("Error", exc_info=True)

# With extra fields (for JSON logging)
logger.info(
    "Operation completed",
    extra={"extra_data": {"symbol": "AAPL", "duration_ms": 150}}
)

# Using LogContext for consistent extra fields
with LogContext(logger, symbol="AAPL", operation="fetch") as ctx:
    ctx.info("Starting fetch")
    ctx.error("Fetch failed", error_code=500)
```

### Market Hours

```python
from app.utils.market_hours import (
    is_market_hours,
    is_trading_day,
    get_eastern_now,
    get_next_market_open,
    seconds_until_market_open,
    get_cache_ttl_multiplier,
)

# Check if market is currently open (Mon-Fri, 9:30 AM - 4:00 PM ET)
if is_market_hours():
    ...

# Check if today is a trading day (Mon-Fri)
if is_trading_day():
    ...

# Get current time in Eastern timezone
now = get_eastern_now()

# Get next market open time
next_open = get_next_market_open()

# Seconds until market opens (None if already open)
seconds = seconds_until_market_open()

# TTL multiplier (1 during market hours, 12 outside)
multiplier = get_cache_ttl_multiplier()
```

---

## Cache (`app/cache/`)

### Cache Keys

```python
from app.cache.keys import CacheKeys

# Generate cache keys
key = CacheKeys.quote("AAPL")           # "argus:quote:AAPL"
key = CacheKeys.ohlcv("AAPL", "1D", "1Y") # "argus:ohlcv:AAPL:1D:1Y"
key = CacheKeys.indicators("AAPL", "1D")  # "argus:indicators:AAPL:1D"
key = CacheKeys.screener({"ma_filter": "20W"})  # "argus:screener:a1b2c3d4"
key = CacheKeys.universe()               # "argus:universe"
key = CacheKeys.stock_info("AAPL")        # "argus:info:AAPL"
key = CacheKeys.search("AAPL")            # "argus:search:e5f6g7h8"
```

### Cache TTL

```python
from app.cache.ttl import CacheTTL

# Get TTL for different data types (market-hours-aware)
ttl = CacheTTL.quote()        # 300 during market, 3600 off-hours
ttl = CacheTTL.ohlcv_daily()  # 3600 (always)
ttl = CacheTTL.ohlcv_weekly() # 86400 (always)
ttl = CacheTTL.indicators()   # 300 during market, 3600 off-hours
ttl = CacheTTL.screener()     # 300 during market, 3600 off-hours
ttl = CacheTTL.universe()     # 86400 (always)
ttl = CacheTTL.stock_info()   # 86400 (always)
ttl = CacheTTL.search()       # 3600 (always)
```

---

## Errors (`app/errors/`)

### Exception Classes

```python
from app.errors.exceptions import (
    ArgusError,      # Base exception
    NotFoundError,   # 404
    ValidationError, # 400
    MarketDataError, # 503
    CacheError,      # 500
    DatabaseError,   # 500
)

# All exceptions have:
#   .message: str
#   .details: dict
#   .status_code: int

# Usage
raise NotFoundError("Stock", "XYZ")
# message: "Stock not found: XYZ"
# status_code: 404
# details: {"resource": "Stock", "identifier": "XYZ"}

raise ValidationError("Invalid MA filter", field="ma_filter")
raise MarketDataError("yfinance timeout", symbol="AAPL")
```

---

## Configuration (`app/config.py`)

```python
from app.config import get_settings, Settings

settings = get_settings()  # Cached singleton

# Available settings (from environment/.env):
settings.app_name            # "Argus"
settings.app_version         # "0.1.0"
settings.debug               # False
settings.environment         # "development"
settings.api_v1_prefix       # "/api/v1"
settings.database_url        # "sqlite:///./argus.db"
settings.redis_url           # "redis://localhost:6379"
settings.redis_enabled       # True
settings.cache_ttl_quote     # 300
settings.cache_ttl_ohlcv_daily    # 3600
settings.cache_ttl_ohlcv_weekly   # 86400
settings.cache_ttl_indicators     # 300
settings.cache_ttl_screener       # 300
settings.cache_ttl_universe       # 86400
settings.cache_ttl_off_hours_multiplier  # 12
settings.market_data_timeout      # 30
settings.market_data_max_retries  # 3
settings.scheduler_enabled        # True
settings.refresh_interval_minutes # 5
settings.log_level           # "INFO"
settings.log_format          # "json"
settings.cors_origins        # ["http://localhost:5173"]
```
