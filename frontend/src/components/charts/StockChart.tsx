import { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, CandlestickData, LineData, HistogramData } from 'lightweight-charts';
import { useChartStore } from '../../stores/chartStore';
import { CHART_COLORS } from '../../utils/constants';
import type { ChartData } from '../../types/indicator';

interface StockChartProps {
  data: ChartData;
}

export function StockChart({ data }: StockChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const maSeriesRefs = useRef<Map<string, ISeriesApi<'Line'>>>(new Map());

  const { settings } = useChartStore();

  useEffect(() => {
    if (!containerRef.current) return;

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
    };
  }, []);

  // Update data
  useEffect(() => {
    if (!candleSeriesRef.current || !volumeSeriesRef.current || !data.ohlcv) return;

    // Format OHLCV data
    const candleData: CandlestickData[] = data.ohlcv.map((d) => ({
      time: d.timestamp.split('T')[0] as string,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    const volumeData: HistogramData[] = data.ohlcv.map((d) => ({
      time: d.timestamp.split('T')[0] as string,
      value: d.volume,
      color: d.close >= d.open ? CHART_COLORS.volumeUp : CHART_COLORS.volumeDown,
    }));

    candleSeriesRef.current.setData(candleData);
    volumeSeriesRef.current.setData(volumeData);

    // Show/hide volume
    volumeSeriesRef.current.applyOptions({
      visible: settings.showVolume,
    });
  }, [data.ohlcv, settings.showVolume]);

  // Update MA lines
  useEffect(() => {
    if (!chartRef.current || !data.indicators) return;

    const chart = chartRef.current;

    // Helper to update or create MA line
    const updateMALine = (key: string, maData: typeof data.indicators.ma_20w, color: string, visible: boolean) => {
      let series = maSeriesRefs.current.get(key);

      if (!visible) {
        if (series) {
          chart.removeSeries(series);
          maSeriesRefs.current.delete(key);
        }
        return;
      }

      if (!maData?.values) return;

      if (!series) {
        series = chart.addLineSeries({
          color,
          lineWidth: 2,
          priceLineVisible: false,
          lastValueVisible: false,
        });
        maSeriesRefs.current.set(key, series);
      }

      const lineData: LineData[] = maData.values
        .filter((v): v is [string, number] => v[1] !== null)
        .map((v) => ({
          time: v[0].split('T')[0] as string,
          value: v[1],
        }));

      series.setData(lineData);
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
