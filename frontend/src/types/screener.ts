export type MAFilter = '20W' | '50W' | '100W' | '200W';
export type SortField = 'symbol' | 'name' | 'price' | 'distance' | 'market_cap' | 'change';
export type SortOrder = 'asc' | 'desc';

export interface ScreenerRequest {
  ma_filter: MAFilter;
  distance_pct: number;
  include_below: boolean;
  include_above: boolean;
  sort_by: SortField;
  sort_order: SortOrder;
  limit: number;
  offset: number;
}

export interface ScreenerResult {
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

export interface ScreenerResponse {
  results: ScreenerResult[];
  total: number;
  filters: ScreenerRequest;
  cached: boolean;
  cache_timestamp: string | null;
}

export const MA_FILTER_OPTIONS: { value: MAFilter; label: string }[] = [
  { value: '20W', label: '20-Week MA' },
  { value: '50W', label: '50-Week MA' },
  { value: '100W', label: '100-Week MA' },
  { value: '200W', label: '200-Week MA' },
];
