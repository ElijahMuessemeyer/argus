import { MainLayout } from '../components/layout/MainLayout';
import { SignalFeed } from '../components/signals/SignalFeed';

export function SignalsPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Trading Signals</h1>
          <p className="text-gray-400 mt-1">
            Recent MA crossovers, RSI signals, MACD crosses, and 52-week highs/lows
          </p>
        </div>

        <SignalFeed />
      </div>
    </MainLayout>
  );
}
