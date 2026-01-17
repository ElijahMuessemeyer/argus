# Frontend Reference

Complete reference for all frontend components, hooks, stores, and utilities.

---

## Components

### UI Components (`src/components/ui/`)

Reusable, presentational components with no business logic.

#### Button

```tsx
import { Button } from '@/components/ui/Button';

// Variants
<Button variant="primary">Primary</Button>   // Blue background
<Button variant="secondary">Secondary</Button> // Gray background
<Button variant="ghost">Ghost</Button>       // Transparent

// Sizes
<Button size="sm">Small</Button>    // Compact
<Button size="md">Medium</Button>   // Default
<Button size="lg">Large</Button>    // Prominent

// With icon
<Button>
  <Icon className="h-4 w-4 mr-2" />
  Label
</Button>

// Disabled
<Button disabled>Disabled</Button>

// Full width
<Button className="w-full">Full Width</Button>
```

#### Card

```tsx
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';

// Basic card
<Card>Content here</Card>

// Padding options
<Card padding="none">No padding</Card>
<Card padding="sm">Small padding (12px)</Card>
<Card padding="md">Medium padding (16px)</Card>  // Default
<Card padding="lg">Large padding (24px)</Card>

// With header
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <Button size="sm">Action</Button>
  </CardHeader>
  <div>Content</div>
</Card>
```

#### Input

```tsx
import { Input } from '@/components/ui/Input';

// Basic
<Input placeholder="Enter text..." />

// With error state
<Input error placeholder="Invalid input" />

// Controlled
<Input
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>

// Types
<Input type="text" />
<Input type="number" />
<Input type="search" />
```

#### Select

```tsx
import { Select } from '@/components/ui/Select';

<Select
  options={[
    { value: '20W', label: '20-Week MA' },
    { value: '50W', label: '50-Week MA' },
  ]}
  value={selected}
  onChange={(e) => setSelected(e.target.value)}
/>
```

#### Toggle

```tsx
import { Toggle } from '@/components/ui/Toggle';

<Toggle
  checked={isEnabled}
  onChange={(checked) => setIsEnabled(checked)}
  label="Enable feature"
  size="sm"  // or "md"
/>
```

#### Badge

```tsx
import { Badge } from '@/components/ui/Badge';

// Variants
<Badge variant="default">Default</Badge>    // Gray
<Badge variant="bullish">Bullish</Badge>    // Green
<Badge variant="bearish">Bearish</Badge>    // Red
<Badge variant="neutral">Neutral</Badge>    // Yellow
```

#### Spinner

```tsx
import { Spinner, LoadingState } from '@/components/ui/Spinner';

// Standalone spinner
<Spinner size="sm" />
<Spinner size="md" />
<Spinner size="lg" />

// Loading state with message
<LoadingState message="Loading data..." />
```

---

### Layout Components (`src/components/layout/`)

Components that define page structure.

#### MainLayout

```tsx
import { MainLayout } from '@/components/layout/MainLayout';
import { Sidebar } from '@/components/layout/Sidebar';

// Without sidebar
<MainLayout>
  <h1>Page Title</h1>
  <Content />
</MainLayout>

// With sidebar
<MainLayout sidebar={<Sidebar />}>
  <Content />
</MainLayout>
```

#### Header

```tsx
// Included in MainLayout automatically
// Contains:
// - Logo
// - StockSearch
// - Navigation links (Screener, Signals)
```

#### Sidebar

```tsx
// Chart settings sidebar
// Contains:
// - Timeframe selector (Daily/Weekly)
// - Period selector (3M/6M/1Y/2Y/5Y)
// - MA toggles (20W, 50W, 100W, 200W)
// - Indicator toggles (Volume, RSI, MACD)
```

---

### Chart Components (`src/components/charts/`)

Components for stock chart visualization.

#### StockChart

Main candlestick chart with MA overlays.

