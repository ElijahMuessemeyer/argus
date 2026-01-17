import { create } from 'zustand';
import type { MAFilter, SortField, SortOrder } from '../types/screener';

interface ScreenerFilters {
  ma_filter: MAFilter;
  distance_pct: number;
  include_below: boolean;
  include_above: boolean;
  sort_by: SortField;
  sort_order: SortOrder;
}

interface ScreenerState {
  filters: ScreenerFilters;
  setFilter: <K extends keyof ScreenerFilters>(key: K, value: ScreenerFilters[K]) => void;
  resetFilters: () => void;
}

const defaultFilters: ScreenerFilters = {
  ma_filter: '20W',
  distance_pct: 5,
  include_below: true,
  include_above: true,
  sort_by: 'distance',
  sort_order: 'asc',
};

export const useScreenerStore = create<ScreenerState>((set) => ({
  filters: defaultFilters,
  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    })),
  resetFilters: () => set({ filters: defaultFilters }),
}));
