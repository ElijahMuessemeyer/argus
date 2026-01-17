# Contributing to Argus

This guide is for developers and AI coding agents who want to contribute to or modify the Argus codebase.

---

## Quick Reference

| Task | Command |
|------|---------|
| Run backend | `cd backend && uvicorn app.main:app --reload` |
| Run frontend | `cd frontend && npm run dev` |
| Run backend tests | `cd backend && pytest` |
| Lint backend | `cd backend && ruff check app/` |
| Lint frontend | `cd frontend && npm run lint` |

---

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (optional, for caching)
- Git

### Initial Setup

```bash
# Clone repository
cd ~/argus

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env

# Frontend setup
cd ../frontend
npm install
```

### Running Development Servers

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## Code Style Guidelines

### Python (Backend)

#### Formatting

- **Line length**: 100 characters
- **Formatter**: Black
- **Linter**: Ruff
- **Type hints**: Required for all public functions

```bash
# Format code
black app/

# Lint code
ruff check app/

# Type check
mypy app/
```

#### Naming Conventions

```python
# Classes: PascalCase
class MarketDataService:
    pass

# Functions/methods: snake_case
def get_stock_quote(symbol: str) -> Quote:
    pass

# Constants: UPPER_SNAKE_CASE
MA_PERIOD_MAP = {"20W": 100}

# Private methods: leading underscore
def _calculate_internal(self):
    pass
```

#### Function Documentation

```python
def calculate_rsi(
    prices: pd.Series,
    period: int = 14,
) -> pd.Series:
    """
    Calculate Relative Strength Index.

    Args:
        prices: Series of closing prices
        period: RSI lookback period (default 14)

    Returns:
        Series with RSI values (0-100 range)

    Raises:
        ValueError: If prices has fewer than period+1 values

    Example:
        >>> prices = pd.Series([44, 44.5, 43.5, 44.25, 45])
        >>> rsi = calculate_rsi(prices, period=3)
    """
```

#### Async Patterns

```python
# Use async for I/O operations
async def get_quote(self, symbol: str) -> Quote:
    # Use await for async calls
    data = await self._fetch_from_api(symbol)
    return Quote(**data)

# Use asyncio.gather for concurrent operations
async def get_batch_quotes(self, symbols: list[str]) -> list[Quote]:
    tasks = [self.get_quote(s) for s in symbols]
    return await asyncio.gather(*tasks)

# Use semaphore for rate limiting
async def process_with_limit(self, items: list):
    semaphore = asyncio.Semaphore(10)

    async def process_one(item):
        async with semaphore:
            return await self._process(item)

    return await asyncio.gather(*[process_one(i) for i in items])
```

### TypeScript (Frontend)

#### Formatting

- **Line length**: 100 characters
- **Formatter**: Prettier (via ESLint)
- **Linter**: ESLint

```bash
# Lint and fix
npm run lint -- --fix
```

#### Naming Conventions

```typescript
// Interfaces: PascalCase with 'I' prefix optional
interface StockData {
  symbol: string;
}

// Types: PascalCase
type MAFilter = '20W' | '50W';

// Functions: camelCase
function formatPrice(value: number): string {}

// Constants: UPPER_SNAKE_CASE
const REFRESH_INTERVAL = 60000;

// Components: PascalCase
function StockChart({ data }: Props) {}

// Hooks: camelCase with 'use' prefix
function useScreener() {}
```

#### Component Structure

```typescript
// 1. Imports (external, then internal)
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

import { Button } from '../ui/Button';
import { useScreener } from '../../hooks/useScreener';
import type { ScreenerResult } from '../../types/screener';

// 2. Types/interfaces
interface Props {
  data: ScreenerResult;
  onSelect: (symbol: string) => void;
}

// 3. Component
export function StockRow({ data, onSelect }: Props) {
  // 3a. Hooks
  const [isHovered, setIsHovered] = useState(false);

  // 3b. Handlers
  const handleClick = () => {
    onSelect(data.symbol);
  };

  // 3c. Render
  return (
    <tr onClick={handleClick}>
      {/* ... */}
    </tr>
  );
}
```

---

## Testing Guidelines

### Backend Tests

#### Test Structure

```
backend/tests/
├── conftest.py          # Shared fixtures
├── unit/                # Unit tests (no external dependencies)
│   ├── test_indicators.py
│   ├── test_screener.py
│   └── test_signals.py
└── integration/         # Integration tests (may use DB/API)
    ├── test_api_health.py
    └── test_api_screener.py
```

#### Writing Unit Tests

```python
# backend/tests/unit/test_indicators.py

import pytest
import pandas as pd
from app.core.indicators import IndicatorCalculator

class TestMovingAverage:
    """Group related tests in classes."""

    def test_sma_calculation(self):
        """Test name describes what is being tested."""
        # Arrange
        prices = pd.Series([10, 20, 30, 40, 50])

        # Act
        result = IndicatorCalculator.moving_average(prices, period=3)

        # Assert
        assert result.iloc[-1] == 40  # (30+40+50)/3

    def test_sma_insufficient_data(self):
        """Test edge cases."""
        prices = pd.Series([10, 20])
        result = IndicatorCalculator.moving_average(prices, period=3)
        assert pd.isna(result.iloc[-1])

    @pytest.mark.parametrize("period,expected", [
        (2, 45),  # (40+50)/2
        (3, 40),  # (30+40+50)/3
        (5, 30),  # (10+20+30+40+50)/5
    ])
    def test_sma_various_periods(self, period, expected):
        """Use parametrize for multiple similar tests."""
        prices = pd.Series([10, 20, 30, 40, 50])
        result = IndicatorCalculator.moving_average(prices, period=period)
        assert result.iloc[-1] == expected
```

