'use client';

import { useRef, useEffect, useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

// Type definitions
export interface MonthlyTrendData {
  /** Months 1-12 */
  months: number[];
  /** Career fortune scores (0-100) */
  career?: number[];
  /** Wealth fortune scores (0-100) */
  wealth?: number[];
  /** Relationship fortune scores (0-100) */
  love?: number[];
  /** Health fortune scores (0-100) */
  health?: number[];
}

export interface MonthlyTrendChartProps {
  /** 12-month fortune data */
  data: MonthlyTrendData;
  /** Dimensions to display, defaults to all available */
  dimensions?: Array<'career' | 'wealth' | 'love' | 'health'>;
  /** Chart title */
  title?: string;
  /** Height of the chart in pixels */
  height?: number;
  /** Whether to show legend */
  showLegend?: boolean;
  /** Whether to show key point markers (peak/low) */
  showMarkers?: boolean;
  /** Theme: 'dark' or 'light' */
  theme?: 'dark' | 'light';
}

type DimensionKey = 'career' | 'wealth' | 'love' | 'health';

interface DimensionConfig {
  key: DimensionKey;
  label: string;
  color: string;
  gradientColor: string;
}

const DIMENSION_CONFIGS: Record<DimensionKey, DimensionConfig> = {
  career: {
    key: 'career',
    label: '事业',
    color: '#f59e0b',
    gradientColor: '#fbbf24',
  },
  wealth: {
    key: 'wealth',
    label: '财运',
    color: '#10b981',
    gradientColor: '#34d399',
  },
  love: {
    key: 'love',
    label: '感情',
    color: '#ec4899',
    gradientColor: '#f472b6',
  },
  health: {
    key: 'health',
    label: '健康',
    color: '#06b6d4',
    gradientColor: '#22d3ee',
  },
};

const MONTH_LABELS = [
  '一月', '二月', '三月', '四月', '五月', '六月',
  '七月', '八月', '九月', '十月', '十一月', '十二月',
];

const MARKDOWN_LABELS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
];

function findPeaksAndLows(values: number[]): { peakIndices: number[]; lowIndices: number[] } {
  if (values.length < 3) {
    return { peakIndices: [], lowIndices: [] };
  }

  const peakIndices: number[] = [];
  const lowIndices: number[] = [];

  for (let i = 1; i < values.length - 1; i++) {
    if (values[i] > values[i - 1] && values[i] > values[i + 1]) {
      peakIndices.push(i);
    }
    if (values[i] < values[i - 1] && values[i] < values[i + 1]) {
      lowIndices.push(i);
    }
  }

  return { peakIndices, lowIndices };
}

function formatTooltip(params: Array<{ seriesName: string; value: number; color: string; dataIndex?: number }>): string {
  const month = params[0]?.dataIndex ?? 0;
  let html = `<div style="font-weight: bold; margin-bottom: 8px;">${MONTH_LABELS[month]}</div>`;

  params.forEach((param) => {
    if (param.value !== null && param.value !== undefined) {
      const score = Math.round(param.value as number);
      const status =
        score >= 80 ? '大吉' :
        score >= 60 ? '吉' :
        score >= 40 ? '平' :
        score >= 20 ? '凶' : '大凶';
      html += `
        <div style="display: flex; align-items: center; gap: 8px; margin: 4px 0;">
          <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: ${param.color};"></span>
          <span>${param.seriesName}: ${score}分 (${status})</span>
        </div>
      `;
    }
  });

  return html;
}

