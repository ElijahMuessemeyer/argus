import { Link } from 'react-router-dom';
import { TrendingUp, Activity, Bell } from 'lucide-react';
import { StockSearch } from '../search/StockSearch';

export function Header() {
  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <TrendingUp className="h-8 w-8 text-blue-500" />
            <span className="text-xl font-bold text-white">Argus</span>
          </Link>

          {/* Search */}
          <div className="flex-1 max-w-lg mx-8">
            <StockSearch />
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            <Link
              to="/"
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            >
              <Activity className="h-4 w-4 mr-2" />
              Screener
            </Link>
            <Link
              to="/signals"
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            >
              <Bell className="h-4 w-4 mr-2" />
              Signals
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
