export interface OHLCV {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Quote {
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

export interface StockInfo {
  symbol: string;
  name: string;
  sector: string | null;
  industry: string | null;
  exchange: string | null;
  market_cap: number | null;
  currency: string;
}

export interface StockData {
  info: StockInfo;
  quote: Quote;
  ohlcv: OHLCV[];
}

export type TimeFrame = '1D' | '1W';
export type Period = '3M' | '6M' | '1Y' | '2Y' | '5Y';
