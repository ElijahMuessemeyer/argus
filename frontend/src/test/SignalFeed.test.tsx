import { MemoryRouter } from 'react-router-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { SignalFeed } from '../components/signals/SignalFeed';
import { useSignalStore } from '../stores/signalStore';
import type { SignalsResponse } from '../types/signal';

const mockResponse: SignalsResponse = {
  signals: [
    {
      id: '1',
      symbol: 'AAPL',
      signal_type: 'rsi_oversold',
      timestamp: '2024-01-01T00:00:00Z',
      price: 120,
      details: {},
      created_at: '2024-01-01T00:00:00Z',
    },
  ],
  total: 1,
  filters: { types: null, symbols: null, hours: 24 },
};

vi.mock('../hooks/useSignals', () => ({
  useSignals: () => ({ data: mockResponse, isLoading: false, error: null }),
}));

const resetFilters = () =>
  useSignalStore.setState({
    filters: {
      types: [],
      symbols: [],
      hours: 24,
    },
  });

describe('SignalFeed', () => {
  beforeEach(() => {
    resetFilters();
  });

  it('updates hours filter', () => {
    render(
      <MemoryRouter
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <SignalFeed />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: '48h' }));

    expect(useSignalStore.getState().filters.hours).toBe(48);
  });

  it('toggles signal type filter', () => {
    render(
      <MemoryRouter
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <SignalFeed />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole('button', { name: 'RSI Oversold' }));

    expect(useSignalStore.getState().filters.types).toContain('rsi_oversold');
  });
});
