import { useParams } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Sidebar } from '../components/layout/Sidebar';
import { StockChart } from '../components/charts/StockChart';
import { ChartControls } from '../components/charts/ChartControls';
import { RSIPane } from '../components/charts/RSIPane';
import { MACDPane } from '../components/charts/MACDPane';
import { LoadingState } from '../components/ui/Spinner';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useChartData, useQuote } from '../hooks/useStock';
import { useChartStore } from '../stores/chartStore';
import { formatPrice, formatPercent, formatCompactNumber, formatMarketCap } from '../utils/formatters';
import { clsx } from 'clsx';

export function StockDetailPage() {
  const { symbol } = useParams<{ symbol: string }>();
  const { data: chartData, isLoading: chartLoading, error: chartError } = useChartData(symbol || null);
  const { data: quote, isLoading: quoteLoading } = useQuote(symbol || null);
  const { settings } = useChartStore();

  if (!symbol) {
    return (
      <MainLayout>
        <div className="text-center py-12 text-gray-400">
          No symbol specified
        </div>
      </MainLayout>
    );
  }

  if (chartLoading || quoteLoading) {
    return (
      <MainLayout sidebar={<Sidebar />}>
        <LoadingState message={`Loading ${symbol}...`} />
      </MainLayout>
    );
  }

  if (chartError || !chartData) {
    return (
      <MainLayout sidebar={<Sidebar />}>
        <div className="text-center py-12 text-red-400">
          Error loading data for {symbol}
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout sidebar={<Sidebar />}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">{symbol}</h1>
            {quote && (
              <div className="flex items-center gap-4 mt-2">
                <span className="text-2xl font-mono text-white">
                  {formatPrice(quote.price)}
                </span>
                <span
                  className={clsx(
                    'text-lg font-medium',
                    quote.change >= 0 ? 'text-green-400' : 'text-red-400'
                  )}
                >
                  {quote.change >= 0 ? '+' : ''}{quote.change.toFixed(2)} ({formatPercent(quote.change_percent)})
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Quote Info */}
        {quote && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <Card padding="sm">
              <div className="text-xs text-gray-400">Volume</div>
              <div className="font-mono text-white">{formatCompactNumber(quote.volume)}</div>
            </Card>
            <Card padding="sm">
              <div className="text-xs text-gray-400">Avg Volume</div>
              <div className="font-mono text-white">
                {quote.avg_volume ? formatCompactNumber(quote.avg_volume) : 'N/A'}
              </div>
            </Card>
            <Card padding="sm">
              <div className="text-xs text-gray-400">Market Cap</div>
              <div className="font-mono text-white">{formatMarketCap(quote.market_cap)}</div>
            </Card>
            <Card padding="sm">
              <div className="text-xs text-gray-400">52W High</div>
              <div className="font-mono text-white">
                {quote.high_52w ? formatPrice(quote.high_52w) : 'N/A'}
              </div>
            </Card>
            <Card padding="sm">
              <div className="text-xs text-gray-400">52W Low</div>
              <div className="font-mono text-white">
                {quote.low_52w ? formatPrice(quote.low_52w) : 'N/A'}
              </div>
            </Card>
            <Card padding="sm">
              <div className="text-xs text-gray-400">52W Range</div>
              <div className="font-mono text-white">
                {quote.high_52w && quote.low_52w
                  ? `${(((quote.price - quote.low_52w) / (quote.high_52w - quote.low_52w)) * 100).toFixed(0)}%`
                  : 'N/A'}
              </div>
            </Card>
          </div>
        )}

        {/* MA Distances */}
        {chartData.indicators && (
          <div className="flex flex-wrap gap-2">
            {chartData.indicators.ma_20w?.distance_percent != null && (
              <Badge
                variant={chartData.indicators.ma_20w.distance_percent < 0 ? 'bullish' : 'neutral'}
              >
                20W MA: {formatPercent(chartData.indicators.ma_20w.distance_percent)}
              </Badge>
            )}
            {chartData.indicators.ma_50w?.distance_percent != null && (
              <Badge
                variant={chartData.indicators.ma_50w.distance_percent < 0 ? 'bullish' : 'neutral'}
              >
                50W MA: {formatPercent(chartData.indicators.ma_50w.distance_percent)}
              </Badge>
            )}
            {chartData.indicators.ma_200w?.distance_percent != null && (
              <Badge
                variant={chartData.indicators.ma_200w.distance_percent < 0 ? 'bullish' : 'neutral'}
              >
                200W MA: {formatPercent(chartData.indicators.ma_200w.distance_percent)}
              </Badge>
            )}
          </div>
        )}

        {/* Chart Controls */}
        <ChartControls />

        {/* Main Chart */}
        <Card padding="none">
          <StockChart data={chartData} />
        </Card>

        {/* RSI Pane */}
        {settings.showRSI && chartData.indicators?.rsi && (
          <Card padding="sm">
            <RSIPane data={chartData.indicators.rsi} />
          </Card>
        )}

        {/* MACD Pane */}
        {settings.showMACD && chartData.indicators?.macd && (
          <Card padding="sm">
            <MACDPane data={chartData.indicators.macd} />
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
