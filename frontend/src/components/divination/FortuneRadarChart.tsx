'use client';

import { useRef, useEffect, memo } from 'react';
import * as echarts from 'echarts';
import { cn } from '@/lib/utils';

interface FortuneRadarChartProps {
  data: FortuneData;
  size?: string;
  theme?: 'light' | 'dark';
  className?: string;
}

export interface FortuneData {
  career: number;      // 事业
  wealth: number;      // 财运
  relationship: number; // 感情
  health: number;      // 健康
  social: number;      // 人际
}

const DIMENSIONS = [
  { name: '事业', key: 'career' as const, color: '#D4AF37' },
  { name: '财运', key: 'wealth' as const, color: '#FFD700' },
  { name: '感情', key: 'relationship' as const, color: '#FF69B4' },
  { name: '健康', key: 'health' as const, color: '#50C878' },
  { name: '人际', key: 'social' as const, color: '#87CEEB' },
];

const DARK_THEME_COLORS = {
  background: 'transparent',
  text: '#94A3B8',
  splitLine: 'rgba(148, 163, 184, 0.1)',
  splitArea: 'rgba(30, 41, 59, 0.5)',
  radarFill: 'rgba(212, 175, 55, 0.15)',
  radarBorder: '#D4AF37',
};

const LIGHT_THEME_COLORS = {
  background: 'transparent',
  text: '#475569',
  splitLine: 'rgba(71, 85, 105, 0.15)',
  splitArea: 'rgba(241, 245, 249, 0.8)',
  radarFill: 'rgba(212, 175, 55, 0.2)',
  radarBorder: '#B8860B',
};

function FortuneRadarChartComponent({
  data,
  size = '400px',
  theme = 'dark',
  className,
}: FortuneRadarChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Initialize chart
    const chart = echarts.init(chartRef.current, theme === 'dark' ? 'dark' : undefined);
    chartInstance.current = chart;

    const colors = theme === 'dark' ? DARK_THEME_COLORS : LIGHT_THEME_COLORS;
    const valueArray = [
      data.career,
      data.wealth,
      data.relationship,
      data.health,
      data.social,
    ];

    const option: echarts.EChartsOption = {
      backgroundColor: colors.background,
      tooltip: {
        trigger: 'item',
        backgroundColor: theme === 'dark' ? 'rgba(15, 23, 42, 0.9)' : 'rgba(255, 255, 255, 0.95)',
        borderColor: theme === 'dark' ? 'rgba(212, 175, 55, 0.3)' : 'rgba(184, 134, 11, 0.3)',
        textStyle: {
          color: colors.text,
        },
        formatter: (params: unknown) => {
          const p = params as { name?: string; value?: number };
          if (p.name) {
            const dim = DIMENSIONS.find(d => d.name === p.name);
            return `<div style="font-weight: 600; margin-bottom: 4px;">${p.name}</div>
                    <div style="color: ${dim?.color || '#D4AF37'}">
                      得分: <strong>${p.value}</strong>/100
                    </div>`;
          }
          return '';
        },
      },
      radar: {
        indicator: DIMENSIONS.map((dim) => ({
          name: dim.name,
          max: 100,
        })),
        shape: 'polygon',
        splitNumber: 4,
        axisName: {
          color: colors.text,
          fontSize: 13,
          fontWeight: 500,
        },
        splitLine: {
          lineStyle: {
            color: colors.splitLine,
            width: 1,
          },
        },
        splitArea: {
          areaStyle: {
            color: [colors.splitArea, 'transparent'],
          },
        },
        axisLine: {
          lineStyle: {
            color: colors.splitLine,
          },
        },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: valueArray,
              name: '运势分析',
              symbol: 'circle',
              symbolSize: 6,
              lineStyle: {
                color: colors.radarBorder,
                width: 2,
              },
              areaStyle: {
                color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
                  { offset: 0, color: colors.radarFill },
                  { offset: 1, color: 'transparent' },
                ]),
              },
              itemStyle: {
                color: colors.radarBorder,
                borderColor: colors.radarBorder,
                borderWidth: 2,
              },
              label: {
                show: true,
                formatter: '{c}',
                position: 'right',
                color: colors.radarBorder,
                fontSize: 12,
                fontWeight: 600,
              },
            },
          ],
        },
      ],
    };

    chart.setOption(option);

    // Handle resize
    const handleResize = () => {
      chart.resize();
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.dispose();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme]);

  // Update chart when data changes
  useEffect(() => {
    if (!chartInstance.current) return;

    const colors = theme === 'dark' ? DARK_THEME_COLORS : LIGHT_THEME_COLORS;
    const valueArray = [
      data.career,
      data.wealth,
      data.relationship,
      data.health,
      data.social,
    ];

    chartInstance.current.setOption({
      series: [
        {
          type: 'radar',
          data: [
            {
              value: valueArray,
              name: '运势分析',
              symbol: 'circle',
              symbolSize: 6,
              lineStyle: {
                color: colors.radarBorder,
                width: 2,
              },
              areaStyle: {
                color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
                  { offset: 0, color: colors.radarFill },
                  { offset: 1, color: 'transparent' },
                ]),
              },
              itemStyle: {
                color: colors.radarBorder,
                borderColor: colors.radarBorder,
                borderWidth: 2,
              },
              label: {
                show: true,
                formatter: '{c}',
                position: 'right',
                color: colors.radarBorder,
                fontSize: 12,
                fontWeight: 600,
              },
            },
          ],
        },
      ],
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, theme]);

  return (
    <div
      ref={chartRef}
      className={cn('min-h-[300px]', className)}
      style={{ width: size, height: size }}
    />
  );
}

// Export types
export type { FortuneRadarChartProps };

// Default data for preview/testing
export const DEFAULT_FORTUNE_DATA: FortuneData = {
  career: 75,
  wealth: 70,
  relationship: 65,
  health: 80,
  social: 60,
};

// Memoized component
export const FortuneRadarChart = memo(FortuneRadarChartComponent);
FortuneRadarChart.displayName = 'FortuneRadarChart';

export default FortuneRadarChart;
