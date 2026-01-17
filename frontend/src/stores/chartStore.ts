import { create } from 'zustand';
import type { TimeFrame, Period } from '../types/stock';

interface ChartSettings {
  timeframe: TimeFrame;
  period: Period;
  showMA20W: boolean;
  showMA50W: boolean;
  showMA100W: boolean;
  showMA200W: boolean;
  showRSI: boolean;
  showMACD: boolean;
  showVolume: boolean;
}

interface ChartState {
  settings: ChartSettings;
  selectedSymbol: string | null;
  setSetting: <K extends keyof ChartSettings>(key: K, value: ChartSettings[K]) => void;
  setSelectedSymbol: (symbol: string | null) => void;
  toggleIndicator: (indicator: keyof ChartSettings) => void;
}

const defaultSettings: ChartSettings = {
  timeframe: '1D',
  period: '1Y',
  showMA20W: true,
  showMA50W: true,
  showMA100W: false,
  showMA200W: true,
  showRSI: false,
  showMACD: false,
  showVolume: true,
};

export const useChartStore = create<ChartState>((set) => ({
  settings: defaultSettings,
  selectedSymbol: null,
  setSetting: (key, value) =>
    set((state) => ({
      settings: { ...state.settings, [key]: value },
    })),
  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
  toggleIndicator: (indicator) =>
    set((state) => ({
      settings: {
        ...state.settings,
        [indicator]: !state.settings[indicator],
      },
    })),
}));
