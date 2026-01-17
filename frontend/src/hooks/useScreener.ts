import { useQuery } from '@tanstack/react-query';
import { fetchScreenerResults } from '../api/screener';
import { useScreenerStore } from '../stores/screenerStore';
import { REFRESH_INTERVALS } from '../utils/constants';

export function useScreener() {
  const filters = useScreenerStore((state) => state.filters);

  return useQuery({
    queryKey: ['screener', filters],
    queryFn: () => fetchScreenerResults(filters),
    refetchInterval: REFRESH_INTERVALS.screener,
    staleTime: REFRESH_INTERVALS.screener / 2,
  });
}