#### Using Fixtures

```python
# backend/tests/conftest.py

import pytest
from datetime import datetime, timedelta
from app.models.stock import OHLCV

@pytest.fixture
def sample_ohlcv() -> list[OHLCV]:
    """Generate sample OHLCV data for testing."""
    base_date = datetime(2024, 1, 1)
    data = []

    for i in range(300):
        date = base_date + timedelta(days=i)
        base_price = 100 + (i * 0.1)

        data.append(OHLCV(
            timestamp=date,
            open=base_price,
            high=base_price + 2,
            low=base_price - 1,
            close=base_price + 1,
            volume=1000000,
        ))

    return data

# Usage in test
def test_with_fixture(sample_ohlcv):
    result = calculate_something(sample_ohlcv)
    assert result is not None
```

#### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/unit/test_indicators.py

# Specific test
pytest tests/unit/test_indicators.py::TestMovingAverage::test_sma_calculation

# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Frontend Tests

```typescript
// frontend/src/components/__tests__/Button.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../ui/Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant classes', () => {
    render(<Button variant="primary">Primary</Button>);
    expect(screen.getByText('Primary')).toHaveClass('bg-blue-600');
  });
});
```

---

## Pull Request Checklist

Before submitting changes, verify:

### Code Quality

- [ ] Code follows style guidelines
- [ ] All functions have type hints (Python) / types (TypeScript)
- [ ] Complex logic is documented with comments
- [ ] No console.log/print statements left in code
- [ ] No hardcoded values (use constants/config)

### Testing

- [ ] New code has tests
- [ ] All tests pass (`pytest` / `npm test`)
- [ ] Edge cases are tested
- [ ] Integration tests updated if API changed

### Documentation

- [ ] Docstrings added for new functions
- [ ] README updated if user-facing changes
- [ ] API.md updated if endpoints changed
- [ ] CHANGELOG updated

### Before Commit

```bash
# Backend
cd backend
source venv/bin/activate
ruff check app/
black app/
pytest

# Frontend
cd frontend
npm run lint
npm test
```

---

## Common Patterns

### Adding a Feature End-to-End

Example: Adding a new indicator (Bollinger Bands)

#### 1. Backend Model

```python
# backend/app/models/indicator.py

class BollingerBandsResult(BaseModel):
    period: int
    std_dev: float
    upper_band: list[tuple[datetime, float | None]]
    middle_band: list[tuple[datetime, float | None]]
    lower_band: list[tuple[datetime, float | None]]
```

#### 2. Backend Calculation

```python
# backend/app/core/indicators.py

@staticmethod
def bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands."""
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower
```

#### 3. Backend API

```python
# backend/app/api/v1/stock.py

@router.get("/{symbol}/chart")
async def get_chart(
    symbol: str,
    include_bollinger: bool = Query(default=False),
    ...
):
    if include_bollinger:
        indicators["bollinger"] = calculate_bollinger(...)
```

#### 4. Frontend Type

```typescript
// frontend/src/types/indicator.ts

export interface BollingerBandsResult {
  period: number;
  std_dev: number;
  upper_band: [string, number | null][];
  middle_band: [string, number | null][];
  lower_band: [string, number | null][];
}
```

#### 5. Frontend API

```typescript
// frontend/src/api/stock.ts

export interface ChartParams {
  include_bollinger?: boolean;
}
```

#### 6. Frontend Store

```typescript
// frontend/src/stores/chartStore.ts

interface ChartSettings {
  showBollinger: boolean;
}
```

#### 7. Frontend Component

```tsx
// frontend/src/components/charts/StockChart.tsx

if (settings.showBollinger && data.indicators?.bollinger) {
  addBollingerBands(chart, data.indicators.bollinger);
}
```

#### 8. Tests

```python
# backend/tests/unit/test_indicators.py

def test_bollinger_bands():
    prices = pd.Series([...])
    upper, middle, lower = IndicatorCalculator.bollinger_bands(prices)
    assert upper.iloc[-1] > middle.iloc[-1] > lower.iloc[-1]
```

---

## Debugging Tips

### Backend Debugging

```python
# Add to .env
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text  # More readable than JSON

# Use logger instead of print
from app.utils.logging import get_logger
logger = get_logger("my_module")
logger.debug("Variable value: %s", some_var)

# Interactive debugging
import pdb; pdb.set_trace()  # Add breakpoint

# Or use debugpy for VS Code
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

### Frontend Debugging

```typescript
// React Query Devtools (add to App.tsx in dev)
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// In component
<ReactQueryDevtools initialIsOpen={false} />

// Console logging
console.log('State:', JSON.stringify(state, null, 2));

// React DevTools
// Install browser extension for component inspection
```

---

## Git Workflow

### Branch Naming

```
feature/add-bollinger-bands
bugfix/fix-rsi-calculation
refactor/cleanup-api-endpoints
docs/update-readme
```

### Commit Messages

```
feat: Add Bollinger Bands indicator

- Add calculation in indicators.py
- Add API parameter for including BB
- Add frontend toggle and visualization

Closes #123
```

Prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `docs:` - Documentation
- `test:` - Tests
- `chore:` - Maintenance

---

## Getting Help

1. **Check existing docs**: `docs/` folder
2. **Read the code**: Follow the patterns in similar files
3. **Run tests**: They serve as documentation
4. **API docs**: http://localhost:8000/docs when backend is running
