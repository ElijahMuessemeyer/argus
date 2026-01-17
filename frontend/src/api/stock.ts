import apiClient from './client';
import type { StockData, Quote, TimeFrame, Period } from '../types/stock';
import type { ChartData, IndicatorData } from '../types/indicator';

export interface StockParams {
  timeframe?: TimeFrame;
  period?: Period;
}

export interface ChartParams {
  timeframe?: TimeFrame;
  period?: Period;
  include_ma?: boolean;
  include_rsi?: boolean;
  include_macd?: boolean;
}

export async function fetchStock(symbol: string, params: StockParams = {}): Promise<StockData> {
  const response = await apiClient.get<StockData>(`/stock/${symbol}`, { params });
  return response.data;
}

export async function fetchQuote(symbol: string): Promise<Quote> {
  const response = await apiClient.get<Quote>(`/stock/${symbol}/quote`);
  return response.data;
}

export async function fetchChartData(symbol: string, params: ChartParams = {}): Promise<ChartData> {
  const response = await apiClient.get<ChartData>(`/stock/${symbol}/chart`, { params });
  return response.data;
}

export async function fetchIndicators(symbol: string): Promise<IndicatorData> {
  const response = await apiClient.get<IndicatorData>(`/stock/${symbol}/indicators`);
  return response.data;
}
