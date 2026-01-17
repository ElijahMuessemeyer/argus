import { useChartStore } from '../../stores/chartStore';
import { Button } from '../ui/Button';
import { Toggle } from '../ui/Toggle';

export function ChartControls() {
  const { settings, setSetting, toggleIndicator } = useChartStore();

  return (
    <div className="flex flex-wrap items-center gap-4 p-4 bg-gray-800 rounded-lg border border-gray-700">
      {/* Timeframe buttons */}
      <div className="flex gap-1">
        <Button
          variant={settings.timeframe === '1D' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setSetting('timeframe', '1D')}
        >
          Daily
        </Button>
        <Button
          variant={settings.timeframe === '1W' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setSetting('timeframe', '1W')}
        >
          Weekly
        </Button>
      </div>

      {/* Period buttons */}
      <div className="flex gap-1">
        {(['3M', '6M', '1Y', '2Y', '5Y'] as const).map((period) => (
          <Button
            key={period}
            variant={settings.period === period ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setSetting('period', period)}
          >
            {period}
          </Button>
        ))}
      </div>

      <div className="h-6 w-px bg-gray-600" />

      {/* MA toggles */}
      <div className="flex gap-3">
        <Toggle
          checked={settings.showMA20W}
          onChange={() => toggleIndicator('showMA20W')}
          label="20W"
          size="sm"
        />
        <Toggle
          checked={settings.showMA50W}
          onChange={() => toggleIndicator('showMA50W')}
          label="50W"
          size="sm"
        />
        <Toggle
          checked={settings.showMA200W}
          onChange={() => toggleIndicator('showMA200W')}
          label="200W"
          size="sm"
        />
      </div>

      <div className="h-6 w-px bg-gray-600" />

      {/* Indicator toggles */}
      <div className="flex gap-3">
        <Toggle
          checked={settings.showVolume}
          onChange={() => toggleIndicator('showVolume')}
          label="Vol"
          size="sm"
        />
        <Toggle
          checked={settings.showRSI}
          onChange={() => toggleIndicator('showRSI')}
          label="RSI"
          size="sm"
        />
        <Toggle
          checked={settings.showMACD}
          onChange={() => toggleIndicator('showMACD')}
          label="MACD"
          size="sm"
        />
      </div>
    </div>
  );
}
