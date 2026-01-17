import { useChartStore } from '../../stores/chartStore';
import { Card, CardHeader, CardTitle } from '../ui/Card';
import { Toggle } from '../ui/Toggle';
import { Select } from '../ui/Select';

const TIMEFRAME_OPTIONS = [
  { value: '1D', label: 'Daily' },
  { value: '1W', label: 'Weekly' },
];

const PERIOD_OPTIONS = [
  { value: '3M', label: '3 Months' },
  { value: '6M', label: '6 Months' },
  { value: '1Y', label: '1 Year' },
  { value: '2Y', label: '2 Years' },
  { value: '5Y', label: '5 Years' },
];

export function Sidebar() {
  const { settings, setSetting, toggleIndicator } = useChartStore();

  return (
    <aside className="w-64 p-4 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Chart Settings</CardTitle>
        </CardHeader>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Timeframe</label>
            <Select
              options={TIMEFRAME_OPTIONS}
              value={settings.timeframe}
              onChange={(e) => setSetting('timeframe', e.target.value as '1D' | '1W')}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Period</label>
            <Select
              options={PERIOD_OPTIONS}
              value={settings.period}
              onChange={(e) => setSetting('period', e.target.value as '3M' | '6M' | '1Y' | '2Y' | '5Y')}
              className="w-full"
            />
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Moving Averages</CardTitle>
        </CardHeader>

        <div className="space-y-3">
          <Toggle
            checked={settings.showMA20W}
            onChange={() => toggleIndicator('showMA20W')}
            label="20-Week MA"
            size="sm"
          />
          <Toggle
            checked={settings.showMA50W}
            onChange={() => toggleIndicator('showMA50W')}
            label="50-Week MA"
            size="sm"
          />
          <Toggle
            checked={settings.showMA100W}
            onChange={() => toggleIndicator('showMA100W')}
            label="100-Week MA"
            size="sm"
          />
          <Toggle
            checked={settings.showMA200W}
            onChange={() => toggleIndicator('showMA200W')}
            label="200-Week MA"
            size="sm"
          />
        </div>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Indicators</CardTitle>
        </CardHeader>

        <div className="space-y-3">
          <Toggle
            checked={settings.showVolume}
            onChange={() => toggleIndicator('showVolume')}
            label="Volume"
            size="sm"
          />
          <Toggle
            checked={settings.showRSI}
            onChange={() => toggleIndicator('showRSI')}
            label="RSI (14)"
            size="sm"
          />
          <Toggle
            checked={settings.showMACD}
            onChange={() => toggleIndicator('showMACD')}
            label="MACD"
            size="sm"
          />
        </div>
      </Card>
    </aside>
  );
}
