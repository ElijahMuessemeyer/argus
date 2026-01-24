import { useEffect, useRef } from 'react';
import {
  createChart,
  IChartApi,
  ISeriesApi,
  CandlestickData,
  AreaData,
  LineData,
  HistogramData,
  BusinessDay,
} from 'lightweight-charts';
import { useChartStore } from '../../stores/chartStore';
import { CHART_COLORS } from '../../utils/constants';
import type { ChartData } from '../../types/indicator';

interface StockChartProps {
  data: ChartData;
}

const toChartDate = (value: unknown): BusinessDay | null => {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(trimmed);
    if (match) {
      return {
        year: Number(match[1]),
        month: Number(match[2]),
        day: Number(match[3]),
      };
    }
    const parsed = new Date(trimmed);
    if (!Number.isNaN(parsed.getTime())) {
      return {
        year: parsed.getUTCFullYear(),
        month: parsed.getUTCMonth() + 1,
        day: parsed.getUTCDate(),
      };
    }
    if (trimmed.includes('T')) {
      const [datePart] = trimmed.split('T');
      const parts = datePart.split('-').map(Number);
      if (parts.length === 3 && parts.every(Number.isFinite)) {
        return { year: parts[0], month: parts[1], day: parts[2] };
      }
    }
    if (trimmed.includes(' ')) {
      const [datePart] = trimmed.split(' ');
      const parts = datePart.split('-').map(Number);
      if (parts.length === 3 && parts.every(Number.isFinite)) {
        return { year: parts[0], month: parts[1], day: parts[2] };
      }
    }
    return null;
  }
  if (value instanceof Date) {
    return {
      year: value.getUTCFullYear(),
      month: value.getUTCMonth() + 1,
      day: value.getUTCDate(),
    };
  }
  if (typeof value === 'number') {
    const ms = value > 1e12 ? value : value * 1000;
    const parsed = new Date(ms);
    if (!Number.isNaN(parsed.getTime())) {
      return {
        year: parsed.getUTCFullYear(),
        month: parsed.getUTCMonth() + 1,
        day: parsed.getUTCDate(),
      };
    }
  }
  return null;
};

const toFiniteNumber = (value: unknown) => {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
};

const extractSeriesPoint = (point: unknown) => {
  if (Array.isArray(point)) {
    const [rawTime, rawValue] = point;
    return { time: toChartDate(rawTime), value: toFiniteNumber(rawValue) };
  }
  if (point && typeof point === 'object') {
    const record = point as Record<string, unknown>;
    const rawTime = record.time ?? record.timestamp ?? record.date ?? record.x;
    const rawValue = record.value ?? record.y ?? record.close ?? record.price;
    return { time: toChartDate(rawTime), value: toFiniteNumber(rawValue) };
  }
  return { time: null, value: null };
};

