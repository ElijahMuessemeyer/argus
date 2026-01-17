import apiClient from './client';

export interface SearchResult {
  symbol: string;
  name: string;
  sector: string | null;
  exchange: string | null;
  in_universe: boolean;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  total: number;
}

export async function searchStocks(query: string, limit: number = 10): Promise<SearchResponse> {
  const response = await apiClient.get<SearchResponse>('/search', {
    params: { q: query, limit },
  });
  return response.data;
}
