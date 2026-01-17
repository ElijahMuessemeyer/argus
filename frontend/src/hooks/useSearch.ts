import { useQuery } from '@tanstack/react-query';
import { searchStocks } from '../api/search';
import { useState, useCallback } from 'react';

export function useSearch() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');

  const handleSearch = useCallback((value: string) => {
    setQuery(value);
    // Simple debounce
    const timer = setTimeout(() => {
      setDebouncedQuery(value);
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  const { data, isLoading, error } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => searchStocks(debouncedQuery),
    enabled: debouncedQuery.length >= 1,
    staleTime: 60000,
  });

  return {
    query,
    setQuery: handleSearch,
    results: data?.results || [],
    isLoading,
    error,
  };
}