```tsx
import { StockChart } from '@/components/charts/StockChart';

<StockChart data={chartData} />

// chartData shape:
{
  symbol: string;
  timeframe: '1D' | '1W';
  period: '3M' | '6M' | '1Y' | '2Y' | '5Y';
  ohlcv: OHLCV[];
  indicators: {
    ma_20w?: MovingAverageResult;
    ma_50w?: MovingAverageResult;
    ma_100w?: MovingAverageResult;
    ma_200w?: MovingAverageResult;
    rsi?: RSIResult;
    macd?: MACDResult;
  };
}
```

**Behavior**:
- Automatically resizes on window resize
- Shows/hides MA lines based on chartStore settings
- Shows/hides volume based on settings

#### ChartControls

Inline controls for chart settings.

```tsx
import { ChartControls } from '@/components/charts/ChartControls';

<ChartControls />

// Contains:
// - Timeframe buttons (Daily/Weekly)
// - Period buttons (3M/6M/1Y/2Y/5Y)
// - MA toggles (20W/50W/200W)
// - Indicator toggles (Vol/RSI/MACD)
```

#### RSIPane

RSI sub-chart (separate from main chart).

```tsx
import { RSIPane } from '@/components/charts/RSIPane';

{showRSI && <RSIPane data={rsiData} />}

// Displays:
// - RSI line (purple)
// - Overbought line at 70 (red dashed)
// - Oversold line at 30 (green dashed)
```

#### MACDPane

MACD sub-chart.

```tsx
import { MACDPane } from '@/components/charts/MACDPane';

{showMACD && <MACDPane data={macdData} />}

// Displays:
// - MACD line (blue)
// - Signal line (orange)
// - Histogram (green/red bars)
```

---

### Screener Components (`src/components/screener/`)

Components for the stock screener feature.

#### ScreenerFilters

Filter controls for screener.

```tsx
import { ScreenerFilters } from '@/components/screener/ScreenerFilters';

<ScreenerFilters />

// Contains:
// - MA filter dropdown (20W/50W/100W/200W)
// - Distance dropdown (2%/5%/10%/15%/20%)
// - Sort dropdown
// - Below/Above toggles
// - Reset button
```

#### ScreenerResults

Table of screener results.

```tsx
import { ScreenerResults } from '@/components/screener/ScreenerResults';

<ScreenerResults />

// Automatically:
// - Fetches data based on filter state
// - Shows loading state
// - Shows empty state
// - Renders StockRow for each result
```

#### StockRow

Single row in screener results table.

```tsx
import { StockRow } from '@/components/screener/StockRow';

<StockRow stock={screenResult} />

// Displays:
// - Symbol and name
// - Sector
// - Price
// - Daily change (colored)
// - MA value
// - Distance from MA (badge)
// - Market cap
//
// Clickable - navigates to stock detail page
```

---

### Signal Components (`src/components/signals/`)

Components for signal feed.

#### SignalFeed

Main signal list with filters.

```tsx
import { SignalFeed } from '@/components/signals/SignalFeed';

<SignalFeed />

// Contains:
// - Time filter (24h/48h/72h/7d)
// - Type filter chips
// - List of SignalCards
```

#### SignalCard

Individual signal display.

```tsx
import { SignalCard } from '@/components/signals/SignalCard';

<SignalCard signal={signal} />

// Displays:
// - Symbol with trend icon
// - Signal type badge
// - Time ago
// - Description
// - Price and details
//
// Clickable - navigates to stock detail page
```

---

### Search Components (`src/components/search/`)

#### StockSearch

Search autocomplete in header.

```tsx
import { StockSearch } from '@/components/search/StockSearch';

<StockSearch />

// Features:
// - Debounced input (300ms)
// - Dropdown with results
// - "In Universe" badge for tracked stocks
// - Keyboard navigation (Enter to select first, Esc to close)
// - Click outside to close
```

---

## Hooks (`src/hooks/`)

Custom React hooks for data fetching and state.

### useScreener

