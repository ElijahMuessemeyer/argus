import { useQuery } from '@tanstack/react-query';
import { fetchSignals } from '../api/signals';
import { useSignalStore } from '../stores/signalStore';
import { REFRESH_INTERVALS } from '../utils/constants';

export function useSignals() {
  const filters = useSignalStore((state) => state.filters);

  return useQuery({
    queryKey: ['signals', filters],
    queryFn: () =>
      fetchSignals({
        types: filters.types.length > 0 ? filters.types : undefined,
        symbols: filters.symbols.length > 0 ? filters.symbols : undefined,
        hours: filters.hours,
      }),
    refetchInterval: REFRESH_INTERVALS.signals,
    staleTime: REFRESH_INTERVALS.signals / 2,
  });
}
