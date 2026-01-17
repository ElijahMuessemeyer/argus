export const CHART_COLORS = {
  background: '#1f2937', // gray-800
  text: '#e5e7eb', // gray-200
  grid: '#374151', // gray-700
  crosshair: '#6b7280', // gray-500

  // Price
  upColor: '#22c55e', // green-500
  downColor: '#ef4444', // red-500
  wickUpColor: '#22c55e',
  wickDownColor: '#ef4444',

  // Moving averages
  ma20w: '#fbbf24', // amber-400
  ma50w: '#f97316', // orange-500
  ma100w: '#8b5cf6', // violet-500
  ma200w: '#06b6d4', // cyan-500

  // Indicators
  rsi: '#a78bfa', // violet-400
  rsiOverbought: '#ef4444', // red-500
  rsiOversold: '#22c55e', // green-500

  macd: '#3b82f6', // blue-500
  macdSignal: '#f97316', // orange-500
  macdHistogramUp: '#22c55e',
  macdHistogramDown: '#ef4444',

  // Volume
  volumeUp: 'rgba(34, 197, 94, 0.5)', // green-500 with opacity
  volumeDown: 'rgba(239, 68, 68, 0.5)', // red-500 with opacity
};

export const REFRESH_INTERVALS = {
  quote: 60000, // 1 minute
  screener: 300000, // 5 minutes
  signals: 60000, // 1 minute
  chart: 300000, // 5 minutes
};

export const API_ENDPOINTS = {
  screener: '/screener',
  stock: '/stock',
  signals: '/signals',
  search: '/search',
  health: '/health',
};
