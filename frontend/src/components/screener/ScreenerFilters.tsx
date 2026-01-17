import { useScreenerStore } from '../../stores/screenerStore';
import { Select } from '../ui/Select';
import { Toggle } from '../ui/Toggle';
import { Button } from '../ui/Button';
import { MA_FILTER_OPTIONS } from '../../types/screener';
import { RotateCcw } from 'lucide-react';

const DISTANCE_OPTIONS = [
  { value: '2', label: 'Within 2%' },
  { value: '5', label: 'Within 5%' },
  { value: '10', label: 'Within 10%' },
  { value: '15', label: 'Within 15%' },
  { value: '20', label: 'Within 20%' },
];

const SORT_OPTIONS = [
  { value: 'distance', label: 'Distance from MA' },
  { value: 'symbol', label: 'Symbol' },
  { value: 'price', label: 'Price' },
  { value: 'change', label: 'Daily Change' },
  { value: 'market_cap', label: 'Market Cap' },
];

export function ScreenerFilters() {
  const { filters, setFilter, resetFilters } = useScreenerStore();

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <div className="flex flex-wrap items-center gap-4">
        {/* MA Filter */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">Moving Average</label>
          <Select
            options={MA_FILTER_OPTIONS}
            value={filters.ma_filter}
            onChange={(e) => setFilter('ma_filter', e.target.value as typeof filters.ma_filter)}
          />
        </div>

        {/* Distance */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">Max Distance</label>
          <Select
            options={DISTANCE_OPTIONS}
            value={filters.distance_pct.toString()}
            onChange={(e) => setFilter('distance_pct', parseFloat(e.target.value))}
          />
        </div>

        {/* Sort */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">Sort By</label>
          <Select
            options={SORT_OPTIONS}
            value={filters.sort_by}
            onChange={(e) => setFilter('sort_by', e.target.value as typeof filters.sort_by)}
          />
        </div>

        {/* Position toggles */}
        <div className="flex items-center gap-4 ml-4">
          <Toggle
            checked={filters.include_below}
            onChange={(checked) => setFilter('include_below', checked)}
            label="Below MA"
            size="sm"
          />
          <Toggle
            checked={filters.include_above}
            onChange={(checked) => setFilter('include_above', checked)}
            label="Above MA"
            size="sm"
          />
        </div>

        {/* Reset */}
        <Button
          variant="ghost"
          size="sm"
          onClick={resetFilters}
          className="ml-auto"
        >
          <RotateCcw className="h-4 w-4 mr-1" />
          Reset
        </Button>
      </div>
    </div>
  );
}