export function MonthlyTrendChart({
  data,
  dimensions = ['career', 'wealth', 'love', 'health'],
  title = '月度运势走势',
  height = 400,
  showLegend = true,
  showMarkers = true,
  theme = 'dark',
}: MonthlyTrendChartProps) {
  const chartRef = useRef<ReactECharts>(null);

  // Theme colors
  const themeColors = useMemo(() => ({
    background: theme === 'dark' ? 'transparent' : '#ffffff',
    text: theme === 'dark' ? '#94a3b8' : '#64748b',
    axis: theme === 'dark' ? '#475569' : '#cbd5e1',
    grid: theme === 'dark' ? 'rgba(148, 163, 184, 0.1)' : 'rgba(100, 116, 139, 0.1)',
  }), [theme]);

  // Generate chart options
  const option: EChartsOption = useMemo(() => {
    const series: EChartsOption['series'] = [];

    dimensions.forEach((dimKey) => {
      const config = DIMENSION_CONFIGS[dimKey];
      const values = data[dimKey];

      if (!values || values.length === 0) return;

      // Find peak and low points
      const { peakIndices, lowIndices } = showMarkers
        ? findPeaksAndLows(values)
        : { peakIndices: [], lowIndices: [] };

      const markPointData: Array<{ type: 'max' | 'min'; name: string; coord: [number, number] }> = [];

      peakIndices.forEach((idx) => {
        markPointData.push({
          type: 'max',
          name: '高峰',
          coord: [idx, values[idx]],
        });
      });

      lowIndices.forEach((idx) => {
        markPointData.push({
          type: 'min',
          name: '低谷',
          coord: [idx, values[idx]],
        });
      });

      series.push({
        name: config.label,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: config.color,
        },
        itemStyle: {
          color: config.color,
          borderWidth: 2,
          borderColor: theme === 'dark' ? '#0f172a' : '#ffffff',
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: `${config.color}40` },
              { offset: 1, color: `${config.color}05` },
            ],
          },
        },
        emphasis: {
          scale: true,
          itemStyle: {
            borderWidth: 3,
            shadowBlur: 10,
            shadowColor: config.color,
          },
        },
        markPoint: showMarkers && markPointData.length > 0 ? {
          symbol: 'circle',
          symbolSize: (value: number, params: unknown) => {
            const p = params as { dataType?: string };
            return p.dataType === 'max' ? 25 : 20;
          },
          label: {
            formatter: (params: unknown) => {
              const p = params as { data?: { type?: string } };
              return p.data?.type === 'max' ? '高峰' : '低谷';
            },
            color: theme === 'dark' ? '#f8fafc' : '#1e293b',
            fontSize: 11,
          },
          data: markPointData,
        } : undefined,
        data: values,
      });
    });

    return {
      backgroundColor: themeColors.background,
      animation: true,
      animationDuration: 1000,
      animationEasing: 'cubicOut',
      grid: {
        left: 50,
        right: 30,
        top: showLegend ? 60 : 40,
        bottom: 50,
        containLabel: false,
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: theme === 'dark' ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        borderColor: theme === 'dark' ? '#334155' : '#e2e8f0',
        borderWidth: 1,
        padding: [12, 16],
        textStyle: {
          color: theme === 'dark' ? '#f1f5f9' : '#334155',
          fontSize: 13,
        },
        axisPointer: {
          type: 'cross',
          crossStyle: {
            color: themeColors.axis,
          },
          lineStyle: {
            color: themeColors.axis,
            type: 'dashed',
          },
        },
        formatter: (params: unknown) => formatTooltip(params as Array<{ seriesName: string; value: number; color: string }>),
      },
      legend: showLegend ? {
        show: true,
        top: 10,
        textStyle: {
          color: themeColors.text,
          fontSize: 13,
        },
        itemWidth: 20,
        itemHeight: 10,
        itemGap: 20,
      } : undefined,
      xAxis: {
        type: 'category',
        data: MARKDOWN_LABELS,
        boundaryGap: false,
        axisLine: {
          lineStyle: {
            color: themeColors.axis,
          },
        },
        axisTick: {
          lineStyle: {
            color: themeColors.axis,
          },
        },
        axisLabel: {
          color: themeColors.text,
          fontSize: 12,
          margin: 12,
        },
        splitLine: {
          show: false,
        },
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        interval: 20,
        axisLine: {
          show: false,
        },
        axisTick: {
          show: false,
        },
        axisLabel: {
          color: themeColors.text,
          fontSize: 12,
          formatter: '{value}',
        },
        splitLine: {
          lineStyle: {
            color: themeColors.grid,
            type: 'dashed',
          },
        },
      },
      series,
    };
  }, [data, dimensions, showLegend, showMarkers, theme, themeColors]);

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      chartRef.current?.getEchartsInstance()?.resize();
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Calculate summary stats
  const summaryStats = useMemo(() => {
    const stats: Array<{
      key: DimensionKey;
      label: string;
      avg: number;
      trend: 'up' | 'down' | 'stable';
      bestMonth: number;
      worstMonth: number;
    }> = [];

    dimensions.forEach((dimKey) => {
      const config = DIMENSION_CONFIGS[dimKey];
      const values = data[dimKey];
      if (!values || values.length === 0) return;

      const avg = Math.round(values.reduce((a, b) => a + b, 0) / values.length);
      const diff = values[values.length - 1] - values[0];
      const trend = diff > 5 ? 'up' : diff < -5 ? 'down' : 'stable';

      let bestMonth = 0;
      let worstMonth = 0;
      let bestValue = -Infinity;
      let worstValue = Infinity;

      values.forEach((val, idx) => {
        if (val > bestValue) {
          bestValue = val;
          bestMonth = idx;
        }
        if (val < worstValue) {
          worstValue = val;
          worstMonth = idx;
        }
      });

      stats.push({
        key: dimKey,
        label: config.label,
        avg,
        trend,
        bestMonth: bestMonth + 1,
        worstMonth: worstMonth + 1,
      });
    });

    return stats;
  }, [data, dimensions]);

  return (
    <Card className="border-amber-500/20 bg-gradient-to-br from-slate-900/80 to-slate-950/80">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-amber-400">
          <svg
            className="h-5 w-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M3 3v18h18" />
            <path d="m19 9-5 5-4-4-3 3" />
          </svg>
          {title}
        </CardTitle>
        <CardDescription>12个月运势变化趋势分析</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Chart */}
        <ReactECharts
          ref={chartRef}
          option={option}
          style={{ height: `${height}px`, width: '100%' }}
          opts={{ renderer: 'canvas' }}
        />

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {summaryStats.map((stat) => (
            <div
              key={stat.key}
              className="flex flex-col p-3 rounded-lg bg-slate-800/50 border border-slate-700/50"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">{stat.label}</span>
                <Badge
                  variant="outline"
                  className="text-xs"
                  style={{
                    borderColor: DIMENSION_CONFIGS[stat.key].color,
                    color: DIMENSION_CONFIGS[stat.key].color,
                  }}
                >
                  {stat.trend === 'up' ? '↑' : stat.trend === 'down' ? '↓' : '→'} {stat.avg}分
                </Badge>
              </div>
              <div className="flex justify-between text-xs text-slate-500">
                <span>最佳: {MONTH_LABELS[stat.bestMonth - 1]}</span>
                <span>低谷: {MONTH_LABELS[stat.worstMonth - 1]}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Legend for peak/low */}
        {showMarkers && (
          <div className="flex items-center justify-center gap-6 text-xs text-slate-500">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500" />
              <span>高峰点</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500" />
              <span>低谷点</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default MonthlyTrendChart;
