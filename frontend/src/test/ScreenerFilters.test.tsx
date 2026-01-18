import { render, screen, fireEvent } from '@testing-library/react';
import { ScreenerFilters } from '../components/screener/ScreenerFilters';
import { useScreenerStore } from '../stores/screenerStore';

const resetFilters = () =>
  useScreenerStore.setState({
    filters: {
      ma_filter: '20W',
      distance_pct: 5,
      include_below: true,
      include_above: true,
      sort_by: 'distance',
      sort_order: 'asc',
    },
  });

describe('ScreenerFilters', () => {
  beforeEach(() => {
    resetFilters();
  });

  it('updates MA filter selection', () => {
    render(<ScreenerFilters />);

    const selects = screen.getAllByRole('combobox');
    fireEvent.change(selects[0], { target: { value: '50W' } });

    expect(useScreenerStore.getState().filters.ma_filter).toBe('50W');
  });

  it('toggles include above/below filters', () => {
    render(<ScreenerFilters />);

    const belowToggle = screen.getByRole('switch', { name: 'Below MA' });
    const aboveToggle = screen.getByRole('switch', { name: 'Above MA' });

    fireEvent.click(belowToggle);
    fireEvent.click(aboveToggle);

    const filters = useScreenerStore.getState().filters;
    expect(filters.include_below).toBe(false);
    expect(filters.include_above).toBe(false);
  });
});
