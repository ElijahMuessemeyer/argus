import { MainLayout } from '../components/layout/MainLayout';
import { ScreenerFilters } from '../components/screener/ScreenerFilters';
import { ScreenerResults } from '../components/screener/ScreenerResults';

export function ScreenerPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Stock Screener</h1>
          <p className="text-gray-400 mt-1">
            Find large-cap US stocks trading near or below key moving averages
          </p>
        </div>

        <ScreenerFilters />
        <ScreenerResults />
      </div>
    </MainLayout>
  );
}
