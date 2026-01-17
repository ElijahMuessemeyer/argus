import apiClient from './client';
import type { SignalsResponse, SignalType } from '../types/signal';

export interface SignalsParams {
  types?: SignalType[];
  symbols?: string[];
  hours?: number;
  limit?: number;
}

export async function fetchSignals(params: SignalsParams = {}): Promise<SignalsResponse> {
  const queryParams: Record<string, string | number> = {};

  if (params.types?.length) {
    queryParams.types = params.types.join(',');
  }
  if (params.symbols?.length) {
    queryParams.symbols = params.symbols.join(',');
  }
  if (params.hours) {
    queryParams.hours = params.hours;
  }
  if (params.limit) {
    queryParams.limit = params.limit;
  }

  const response = await apiClient.get<SignalsResponse>('/signals', { params: queryParams });
  return response.data;
}
