import { useQuery } from '@tanstack/react-query';
import { fetchStock, fetchQuote, fetchChartData, fetchIndicators } from '../api/stock';
import { useChartStore } from '../stores/chartStore';
import { REFRESH_INTERVALS } from '../utils/constants';

export function useStock(symbol: string | null) {
  return useQuery({
    queryKey: ['stock', symbol],
    queryFn: () => (symbol ? fetchStock(symbol) : Promise.reject('No symbol')),
    enabled: !!symbol,
    staleTime: REFRESH_INTERVALS.quote,
  });
}

export function useQuote(symbol: string | null) {
  return useQuery({
    queryKey: ['quote', symbol],
    queryFn: () => (symbol ? fetchQuote(symbol) : Promise.reject('No symbol')),
    enabled: !!symbol,
    refetchInterval: REFRESH_INTERVALS.quote,
    staleTime: REFRESH_INTERVALS.quote / 2,
  });
}

export function useChartData(symbol: string | null) {
  const settings = useChartStore((state) => state.settings);

  return useQuery({
    queryKey: ['chart', symbol, settings.timeframe, settings.period, settings.showRSI, settings.showMACD],
    queryFn: () =>
      symbol
        ? fetchChartData(symbol, {
            timeframe: settings.timeframe,
            period: settings.period,
            include_ma: true,
            include_rsi: settings.showRSI,
            include_macd: settings.showMACD,
          })
        : Promise.reject('No symbol'),
    enabled: !!symbol,
    staleTime: REFRESH_INTERVALS.chart,
  });
}

export function useIndicators(symbol: string | null) {
  return useQuery({
    queryKey: ['indicators', symbol],
    queryFn: () => (symbol ? fetchIndicators(symbol) : Promise.reject('No symbol')),
    enabled: !!symbol,
    staleTime: REFRESH_INTERVALS.chart,
  });
}