export function StockChart({ data }: StockChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const areaSeriesRef = useRef<ISeriesApi<'Area'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const maSeriesRefs = useRef<Map<string, ISeriesApi<'Line'>>>(new Map());
  const lastViewKeyRef = useRef<string | null>(null);

  const { settings } = useChartStore();

  useEffect(() => {
    if (!containerRef.current) return;

    maSeriesRefs.current.clear();

    // Create chart
    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: CHART_COLORS.background },
        textColor: CHART_COLORS.text,
      },
      grid: {
        vertLines: { color: CHART_COLORS.grid },
        horzLines: { color: CHART_COLORS.grid },
      },
      crosshair: {
        mode: 1,
        vertLine: { color: CHART_COLORS.crosshair },
        horzLine: { color: CHART_COLORS.crosshair },
      },
      rightPriceScale: {
        borderColor: CHART_COLORS.grid,
      },
      timeScale: {
        borderColor: CHART_COLORS.grid,
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: CHART_COLORS.upColor,
      downColor: CHART_COLORS.downColor,
      wickUpColor: CHART_COLORS.wickUpColor,
      wickDownColor: CHART_COLORS.wickDownColor,
      borderVisible: false,
    });
    candleSeriesRef.current = candleSeries;

    const areaSeries = chart.addAreaSeries({
      lineColor: CHART_COLORS.upColor,
      topColor: 'rgba(34, 197, 94, 0.35)',
      bottomColor: 'rgba(34, 197, 94, 0.0)',
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: false,
      visible: false,
    });
    areaSeriesRef.current = areaSeries;

    // Volume series
    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    });
    volumeSeriesRef.current = volumeSeries;

    chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    // Handle resize
    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
      areaSeriesRef.current = null;
      maSeriesRefs.current.clear();
    };
  }, []);

  // Update data
  useEffect(() => {
    if (
      !candleSeriesRef.current ||
      !areaSeriesRef.current ||
      !volumeSeriesRef.current ||
      !data.ohlcv
    )
      return;

    // Format OHLCV data
    const candleData: CandlestickData[] = data.ohlcv
      .map((d) => {
        const time = toChartDate(d.timestamp);
        if (!time) return null;
        return {
          time,
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        } satisfies CandlestickData;
      })
      .filter((d): d is CandlestickData => d !== null);

    const volumeData: HistogramData[] = data.ohlcv
      .map((d) => {
        const time = toChartDate(d.timestamp);
        if (!time) return null;
        return {
          time,
          value: d.volume,
          color: d.close >= d.open ? CHART_COLORS.volumeUp : CHART_COLORS.volumeDown,
        } satisfies HistogramData;
      })
      .filter((d): d is HistogramData => d !== null);

    const areaData: AreaData[] = data.ohlcv
      .map((d) => {
        const time = toChartDate(d.timestamp);
        if (!time) return null;
        return {
          time,
          value: d.close,
        } satisfies AreaData;
      })
      .filter((d): d is AreaData => d !== null);

    const isLongRange = data.period === '2Y' || data.period === '5Y';

    candleSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volumeData);
    areaSeriesRef.current.setData(areaData);

    candleSeriesRef.current.applyOptions({ visible: !isLongRange });
    areaSeriesRef.current.applyOptions({ visible: isLongRange });

    const viewKey = `${data.symbol}-${data.timeframe}-${data.period}`;
    if (chartRef.current && lastViewKeyRef.current !== viewKey) {
      chartRef.current.timeScale().fitContent();
      lastViewKeyRef.current = viewKey;
    }

    // Show/hide volume
    volumeSeriesRef.current.applyOptions({
      visible: settings.showVolume,
    });
  }, [data.ohlcv, data.symbol, data.timeframe, data.period, settings.showVolume]);

  // Update MA lines
  useEffect(() => {
    if (!chartRef.current || !data.indicators) return;

    const chart = chartRef.current;

    const fallbackPeriods =
      data.timeframe === '1W'
        ? { ma_20w: 20, ma_50w: 50, ma_100w: 100, ma_200w: 200 }
        : { ma_20w: 100, ma_50w: 250, ma_100w: 500, ma_200w: 1000 };

    const computeFallbackMA = (period: number): LineData[] => {
      if (!data.ohlcv || data.ohlcv.length < period) return [];
      const output: LineData[] = [];
      let sum = 0;
      for (let i = 0; i < data.ohlcv.length; i += 1) {
        const close = data.ohlcv[i].close;
        if (!Number.isFinite(close)) continue;
        sum += close;
        if (i >= period) {
          const prev = data.ohlcv[i - period]?.close ?? 0;
          if (Number.isFinite(prev)) {
            sum -= prev;
          }
        }
        if (i >= period - 1) {
          const time = toChartDate(data.ohlcv[i].timestamp);
          if (!time) continue;
          output.push({ time, value: Number((sum / period).toFixed(2)) });
        }
      }
      return output;
    };

    // Helper to update or create MA line
    const updateMALine = (
      key: keyof typeof fallbackPeriods,
      maData: typeof data.indicators.ma_20w,
      color: string,
      visible: boolean
    ) => {
      let series = maSeriesRefs.current.get(key);

      if (!series && visible) {
        series = chart.addLineSeries({
          color,
          lineWidth: 2,
          priceLineVisible: false,
          lastValueVisible: false,
        });
        maSeriesRefs.current.set(key, series);
      }

      if (!series) {
        return;
      }

      let lineData: LineData[] = [];
      if (maData?.values?.length) {
        lineData = maData.values
          .map((point) => {
            const { time, value } = extractSeriesPoint(point);
            if (!time || value === null) return null;
            return { time, value } satisfies LineData;
          })
          .filter((v): v is LineData => v !== null);
      }

      if (lineData.length === 0) {
        lineData = computeFallbackMA(fallbackPeriods[key]);
      }

      series.setData(lineData);
      series.applyOptions({ visible: visible && lineData.length > 0 });
    };

    updateMALine('ma_20w', data.indicators.ma_20w, CHART_COLORS.ma20w, settings.showMA20W);
    updateMALine('ma_50w', data.indicators.ma_50w, CHART_COLORS.ma50w, settings.showMA50W);
    updateMALine('ma_100w', data.indicators.ma_100w, CHART_COLORS.ma100w, settings.showMA100W);
    updateMALine('ma_200w', data.indicators.ma_200w, CHART_COLORS.ma200w, settings.showMA200W);
  }, [data.indicators, settings.showMA20W, settings.showMA50W, settings.showMA100W, settings.showMA200W]);

  return (
    <div ref={containerRef} className="w-full h-[500px] rounded-lg overflow-hidden" />
  );
}
