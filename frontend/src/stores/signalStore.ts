import { create } from 'zustand';
import type { SignalType } from '../types/signal';

interface SignalFilters {
  types: SignalType[];
  symbols: string[];
  hours: number;
}

interface SignalState {
  filters: SignalFilters;
  setTypes: (types: SignalType[]) => void;
  setSymbols: (symbols: string[]) => void;
  setHours: (hours: number) => void;
  toggleType: (type: SignalType) => void;
  resetFilters: () => void;
}

const defaultFilters: SignalFilters = {
  types: [],
  symbols: [],
  hours: 24,
};

export const useSignalStore = create<SignalState>((set) => ({
  filters: defaultFilters,
  setTypes: (types) =>
    set((state) => ({
      filters: { ...state.filters, types },
    })),
  setSymbols: (symbols) =>
    set((state) => ({
      filters: { ...state.filters, symbols },
    })),
  setHours: (hours) =>
    set((state) => ({
      filters: { ...state.filters, hours },
    })),
  toggleType: (type) =>
    set((state) => {
      const types = state.filters.types.includes(type)
        ? state.filters.types.filter((t) => t !== type)
        : [...state.filters.types, type];
      return { filters: { ...state.filters, types } };
    }),
  resetFilters: () => set({ filters: defaultFilters }),
}));