```tsx
import { useScreener } from '@/hooks/useScreener';

function Component() {
  const { data, isLoading, error, refetch } = useScreener();

  // data: ScreenerResponse | undefined
  // isLoading: boolean
  // error: Error | null
  // refetch: () => void

  // Automatically:
  // - Uses filter state from screenerStore
  // - Refetches every 5 minutes
  // - Caches results
}
```

### useStock

```tsx
import { useStock, useQuote, useChartData, useIndicators } from '@/hooks/useStock';

// Full stock data
const { data } = useStock('AAPL');

// Just quote (refetches every minute)
const { data } = useQuote('AAPL');

// Chart data with indicators
const { data } = useChartData('AAPL');
// Uses chartStore settings for timeframe, period, RSI, MACD

// All indicators
const { data } = useIndicators('AAPL');
```

### useSignals

```tsx
import { useSignals } from '@/hooks/useSignals';

const { data, isLoading, error } = useSignals();

// Automatically:
// - Uses filter state from signalStore
// - Refetches every minute
```

### useSearch

```tsx
import { useSearch } from '@/hooks/useSearch';

const { query, setQuery, results, isLoading } = useSearch();

// query: current input value
// setQuery: debounced setter (300ms)
// results: SearchResult[]
// isLoading: boolean
```

---

## Stores (`src/stores/`)

Zustand state stores for client-side state.

### screenerStore

```tsx
import { useScreenerStore } from '@/stores/screenerStore';

// Get state
const filters = useScreenerStore((state) => state.filters);
// filters: { ma_filter, distance_pct, include_below, include_above, sort_by, sort_order }

// Actions
const setFilter = useScreenerStore((state) => state.setFilter);
setFilter('ma_filter', '50W');
setFilter('distance_pct', 10);

const resetFilters = useScreenerStore((state) => state.resetFilters);
resetFilters();
```

### chartStore

```tsx
import { useChartStore } from '@/stores/chartStore';

// Get settings
const settings = useChartStore((state) => state.settings);
// settings: { timeframe, period, showMA20W, showMA50W, ... showRSI, showMACD }

// Get selected symbol
const selectedSymbol = useChartStore((state) => state.selectedSymbol);

// Actions
const setSetting = useChartStore((state) => state.setSetting);
setSetting('timeframe', '1W');

const setSelectedSymbol = useChartStore((state) => state.setSelectedSymbol);
setSelectedSymbol('AAPL');

const toggleIndicator = useChartStore((state) => state.toggleIndicator);
toggleIndicator('showRSI');  // Toggles true/false
```

### signalStore

```tsx
import { useSignalStore } from '@/stores/signalStore';

// Get state
const filters = useSignalStore((state) => state.filters);
// filters: { types: SignalType[], symbols: string[], hours: number }

// Actions
const setTypes = useSignalStore((state) => state.setTypes);
setTypes(['rsi_oversold', 'rsi_overbought']);

const toggleType = useSignalStore((state) => state.toggleType);
toggleType('macd_bullish_cross');  // Add or remove

const setHours = useSignalStore((state) => state.setHours);
setHours(48);

const resetFilters = useSignalStore((state) => state.resetFilters);
```

---

## Types (`src/types/`)

TypeScript type definitions.

### Stock Types

```typescript
// src/types/stock.ts

interface OHLCV {
  timestamp: string;  // ISO format
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
  volume: number;
  avg_volume: number | null;
  market_cap: number | null;
  high_52w: number | null;
  low_52w: number | null;
  updated_at: string;
}

interface StockInfo {
  symbol: string;
  name: string;
  sector: string | null;
  industry: string | null;
  exchange: string | null;
  market_cap: number | null;
  currency: string;
}

type TimeFrame = '1D' | '1W';
type Period = '3M' | '6M' | '1Y' | '2Y' | '5Y';
```

### Indicator Types

