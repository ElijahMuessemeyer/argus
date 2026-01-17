import apiClient from './client';
import type { ScreenerResponse, MAFilter, SortField, SortOrder } from '../types/screener';

export interface ScreenerParams {
  ma_filter?: MAFilter;
  distance_pct?: number;
  include_below?: boolean;
  include_above?: boolean;
  sort_by?: SortField;
  sort_order?: SortOrder;
  limit?: number;
  offset?: number;
}

export async function fetchScreenerResults(params: ScreenerParams = {}): Promise<ScreenerResponse> {
  const response = await apiClient.get<ScreenerResponse>('/screener', { params });
  return response.data;
}
