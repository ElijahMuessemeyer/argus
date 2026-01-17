# Argus API Documentation

Base URL: `http://localhost:8000/api/v1`

## Endpoints

### Health Check

```
GET /health
```

Returns application health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2024-01-15T10:30:00Z",
  "market_open": true,
  "redis_connected": true
}
```

---

### Screener

```
GET /screener
```

Screen stocks based on moving average criteria.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `ma_filter` | string | `20W` | MA period (20W, 50W, 100W, 200W) |
| `distance_pct` | float | `5.0` | Max % distance from MA |
| `include_below` | bool | `true` | Include stocks below MA |
| `include_above` | bool | `true` | Include stocks at/above MA |
| `sort_by` | string | `distance` | Sort field |
| `sort_order` | string | `asc` | Sort order (asc, desc) |
| `limit` | int | `100` | Max results |
| `offset` | int | `0` | Pagination offset |

**Response:**
```json
{
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "sector": "Technology",
      "price": 185.50,
      "change": 2.30,
      "change_percent": 1.25,
      "market_cap": 2850000000000,
      "ma_value": 180.25,
      "ma_period": "20W",
      "distance": 5.25,
      "distance_percent": 2.91,
      "position": "above"
    }
  ],
  "total": 45,
  "filters": { ... },
  "cached": false
}
```

---

### Stock Data

```
GET /stock/{symbol}
```

Get complete stock data.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `timeframe` | string | `1D` | Chart timeframe (1D, 1W) |
| `period` | string | `1Y` | History period (3M, 6M, 1Y, 2Y, 5Y) |

**Response:**
```json
{
  "info": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "exchange": "NASDAQ",
    "market_cap": 2850000000000,
    "currency": "USD"
  },
  "quote": {
    "symbol": "AAPL",
    "price": 185.50,
    "change": 2.30,
    "change_percent": 1.25,
    "volume": 45000000,
    "avg_volume": 50000000,
    "market_cap": 2850000000000,
    "high_52w": 199.62,
    "low_52w": 124.17,
    "updated_at": "2024-01-15T16:00:00Z"
  },
  "ohlcv": [
    {
      "timestamp": "2024-01-15T00:00:00",
      "open": 183.20,
      "high": 186.00,
      "low": 182.50,
      "close": 185.50,
      "volume": 45000000
    }
  ]
}
```

---

### Stock Quote

```
GET /stock/{symbol}/quote
```

Get real-time quote only.

---

### Chart Data

```
GET /stock/{symbol}/chart
```

Get chart data with optional indicators.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `timeframe` | string | `1D` | Chart timeframe |
| `period` | string | `1Y` | History period |
| `include_ma` | bool | `true` | Include moving averages |
| `include_rsi` | bool | `false` | Include RSI |
| `include_macd` | bool | `false` | Include MACD |

---

### Signals

```
GET /signals
```

Get trading signals.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `types` | string | - | Comma-separated signal types |
| `symbols` | string | - | Comma-separated symbols |
| `hours` | int | `24` | Get signals from last N hours |
| `limit` | int | `100` | Max signals to return |

**Signal Types:**
- `ma_crossover_bullish` / `ma_crossover_bearish`
- `rsi_oversold` / `rsi_overbought`
- `macd_bullish_cross` / `macd_bearish_cross`
- `near_52w_high` / `near_52w_low`
- `new_52w_high` / `new_52w_low`

**Response:**
```json
{
  "signals": [
    {
      "id": "abc-123",
      "symbol": "AAPL",
      "signal_type": "ma_crossover_bullish",
      "timestamp": "2024-01-15T14:30:00Z",
      "price": 185.50,
      "details": {
        "ma_period": "20W"
      },
      "created_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 25,
  "filters": { ... }
}
```

---

### Search

```
GET /search
```

Search for stocks.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `q` | string | required | Search query |
| `limit` | int | `10` | Max results |

**Response:**
```json
{
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "sector": "Technology",
      "exchange": "NASDAQ",
      "in_universe": true
    }
  ],
  "query": "AAPL",
  "total": 1
}
```

---

## Error Responses

All errors follow this format:

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

**Status Codes:**
- `400` - Bad Request / Validation Error
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (market data issues)
