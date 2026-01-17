import { useNavigate } from 'react-router-dom';
import { clsx } from 'clsx';
import type { ScreenerResult } from '../../types/screener';
import { formatPrice, formatPercent, formatMarketCap } from '../../utils/formatters';

interface StockRowProps {
  stock: ScreenerResult;
}

export function StockRow({ stock }: StockRowProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/stock/${stock.symbol}`);
  };

  return (
    <tr
      onClick={handleClick}
      className="border-b border-gray-700 hover:bg-gray-800/50 cursor-pointer transition-colors"
    >
      <td className="px-4 py-3">
        <div>
          <span className="font-medium text-white">{stock.symbol}</span>
          <p className="text-sm text-gray-400 truncate max-w-[200px]">{stock.name}</p>
        </div>
      </td>
      <td className="px-4 py-3 text-gray-300">{stock.sector || '-'}</td>
      <td className="px-4 py-3 text-right font-mono text-white">
        {formatPrice(stock.price)}
      </td>
      <td
        className={clsx(
          'px-4 py-3 text-right font-mono',
          stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
        )}
      >
        {formatPercent(stock.change_percent)}
      </td>
      <td className="px-4 py-3 text-right font-mono text-gray-300">
        {formatPrice(stock.ma_value)}
      </td>
      <td className="px-4 py-3 text-right">
        <span
          className={clsx(
            'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
            stock.position === 'below'
              ? 'bg-green-900/50 text-green-400'
              : stock.position === 'above'
              ? 'bg-yellow-900/50 text-yellow-400'
              : 'bg-gray-700 text-gray-300'
          )}
        >
          {stock.position === 'at' ? 'At MA' : formatPercent(stock.distance_percent)}
        </span>
      </td>
      <td className="px-4 py-3 text-right text-gray-300">
        {formatMarketCap(stock.market_cap)}
      </td>
    </tr>
  );
}
