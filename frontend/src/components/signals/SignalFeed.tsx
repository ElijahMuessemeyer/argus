import { useSignals } from '../../hooks/useSignals';
import { useSignalStore } from '../../stores/signalStore';
import { SignalCard } from './SignalCard';
import { LoadingState } from '../ui/Spinner';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { SIGNAL_TYPE_INFO, SignalType } from '../../types/signal';

const SIGNAL_TYPES = Object.keys(SIGNAL_TYPE_INFO) as SignalType[];

export function SignalFeed() {
  const { data, isLoading, error } = useSignals();
  const { filters, toggleType, setHours, resetFilters } = useSignalStore();

  if (isLoading) {
    return <LoadingState message="Loading signals..." />;
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-400">
        Error loading signals. Please try again.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span className="text-sm text-gray-400">Time:</span>
          {[24, 48, 72, 168].map((hours) => (
            <Button
              key={hours}
              variant={filters.hours === hours ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setHours(hours)}
            >
              {hours <= 48 ? `${hours}h` : `${hours / 24}d`}
            </Button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-gray-400 mr-2">Types:</span>
          {SIGNAL_TYPES.map((type) => {
            const info = SIGNAL_TYPE_INFO[type];
            const isActive = filters.types.includes(type);
            return (
              <button
                key={type}
                onClick={() => toggleType(type)}
                className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {info.name}
              </button>
            );
          })}
          {filters.types.length > 0 && (
            <Button variant="ghost" size="sm" onClick={resetFilters}>
              Clear
            </Button>
          )}
        </div>
      </div>

      {/* Results */}
      {!data || data.signals.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          No signals found. Try adjusting the filters.
        </div>
      ) : (
        <>
          <div className="text-sm text-gray-400">
            {data.total} signals in the last {filters.hours} hours
          </div>
          <div className="space-y-3">
            {data.signals.map((signal) => (
              <SignalCard key={signal.id} signal={signal} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
