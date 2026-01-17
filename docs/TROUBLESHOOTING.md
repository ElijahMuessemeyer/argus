# Troubleshooting Guide

This guide covers common issues and their solutions when working with Argus.

---

## Quick Diagnostics

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check if Redis is running
redis-cli ping

# Check Python version
python --version  # Should be 3.11+

# Check Node version
node --version  # Should be 18+

# Check if ports are in use
lsof -i :8000  # Backend port
lsof -i :5173  # Frontend port
```

---

## Backend Issues

### Application Won't Start

#### Error: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause**: Virtual environment not activated or dependencies not installed.

**Solution**:
```bash
cd backend
source venv/bin/activate  # Activate venv
pip install -r requirements.txt  # Install deps
```

#### Error: Address already in use

```
ERROR: [Errno 48] Address already in use
```

**Cause**: Port 8000 is already in use.

**Solution**:
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

#### Error: Database connection failed

```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Cause**: Database path issue or permissions.

**Solution**:
```bash
# Check database URL in .env
cat .env | grep DATABASE_URL

# Ensure directory exists and is writable
mkdir -p ~/argus/backend/data
chmod 755 ~/argus/backend/data

# Use absolute path in .env
DATABASE_URL=sqlite:////Users/yourname/argus/backend/argus.db
```

### Market Data Issues

#### Error: No data returned from yfinance

```
WARNING: No OHLCV data for XYZ
```

**Causes**:
1. Invalid symbol
2. yfinance rate limiting
3. Network issues

**Solutions**:
```python
# Test symbol directly
import yfinance as yf
ticker = yf.Ticker("AAPL")
print(ticker.info)  # Should return data

# If rate limited, wait and retry
# yfinance has undocumented rate limits

# Check network
import requests
requests.get("https://finance.yahoo.com").status_code  # Should be 200
```

#### Error: yfinance timeout

```
MarketDataError: yfinance timeout
```

**Cause**: Slow network or Yahoo Finance issues.

**Solution**:
```python
# Increase timeout in config.py
MARKET_DATA_TIMEOUT = 60  # Default is 30

# Or in .env
MARKET_DATA_TIMEOUT=60
```

### Redis Issues

#### Error: Redis connection refused

```
redis.exceptions.ConnectionError: Connection refused
```

**Cause**: Redis not running or wrong URL.

**Solutions**:
```bash
# Check if Redis is running
redis-cli ping  # Should return PONG

# Start Redis
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

**Or disable Redis** (uses no caching):
```env
# In .env
REDIS_ENABLED=false
```

#### Warning: Cache get/set error

```
WARNING: Cache set error for argus:quote:AAPL
```

**Cause**: Redis connected but operation failed.

**Solutions**:
```bash
# Check Redis memory
redis-cli INFO memory

# Clear Redis cache
redis-cli FLUSHDB

# Check for large values
redis-cli DEBUG OBJECT argus:quote:AAPL
```

### API Endpoint Issues

#### Error: 404 Not Found

```json
{"detail": "Not Found"}
```

**Causes**:
1. Wrong URL path
2. Missing API version prefix
3. Endpoint not registered

**Solutions**:
```bash
# Correct URL format
curl http://localhost:8000/api/v1/health  # Note: /api/v1/ prefix

# Check available endpoints
curl http://localhost:8000/openapi.json | jq '.paths | keys'

# Or visit Swagger docs
open http://localhost:8000/docs
```

#### Error: 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["query", "ma_filter"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

**Cause**: Invalid parameter value.

**Solution**: Check parameter constraints in API docs
```bash
# Valid ma_filter values: 20W, 50W, 100W, 200W
curl "http://localhost:8000/api/v1/screener?ma_filter=20W"  # Correct
curl "http://localhost:8000/api/v1/screener?ma_filter=30W"  # Invalid
```

### Scheduler Issues

#### Scheduled tasks not running

**Causes**:
1. Scheduler disabled
2. Outside market hours
3. Timezone issue

**Solutions**:
```python
# Check scheduler status in logs
# Should see: "Scheduler configured with market hours jobs"

# Enable scheduler in .env
SCHEDULER_ENABLED=true

# Check if within market hours (Mon-Fri, 9:30 AM - 4:00 PM ET)
from app.utils.market_hours import is_market_hours
print(is_market_hours())  # Should be True during market hours

# Force run task manually
from app.tasks.refresh_data import refresh_market_data
import asyncio
asyncio.run(refresh_market_data())
```

---

## Frontend Issues

### Build/Start Issues

#### Error: Cannot find module

```
Error: Cannot find module '@tanstack/react-query'
```

**Cause**: Dependencies not installed.

**Solution**:
```bash
cd frontend
rm -rf node_modules
npm install
```

#### Error: ENOENT package.json

```
ENOENT: no such file or directory, open 'package.json'
```

**Cause**: Wrong directory.

**Solution**:
```bash
cd ~/argus/frontend  # Make sure you're in frontend directory
npm run dev
```

#### Error: Port 5173 in use

```
Error: Port 5173 is in use
```

**Solution**:
```bash
# Kill process using port
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

### API Connection Issues

