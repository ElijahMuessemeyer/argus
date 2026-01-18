# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (optional)
- Git

## Initial Setup

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment file
cp .env.example .env

# Initialize database
python -c "from app.db.session import init_db; init_db()"
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install
```

## Running Development Servers

### Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API will be available at http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at http://localhost:5173

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_indicators.py

# Run specific test
pytest tests/unit/test_indicators.py::TestMovingAverage::test_sma_basic
```

### Frontend Tests

```bash
cd frontend

# Run tests (Vitest)
npm run test
```

## Code Quality

### Backend

```bash
cd backend
source venv/bin/activate

# Lint
ruff check app tests

# Format
black app tests

# Type check
mypy app/
```

### Frontend

```bash
cd frontend

# Lint
npm run lint

# Type check
npm run typecheck

# Fix lint issues
npm run lint -- --fix
```

## Environment Variables

### Backend (.env)

```env
# Application
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LOG_FORMAT=text

# Database
DATABASE_URL=sqlite:///./argus.db

# Redis
REDIS_URL=redis://localhost:6379
REDIS_ENABLED=false  # Set to true if Redis is available

# Scheduler
SCHEDULER_ENABLED=true
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:8000
```

## Database Migrations

Using Alembic for migrations:

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Adding New Features

### Backend

1. Create Pydantic models in `app/models/`
2. Add database models in `app/models/db.py` if needed
3. Implement business logic in `app/core/`
4. Create API endpoint in `app/api/v1/`
5. Add tests in `tests/`

### Frontend

1. Add TypeScript types in `src/types/`
2. Create API functions in `src/api/`
3. Add Zustand store in `src/stores/` if needed
4. Create custom hook in `src/hooks/`
5. Build component in `src/components/`

## Common Tasks

### Adding a New Indicator

1. Add calculation in `backend/app/core/indicators.py`
2. Add model in `backend/app/models/indicator.py`
3. Update chart endpoint in `backend/app/api/v1/stock.py`
4. Add frontend type in `frontend/src/types/indicator.ts`
5. Update chart component

### Adding a New Signal Type

1. Add to `SignalType` enum in `backend/app/models/signal.py`
2. Implement detection in `backend/app/core/signals.py`
3. Add to frontend types in `frontend/src/types/signal.ts`
4. Update `SIGNAL_TYPE_INFO` constant

## Troubleshooting

### Backend won't start

- Check Python version: `python --version` (need 3.11+)
- Check virtual environment is activated
- Verify all dependencies: `pip install -r requirements.txt`

### Frontend won't start

- Check Node version: `node --version` (need 18+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check for port conflicts

### Market data not loading

- yfinance may have rate limits
- Check network connectivity
- Verify stock symbol exists

### Cache not working

- Check Redis is running: `redis-cli ping`
- Set `REDIS_ENABLED=true` in .env
- Check connection URL
