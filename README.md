# Argus - Stock Screening Web Application

> **Note:** This project is being retired. Argus 2 is coming soon with a completely redesigned architecture and new features. Stay tuned!

---

A stock screening web application that helps investors identify large-cap US stocks trading near or below key moving averages, with interactive charts and real-time signal tracking.

## Features

- **Screener**: Find large-cap US stocks near/below MAs (20W, 50W, 100W, 200W)
- **Interactive Charts**: TradingView-style charts with MA overlays using Lightweight Charts
- **Indicators**: RSI and MACD as toggleable sub-charts
- **Signal Feed**: MA crossovers, RSI overbought/oversold, MACD crossovers, 52W highs/lows
- **Search**: Look up any US stock (not just screener results)
- **5-Minute Updates**: During market hours (9:30 AM - 4:00 PM ET)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3.11+ |
| Frontend | React 18, TypeScript, Vite |
| Charts | Lightweight Charts (TradingView) |
| State | Zustand |
| Data Fetching | React Query |
| Styling | Tailwind CSS |
| Cache | Redis |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Scheduler | APScheduler |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (optional, falls back to no-cache mode)

### Development Setup

1. **Clone and setup backend**:
```bash
cd ~/argus/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

2. **Start backend**:
```bash
uvicorn app.main:app --reload
```

3. **Setup frontend** (new terminal):
```bash
cd ~/argus/frontend
npm install
```

4. **Start frontend**:
```bash
npm run dev
```

5. **Open browser**: http://localhost:5173

### Docker Setup

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/screener` | Screen stocks by MA distance |
| `GET /api/v1/stock/{symbol}` | Get stock data |
| `GET /api/v1/stock/{symbol}/chart` | Get chart data with indicators |
| `GET /api/v1/signals` | Get trading signals |
| `GET /api/v1/search` | Search stocks |

See [API Documentation](docs/API.md) for full details.

## Moving Average Calculations

| MA | Trading Days |
|----|--------------|
| 20W MA | 100-day SMA |
| 50W MA | 250-day SMA |
| 100W MA | 500-day SMA |
| 200W MA | 1000-day SMA |

## Project Structure

```
argus/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Business logic
│   │   ├── models/          # Pydantic schemas
│   │   ├── services/        # External services
│   │   ├── tasks/           # Background tasks
│   │   └── utils/           # Utilities
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── api/             # API client
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── pages/           # Page components
│   │   ├── stores/          # Zustand stores
│   │   └── types/           # TypeScript types
├── docker-compose.yml
└── Makefile
```

## Development

```bash
# Run backend + frontend tests
make test

# Lint + type-check (Python + TypeScript)
make lint

# Clean build artifacts
make clean
```

### CI

GitHub Actions runs on every push/PR:
- Backend: ruff, black, mypy, pytest
- Frontend: eslint, tsc type-check, vitest

## License

MIT
