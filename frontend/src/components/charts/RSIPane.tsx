import { useEffect, useRef } from 'react';
import { createChart, IChartApi, LineData } from 'lightweight-charts';
import { CHART_COLORS } from '../../utils/constants';
import type { RSIResult } from '../../types/indicator';

interface RSIPaneProps {
  data: RSIResult;
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

export function RSIPane({ data }: RSIPaneProps) {
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
        scaleMargins: { top: 0.1, bottom: 0.1 },
      },
      timeScale: {
        visible: false,
      },
      height: 100,
    });

    chartRef.current = chart;

    // RSI line
    const rsiSeries = chart.addLineSeries({
      color: CHART_COLORS.rsi,
      lineWidth: 2,
      priceLineVisible: false,
    });

    const rsiData: LineData[] = data.values
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

    rsiSeries.setData(rsiData);

    // Overbought/Oversold lines
    chart.addLineSeries({
      color: CHART_COLORS.rsiOverbought,
      lineWidth: 1,
      lineStyle: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    }).setData(
      rsiData.map((d) => ({ time: d.time, value: 70 }))
    );

    chart.addLineSeries({
      color: CHART_COLORS.rsiOversold,
      lineWidth: 1,
      lineStyle: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    }).setData(
      rsiData.map((d) => ({ time: d.time, value: 30 }))
    );

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
      <div className="text-xs text-gray-400 mb-1">RSI (14)</div>
      <div ref={containerRef} className="rounded-lg overflow-hidden" />
    </div>
  );
}
