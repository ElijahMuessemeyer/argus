import { useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { searchStocks } from '../api/search';

export function useSearch() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  const { data, isFetching, error } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: ({ signal }) => searchStocks(debouncedQuery, 10, { signal }),
    enabled: debouncedQuery.length >= 1,
    staleTime: 60000,
    retry: false,
  });

  const isCanceled =
    (error && typeof error === 'object' && 'code' in error && (error as { code?: string }).code === 'ERR_CANCELED') ||
    (error instanceof Error && error.name === 'CanceledError');

  return {
    query,
    setQuery,
    results: data?.results || [],
    isLoading: isFetching,
    error: isCanceled ? null : error,
  };
}
