export type MAType = 'SMA' | 'EMA';

export interface MovingAverageResult {
  period: number;
  ma_type: MAType;
  values: [string, number | null][];
  current_value: number | null;
  current_price: number | null;
  distance_percent: number | null;
}

export interface RSIResult {
  period: number;
  values: [string, number | null][];
  current_value: number | null;
  is_overbought: boolean;
  is_oversold: boolean;
}

export interface MACDResult {
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

export interface IndicatorData {
  symbol: string;
  ma_20w: MovingAverageResult | null;
  ma_50w: MovingAverageResult | null;
  ma_100w: MovingAverageResult | null;
  ma_200w: MovingAverageResult | null;
  rsi: RSIResult | null;
  macd: MACDResult | null;
}

export interface ChartData {
  symbol: string;
  timeframe: string;
  period: string;
  ohlcv: import('./stock').OHLCV[];
  indicators: {
    ma_20w?: MovingAverageResult;
    ma_50w?: MovingAverageResult;
    ma_100w?: MovingAverageResult;
    ma_200w?: MovingAverageResult;
    rsi?: RSIResult;
    macd?: MACDResult;
  };
}
