import { render, screen, fireEvent } from '@testing-library/react';
import { ChartControls } from '../components/charts/ChartControls';
import { useChartStore } from '../stores/chartStore';

const resetSettings = () =>
  useChartStore.setState({
    settings: {
      timeframe: '1D',
      period: '1Y',
      showMA20W: true,
      showMA50W: true,
      showMA100W: false,
      showMA200W: true,
      showRSI: false,
      showMACD: false,
      showVolume: true,
    },
  });

describe('ChartControls', () => {
  beforeEach(() => {
    resetSettings();
  });

  it('updates timeframe when clicking Weekly', () => {
    render(<ChartControls />);

    fireEvent.click(screen.getByRole('button', { name: 'Weekly' }));

    expect(useChartStore.getState().settings.timeframe).toBe('1W');
  });

  it('toggles RSI indicator', () => {
    render(<ChartControls />);

    fireEvent.click(screen.getByRole('switch', { name: 'RSI' }));

    expect(useChartStore.getState().settings.showRSI).toBe(true);
  });
});
