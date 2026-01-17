export type SignalType =
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

export interface Signal {
  id: string;
  symbol: string;
  signal_type: SignalType;
  timestamp: string;
  price: number;
  details: Record<string, unknown>;
  created_at: string;
}

export interface SignalsResponse {
  signals: Signal[];
  total: number;
  filters: {
    types: string[] | null;
    symbols: string[] | null;
    hours: number;
  };
}

export interface SignalTypeInfo {
  type: SignalType;
  name: string;
  description: string;
  sentiment: 'bullish' | 'bearish' | 'neutral';
}

export const SIGNAL_TYPE_INFO: Record<SignalType, SignalTypeInfo> = {
  ma_crossover_bullish: {
    type: 'ma_crossover_bullish',
    name: 'MA Crossover Bullish',
    description: 'Price crosses above a moving average',
    sentiment: 'bullish',
  },
  ma_crossover_bearish: {
    type: 'ma_crossover_bearish',
    name: 'MA Crossover Bearish',
    description: 'Price crosses below a moving average',
    sentiment: 'bearish',
  },
  rsi_oversold: {
    type: 'rsi_oversold',
    name: 'RSI Oversold',
    description: 'RSI drops below 30',
    sentiment: 'bullish',
  },
  rsi_overbought: {
    type: 'rsi_overbought',
    name: 'RSI Overbought',
    description: 'RSI rises above 70',
    sentiment: 'bearish',
  },
  macd_bullish_cross: {
    type: 'macd_bullish_cross',
    name: 'MACD Bullish Cross',
    description: 'MACD line crosses above signal line',
    sentiment: 'bullish',
  },
  macd_bearish_cross: {
    type: 'macd_bearish_cross',
    name: 'MACD Bearish Cross',
    description: 'MACD line crosses below signal line',
    sentiment: 'bearish',
  },
  near_52w_high: {
    type: 'near_52w_high',
    name: 'Near 52W High',
    description: 'Within 5% of 52-week high',
    sentiment: 'neutral',
  },
  near_52w_low: {
    type: 'near_52w_low',
    name: 'Near 52W Low',
    description: 'Within 5% of 52-week low',
    sentiment: 'neutral',
  },
  new_52w_high: {
    type: 'new_52w_high',
    name: 'New 52W High',
    description: 'New 52-week high',
    sentiment: 'bullish',
  },
  new_52w_low: {
    type: 'new_52w_low',
    name: 'New 52W Low',
    description: 'New 52-week low',
    sentiment: 'bearish',
  },
};
