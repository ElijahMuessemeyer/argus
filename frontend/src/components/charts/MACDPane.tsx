import { useEffect, useRef } from 'react';
import { createChart, IChartApi, LineData, HistogramData } from 'lightweight-charts';
import { CHART_COLORS } from '../../utils/constants';
import type { MACDResult } from '../../types/indicator';

interface MACDPaneProps {
  data: MACDResult;
}

const toChartDate = (value: unknown) => {
  if (typeof value === 'string') {
    return value.split('T')[0];
  }
  if (value instanceof Date) {
    return value.toISOString().split('T')[0];
  }
  return null;
};

export function MACDPane({ data }: MACDPaneProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: CHART_COLORS.background },
        textColor: CHART_COLORS.text,
      },
      grid: {
        vertLines: { color: CHART_COLORS.grid },
        horzLines: { color: CHART_COLORS.grid },
      },
      rightPriceScale: {
        borderColor: CHART_COLORS.grid,
      },
      timeScale: {
        visible: false,
      },
      height: 120,
    });

    chartRef.current = chart;

    // Histogram
    const histogramSeries = chart.addHistogramSeries({
      priceFormat: { type: 'price', precision: 4 },
      priceLineVisible: false,
    });

    const histogramData: HistogramData[] = data.histogram
      .map((v) => {
        if (v[1] === null || !Number.isFinite(v[1])) return null;
        const time = toChartDate(v[0]);
        if (!time) return null;
        return {
          time,
          value: v[1],
          color: v[1] >= 0 ? CHART_COLORS.macdHistogramUp : CHART_COLORS.macdHistogramDown,
        } satisfies HistogramData;
      })
      .filter((v): v is HistogramData => v !== null);

    histogramSeries.setData(histogramData);

    // MACD line
    const macdSeries = chart.addLineSeries({
      color: CHART_COLORS.macd,
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    const macdData: LineData[] = data.macd_line
      .map((v) => {
        if (v[1] === null || !Number.isFinite(v[1])) return null;
        const time = toChartDate(v[0]);
        if (!time) return null;
        return {
          time,
          value: v[1],
        } satisfies LineData;
      })
      .filter((v): v is LineData => v !== null);

    macdSeries.setData(macdData);

    // Signal line
    const signalSeries = chart.addLineSeries({
      color: CHART_COLORS.macdSignal,
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    const signalData: LineData[] = data.signal_line
      .map((v) => {
        if (v[1] === null || !Number.isFinite(v[1])) return null;
        const time = toChartDate(v[0]);
        if (!time) return null;
        return {
          time,
          value: v[1],
        } satisfies LineData;
      })
      .filter((v): v is LineData => v !== null);

    signalSeries.setData(signalData);

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data]);

  return (
    <div className="mt-2">
      <div className="text-xs text-gray-400 mb-1">MACD (12, 26, 9)</div>
      <div ref={containerRef} className="rounded-lg overflow-hidden" />
    </div>
  );
}
