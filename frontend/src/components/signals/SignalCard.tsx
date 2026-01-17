import { useNavigate } from 'react-router-dom';
import { clsx } from 'clsx';
import type { Signal } from '../../types/signal';
import { SIGNAL_TYPE_INFO } from '../../types/signal';
import { formatPrice, formatTimeAgo } from '../../utils/formatters';
import { Badge } from '../ui/Badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface SignalCardProps {
  signal: Signal;
}

export function SignalCard({ signal }: SignalCardProps) {
  const navigate = useNavigate();
  const info = SIGNAL_TYPE_INFO[signal.signal_type];

  const handleClick = () => {
    navigate(`/stock/${signal.symbol}`);
  };

  const getIcon = () => {
    switch (info.sentiment) {
      case 'bullish':
        return <TrendingUp className="h-4 w-4 text-green-400" />;
      case 'bearish':
        return <TrendingDown className="h-4 w-4 text-red-400" />;
      default:
        return <Minus className="h-4 w-4 text-yellow-400" />;
    }
  };

  return (
    <div
      onClick={handleClick}
      className={clsx(
        'p-4 rounded-lg border cursor-pointer transition-colors',
        'bg-gray-800 hover:bg-gray-700',
        {
          'border-green-800': info.sentiment === 'bullish',
          'border-red-800': info.sentiment === 'bearish',
          'border-gray-700': info.sentiment === 'neutral',
        }
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          {getIcon()}
          <span className="font-medium text-white">{signal.symbol}</span>
          <Badge variant={info.sentiment}>{info.name}</Badge>
        </div>
        <span className="text-sm text-gray-400">
          {formatTimeAgo(signal.timestamp)}
        </span>
      </div>

      <p className="mt-2 text-sm text-gray-300">{info.description}</p>

      <div className="mt-3 flex items-center gap-4 text-sm">
        <span className="text-gray-400">
          Price: <span className="text-white">{formatPrice(signal.price)}</span>
        </span>
        {signal.details.ma_period && (
          <span className="text-gray-400">
            MA: <span className="text-white">{signal.details.ma_period as string}</span>
          </span>
        )}
        {signal.details.rsi_value && (
          <span className="text-gray-400">
            RSI: <span className="text-white">{(signal.details.rsi_value as number).toFixed(1)}</span>
          </span>
        )}
      </div>
    </div>
  );
}