#### Error: Network Error / CORS

```
Access to XMLHttpRequest blocked by CORS policy
```

**Cause**: Backend not running or CORS misconfigured.

**Solutions**:
```bash
# Make sure backend is running
curl http://localhost:8000/api/v1/health

# Check CORS in backend .env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

#### Error: 404 when calling API

```
GET http://localhost:5173/api/v1/screener 404
```

**Cause**: Vite proxy not configured or backend not running.

**Solutions**:
```typescript
// Check vite.config.ts has proxy
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});

// Or set API URL in .env.local
VITE_API_URL=http://localhost:8000
```

### Chart Issues

#### Chart not rendering

**Causes**:
1. Container has zero height
2. Data format incorrect
3. Lightweight Charts error

**Solutions**:
```tsx
// Ensure container has height
<div className="h-[500px]">  {/* Fixed height */}
  <StockChart data={data} />
</div>

// Check data format
console.log(data.ohlcv[0]);
// Should be: { timestamp: "2024-01-15T00:00:00", open: 100, ... }

// Check browser console for Lightweight Charts errors
```

#### MA lines not showing

**Cause**: Insufficient data for MA period.

**Solution**:
```typescript
// 200W MA needs 1000 days of data
// Make sure API is returning enough history
console.log(data.ohlcv.length);  // Should be > 1000 for 200W MA
```

### State Issues

#### Filters not updating

**Cause**: Zustand store not properly connected.

**Solution**:
```typescript
// Check component is using store correctly
const filters = useScreenerStore((state) => state.filters);
const setFilter = useScreenerStore((state) => state.setFilter);

// Not this (creates new subscription each render):
const { filters, setFilter } = useScreenerStore();
```

#### Data not refetching

**Cause**: React Query cache not invalidating.

**Solution**:
```typescript
// Force refetch
const { refetch } = useScreener();
refetch();

// Or invalidate all queries
import { useQueryClient } from '@tanstack/react-query';
const queryClient = useQueryClient();
queryClient.invalidateQueries(['screener']);
```

---

## Docker Issues

### Container won't start

```
docker: Error response from daemon: driver failed programming external connectivity
```

**Cause**: Port conflict.

**Solution**:
```bash
# Check what's using the port
docker ps
lsof -i :8000

# Stop conflicting containers
docker stop $(docker ps -q)

# Or use different ports in docker-compose.yml
```

### Container can't connect to Redis

```
redis.exceptions.ConnectionError: Error connecting to redis:6379
```

**Cause**: Network issue between containers.

**Solution**:
```yaml
# In docker-compose.yml, ensure services are on same network
services:
  backend:
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379  # Use service name, not localhost
```

### Volume permission issues

```
PermissionError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Fix permissions on host
chmod -R 755 ~/argus/backend/data

# Or in Dockerfile, use non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
```

---

## Performance Issues

### Slow screener results

**Causes**:
1. Too many stocks in universe
2. No caching
3. yfinance rate limits

**Solutions**:
```python
# Reduce universe size temporarily
# In universe.py, limit DEFAULT_UNIVERSE

# Enable Redis caching
REDIS_ENABLED=true

# Increase concurrency limit (carefully)
# In screener.py
semaphore = asyncio.Semaphore(20)  # Default is 10
```

### High memory usage

**Cause**: Large data in memory.

**Solutions**:
```python
# Limit OHLCV history
# In market_data.py, limit data returned
history = history.tail(1000)  # Only keep last 1000 days

# Clear Python cache
import gc
gc.collect()
```

### Frontend slow/unresponsive

**Causes**:
1. Too many re-renders
2. Large chart data
3. Memory leak

**Solutions**:
```typescript
// Memoize expensive components
import { memo } from 'react';
export const StockRow = memo(function StockRow({ data }) {
  // ...
});

// Limit chart data points
const chartData = data.ohlcv.slice(-500);  // Last 500 points

// Check React DevTools Profiler for render issues
```

---

## Common Error Messages Reference

| Error | Meaning | Solution |
|-------|---------|----------|
| `ModuleNotFoundError` | Missing Python package | `pip install -r requirements.txt` |
| `ENOENT` | File/directory not found | Check paths, run from correct directory |
| `CORS error` | Cross-origin request blocked | Start backend, check CORS config |
| `422 Unprocessable Entity` | Invalid request parameters | Check API docs for valid values |
| `503 Service Unavailable` | External service down | Check yfinance, wait and retry |
| `Redis ConnectionError` | Can't connect to Redis | Start Redis or disable in config |
| `Timeout` | Operation took too long | Increase timeout, check network |

---

## Getting More Help

1. **Check logs**: Backend logs show detailed error info
   ```bash
   # If using JSON logging
   uvicorn app.main:app 2>&1 | jq .

   # Or use text format for readability
   LOG_FORMAT=text uvicorn app.main:app --reload
   ```

2. **Enable debug mode**:
   ```env
   DEBUG=true
   LOG_LEVEL=DEBUG
   ```

3. **Check API docs**: http://localhost:8000/docs

4. **Search existing code**: Similar patterns may already exist
   ```bash
   grep -r "pattern" backend/app/
   ```
