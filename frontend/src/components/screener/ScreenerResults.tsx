import { useScreener } from '../../hooks/useScreener';
import { useScreenerStore } from '../../stores/screenerStore';
import { StockRow } from './StockRow';
import { LoadingState } from '../ui/Spinner';
import { ArrowUpDown } from 'lucide-react';

export function ScreenerResults() {
  const { data, isLoading, error } = useScreener();
  const { filters, setFilter } = useScreenerStore();

  const toggleSort = () => {
    setFilter('sort_order', filters.sort_order === 'asc' ? 'desc' : 'asc');
  };

  if (isLoading) {
    return <LoadingState message="Loading screener results..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-400">
        Error loading data. Please try again.
      </div>
    );
  }

  if (!data || data.results.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        No stocks match your criteria. Try adjusting the filters.
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-900/50 text-left text-sm text-gray-400">
              <th className="px-4 py-3 font-medium">Symbol</th>
              <th className="px-4 py-3 font-medium">Sector</th>
              <th className="px-4 py-3 font-medium text-right">Price</th>
              <th className="px-4 py-3 font-medium text-right">Change</th>
              <th className="px-4 py-3 font-medium text-right">
                {filters.ma_filter} MA
              </th>
              <th className="px-4 py-3 font-medium text-right">
                <button
                  onClick={toggleSort}
                  className="inline-flex items-center hover:text-white transition-colors"
                >
                  Distance
                  <ArrowUpDown className="ml-1 h-3 w-3" />
                </button>
              </th>
              <th className="px-4 py-3 font-medium text-right">Market Cap</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((stock) => (
              <StockRow key={stock.symbol} stock={stock} />
            ))}
          </tbody>
        </table>
      </div>

      <div className="px-4 py-3 bg-gray-900/50 border-t border-gray-700 text-sm text-gray-400">
        Showing {data.results.length} of {data.total} stocks
        {data.cached && (
          <span className="ml-2">
            (cached)
          </span>
        )}
      </div>
    </div>
  );
}
