import { MemoryRouter } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { SignalCard } from '../components/signals/SignalCard';
import type { Signal } from '../types/signal';
import { SIGNAL_TYPE_INFO } from '../types/signal';

const baseSignal: Signal = {
  id: 'signal-1',
  symbol: 'AAPL',
  signal_type: 'rsi_oversold',
  timestamp: '2024-01-01T00:00:00Z',
  price: 123.45,
  details: {
    rsi_value: 28.1,
  },
  created_at: '2024-01-01T00:00:00Z',
};

describe('SignalCard', () => {
  it('renders signal metadata and description', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2024-01-01T00:00:00Z'));

    render(
      <MemoryRouter
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <SignalCard signal={baseSignal} />
      </MemoryRouter>
    );

    const info = SIGNAL_TYPE_INFO[baseSignal.signal_type];

    expect(screen.getByText(baseSignal.symbol)).toBeInTheDocument();
    expect(screen.getByText(info.description)).toBeInTheDocument();
    expect(screen.getByText('Just now')).toBeInTheDocument();
    expect(screen.getByText(/\$?123\.45/)).toBeInTheDocument();

    vi.useRealTimers();
  });
});