```typescript
// src/types/indicator.ts

interface MovingAverageResult {
  period: number;
  ma_type: 'SMA' | 'EMA';
  values: [string, number | null][];  // [timestamp, value]
  current_value: number | null;
  current_price: number | null;
  distance_percent: number | null;
}

interface RSIResult {
  period: number;
  values: [string, number | null][];
  current_value: number | null;
  is_overbought: boolean;
  is_oversold: boolean;
}

interface MACDResult {
  fast_period: number;
  slow_period: number;
  signal_period: number;
  macd_line: [string, number | null][];
  signal_line: [string, number | null][];
  histogram: [string, number | null][];
  current_macd: number | null;
  current_signal: number | null;
  current_histogram: number | null;
}
```

### Signal Types

```typescript
// src/types/signal.ts

type SignalType =
  | 'ma_crossover_bullish'
  | 'ma_crossover_bearish'
  | 'rsi_oversold'
  | 'rsi_overbought'
  | 'macd_bullish_cross'
  | 'macd_bearish_cross'
  | 'near_52w_high'
  | 'near_52w_low'
  | 'new_52w_high'
  | 'new_52w_low';

interface Signal {
  id: string;
  symbol: string;
  signal_type: SignalType;
  timestamp: string;
  price: number;
  details: Record<string, unknown>;
  created_at: string;
}
```

### Screener Types

```typescript
// src/types/screener.ts

type MAFilter = '20W' | '50W' | '100W' | '200W';
type SortField = 'symbol' | 'name' | 'price' | 'distance' | 'market_cap' | 'change';
type SortOrder = 'asc' | 'desc';

interface ScreenerResult {
  symbol: string;
  name: string;
  sector: string | null;
  price: number;
  change: number;
  change_percent: number;
  market_cap: number | null;
  ma_value: number;
  ma_period: string;
  distance: number;
  distance_percent: number;
  position: 'above' | 'below' | 'at';
}
```

---

## Utilities (`src/utils/`)

### Formatters

```typescript
import {
  formatPrice,
  formatPercent,
  formatNumber,
  formatCompactNumber,
  formatMarketCap,
  formatVolume,
  formatDate,
  formatDateTime,
  formatTimeAgo,
} from '@/utils/formatters';

formatPrice(123.45)        // "$123.45"
formatPercent(5.25)        // "+5.25%"
formatPercent(-3.10)       // "-3.10%"
formatNumber(1234567)      // "1,234,567"
formatCompactNumber(1.5e9) // "1.50B"
formatMarketCap(2.85e12)   // "2.85T"
formatVolume(45000000)     // "45.00M"
formatDate("2024-01-15")   // "Jan 15, 2024"
formatDateTime("2024-01-15T14:30:00") // "Jan 15, 2:30 PM"
formatTimeAgo("2024-01-15T14:30:00")  // "5m ago", "2h ago", "3d ago"
```

### Constants

```typescript
import { CHART_COLORS, REFRESH_INTERVALS } from '@/utils/constants';

CHART_COLORS.upColor      // '#22c55e' (green)
CHART_COLORS.downColor    // '#ef4444' (red)
CHART_COLORS.ma20w        // '#fbbf24' (amber)
CHART_COLORS.ma50w        // '#f97316' (orange)
CHART_COLORS.ma200w       // '#06b6d4' (cyan)

REFRESH_INTERVALS.quote     // 60000 (1 minute)
REFRESH_INTERVALS.screener  // 300000 (5 minutes)
REFRESH_INTERVALS.signals   // 60000 (1 minute)
```

---

## Pages (`src/pages/`)

Top-level page components.

### ScreenerPage

```
Route: /
Contains: MainLayout > ScreenerFilters, ScreenerResults
```

### StockDetailPage

```
Route: /stock/:symbol
Contains: MainLayout with Sidebar > Quote info, ChartControls, StockChart, RSIPane?, MACDPane?
```

### SignalsPage

```
Route: /signals
Contains: MainLayout > SignalFeed
```
