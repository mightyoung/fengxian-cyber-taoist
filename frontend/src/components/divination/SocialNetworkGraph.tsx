'use client';

import { useRef, useEffect, memo, useCallback } from 'react';
import * as echarts from 'echarts';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

export interface PalaceNode {
  id: string;
  name: string;
  main_star: string;
  strength: '强' | '中' | '弱';
  star_count: number;
  transform_count: number;
  location: string;
}

export interface PalaceRelation {
  source: string;
  target: string;
  type: '相生' | '相克' | '相合' | '相冲' | '相刑' | '三合';
  label?: string;
}

export interface SocialNetworkGraphProps {
  palaceData: PalaceNode[];
  relations: PalaceRelation[];
  size?: string;
  theme?: 'light' | 'dark';
  className?: string;
  onNodeClick?: (palace: PalaceNode) => void;
}

// ============================================================================
// Constants
// ============================================================================

const PALACE_POSITIONS: Record<string, { x: number; y: number }> = {
  '命宫': { x: 0, y: -200 },
  '兄弟宫': { x: 100, y: -173 },
  '夫妻宫': { x: 173, y: -100 },
  '子女宫': { x: 200, y: 0 },
  '财帛宫': { x: 173, y: 100 },
  '疾厄宫': { x: 100, y: 173 },
  '迁移宫': { x: 0, y: 200 },
  '官禄宫': { x: -100, y: 173 },
  '田宅宫': { x: -173, y: 100 },
  '福德宫': { x: -200, y: 0 },
  '父母宫': { x: -173, y: -100 },
  '奴仆宫': { x: -100, y: -173 },
};

const RELATION_COLORS = {
  '相生': '#22C55E',
  '相克': '#EF4444',
  '相合': '#3B82F6',
  '相冲': '#F97316',
  '相刑': '#A855F7',
  '三合': '#06B6D4',
};

const STRENGTH_COLORS = {
  '强': '#22C55E',
  '中': '#EAB308',
  '弱': '#EF4444',
};

const DARK_THEME = {
  background: 'transparent',
  text: '#94A3B8',
  nodeBorder: 'rgba(212, 175, 55, 0.6)',
  nodeBg: 'rgba(15, 23, 42, 0.9)',
  linkLine: 'rgba(148, 163, 184, 0.3)',
};

const LIGHT_THEME = {
  background: 'transparent',
  text: '#475569',
  nodeBorder: 'rgba(184, 134, 11, 0.6)',
  nodeBg: 'rgba(255, 255, 255, 0.95)',
  linkLine: 'rgba(71, 85, 105, 0.3)',
};

// ============================================================================
// Component
// ============================================================================

function SocialNetworkGraphComponent({
  palaceData,
  relations,
  size = '500px',
  theme = 'dark',
  className,
  onNodeClick,
}: SocialNetworkGraphProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  // Build ECharts option
  const buildOption = useCallback(() => {
    const colors = theme === 'dark' ? DARK_THEME : LIGHT_THEME;

    // Process nodes
    const nodes = palaceData.map((palace) => {
      const position = PALACE_POSITIONS[palace.name];
      return {
        id: palace.id,
        name: palace.name,
        x: position?.x ?? 0,
        y: position?.y ?? 0,
        value: [position?.x ?? 0, position?.y ?? 0],
        main_star: palace.main_star,
        strength: palace.strength,
        star_count: palace.star_count,
        transform_count: palace.transform_count,
        location: palace.location,
        itemStyle: {
          color: {
            type: 'radial' as const,
            x: 0.5,
            y: 0.5,
            r: 0.5,
            colorStops: [
              { offset: 0, color: colors.nodeBg },
              { offset: 1, color: STRENGTH_COLORS[palace.strength] + '40' },
            ],
          } as echarts.RadialGradientObject,
          borderColor: STRENGTH_COLORS[palace.strength],
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: STRENGTH_COLORS[palace.strength] + '60',
        },
      };
    });

    // Process edges
    const edges = relations.map((relation, idx) => ({
      id: `edge-${idx}`,
      source: relation.source,
      target: relation.target,
      name: relation.type,
      lineStyle: {
        color: RELATION_COLORS[relation.type] || colors.linkLine,
        width: 2,
        curveness: 0.2,
        opacity: 0.8,
      },
      label: {
        show: true,
        formatter: relation.type,
        fontSize: 10,
        color: RELATION_COLORS[relation.type] || colors.text,
        backgroundColor: theme === 'dark' ? 'rgba(15, 23, 42, 0.8)' : 'rgba(255, 255, 255, 0.8)',
        padding: [2, 4],
        borderRadius: 2,
      },
    }));

    const option: echarts.EChartsOption = {
      backgroundColor: colors.background,
      tooltip: {
        trigger: 'item',
        backgroundColor: theme === 'dark' ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
        borderColor: theme === 'dark' ? 'rgba(212, 175, 55, 0.3)' : 'rgba(184, 134, 11, 0.3)',
        textStyle: {
          color: colors.text,
        },
        formatter: (params: unknown) => {
          const p = params as { dataType?: string; data?: Record<string, unknown> };
          if (p.dataType === 'node' && p.data) {
            const node = p.data;
            return `
              <div style="padding: 4px;">
                <div style="font-weight: 600; font-size: 14px; margin-bottom: 6px; color: #D4AF37;">
                  ${node.name as string}
                </div>
                <div style="font-size: 12px; color: ${colors.text};">
                  <div style="margin-bottom: 4px;">
                    <span style="color: #94A3B8;">主星:</span>
                    <span style="color: #F0F0F0;">${node.main_star as string}</span>
                  </div>
                  <div style="margin-bottom: 4px;">
                    <span style="color: #94A3B8;">强弱:</span>
                    <span style="color: ${STRENGTH_COLORS[node.strength as keyof typeof STRENGTH_COLORS]};">
                      ${node.strength as string}
                    </span>
                  </div>
                  <div style="margin-bottom: 4px;">
                    <span style="color: #94A3B8;">星曜:</span>
                    <span style="color: #F0F0F0;">${node.star_count as number}颗</span>
                  </div>
                  <div style="margin-bottom: 4px;">
                    <span style="color: #94A3B8;">四化:</span>
                    <span style="color: #F0F0F0;">${node.transform_count as number}个</span>
                  </div>
                  <div>
                    <span style="color: #94A3B8;">位置:</span>
                    <span style="color: #F0F0F0;">${node.location as string}</span>
                  </div>
                </div>
              </div>
            `;
          }
          if (p.dataType === 'edge' && p.data) {
            const edge = p.data;
            return `
              <div style="padding: 4px;">
                <div style="font-weight: 600; color: ${edge.name as string};">
                  ${edge.name as string}
                </div>
              </div>
            `;
          }
          return '';
        },
      },
      series: [
        {
          type: 'graph',
          layout: 'none',
          coordinateSystem: 'cartesian2d',
          symbolSize: 60,
          roam: true,
          zoom: 1,
          draggable: true,
          focusNodeAdjacency: true,
          lineStyle: {
            width: 2,
            curveness: 0.2,
            opacity: 0.8,
          },
          label: {
            show: true,
            position: 'bottom',
            distance: 8,
            formatter: '{b}',
            fontSize: 12,
            fontWeight: 500,
            color: colors.text,
          },
          labelLayout: {
            hideOverlap: false,
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 4,
              opacity: 1,
            },
            itemStyle: {
              shadowBlur: 20,
              shadowColor: 'rgba(212, 175, 55, 0.5)',
            },
          },
          data: nodes,
          edges: edges,
        },
      ],
      xAxis: {
        show: false,
        min: -250,
        max: 250,
      },
      yAxis: {
        show: false,
        min: -250,
        max: 250,
      },
    };

    return option;
  }, [palaceData, relations, theme]);

  // Initialize chart
  useEffect(() => {
    if (!chartRef.current) return;

    const chart = echarts.init(chartRef.current, theme === 'dark' ? 'dark' : undefined);
    chartInstance.current = chart;

    chart.setOption(buildOption());

    // Handle node click
    const handleClick = (params: unknown) => {
      const p = params as { dataType?: string; data?: Record<string, unknown> };
      if (p.dataType === 'node' && p.data && onNodeClick) {
        const palace = palaceData.find(pal => pal.id === p.data?.id);
        if (palace) {
          onNodeClick(palace);
        }
      }
    };

    chart.on('click', handleClick);

    // Handle resize
    const handleResize = () => {
      chart.resize();
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.off('click', handleClick);
      chart.dispose();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme]);

  // Update chart when data changes
  useEffect(() => {
    if (!chartInstance.current) return;
    chartInstance.current.setOption(buildOption());
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [palaceData, relations, theme]);

  return (
    <div
      ref={chartRef}
      className={cn('min-h-[400px]', className)}
      style={{ width: size, height: size }}
    />
  );
}

// ============================================================================
// Default Data
// ============================================================================

export const DEFAULT_PALACE_DATA: PalaceNode[] = [
  { id: 'menggong', name: '命宫', main_star: '天机', strength: '强', star_count: 5, transform_count: 2, location: '卯宫' },
  { id: 'xiongdigong', name: '兄弟宫', main_star: '太阳', strength: '中', star_count: 3, transform_count: 1, location: '卯宫' },
  { id: 'fuqigong', name: '夫妻宫', main_star: '太阴', strength: '强', star_count: 4, transform_count: 2, location: '丑宫' },
  { id: 'zinvgong', name: '子女宫', main_star: '天同', strength: '弱', star_count: 2, transform_count: 0, location: '寅宫' },
  { id: 'caibogong', name: '财帛宫', main_star: '武曲', strength: '强', star_count: 6, transform_count: 1, location: '辰宫' },
  { id: 'jieggong', name: '疾厄宫', main_star: '天枢', strength: '中', star_count: 3, transform_count: 1, location: '卯宫' },
  { id: 'qianyigong', name: '迁移宫', main_star: '太阳', strength: '强', star_count: 5, transform_count: 2, location: '午宫' },
  { id: 'guanlugong', name: '官禄宫', main_star: '紫微', strength: '强', star_count: 7, transform_count: 3, location: '巳宫' },
  { id: 'tianzhgong', name: '田宅宫', main_star: '贪狼', strength: '中', star_count: 4, transform_count: 1, location: '辰宫' },
  { id: 'fukegong', name: '福德宫', main_star: '天梁', strength: '强', star_count: 3, transform_count: 2, location: '未宫' },
  { id: 'fumugong', name: '父母宫', main_star: '天府', strength: '中', star_count: 4, transform_count: 0, location: '申宫' },
  { id: 'nupugong', name: '奴仆宫', main_star: '七杀', strength: '弱', star_count: 2, transform_count: 1, location: '酉宫' },
];

export const DEFAULT_RELATIONS: PalaceRelation[] = [
  { source: 'menggong', target: 'xiongdigong', type: '相生' },
  { source: 'menggong', target: 'fuqigong', type: '相合' },
  { source: 'menggong', target: 'guanlugong', type: '相生' },
  { source: 'xiongdigong', target: 'fuqigong', type: '相克' },
  { source: 'fuqigong', target: 'zinvgong', type: '相生' },
  { source: 'zinvgong', target: 'caibogong', type: '相合' },
  { source: 'caibogong', target: 'jieggong', type: '相克' },
  { source: 'jieggong', target: 'qianyigong', type: '相冲' },
  { source: 'qianyigong', target: 'guanlugong', type: '相刑' },
  { source: 'guanlugong', target: 'tianzhgong', type: '三合' },
  { source: 'tianzhgong', target: 'fukegong', type: '相生' },
  { source: 'fukegong', target: 'fumugong', type: '相合' },
  { source: 'fumugong', target: 'nupugong', type: '相克' },
  { source: 'nupugong', target: 'menggong', type: '相冲' },
];

// Memoized component
export const SocialNetworkGraph = memo(SocialNetworkGraphComponent);
SocialNetworkGraph.displayName = 'SocialNetworkGraph';

// ============================================================================
// Utility Functions
// ============================================================================

export function getRelationSummary(relations: PalaceRelation[]) {
  const summary: Record<string, number> = {};
  relations.forEach(r => {
    summary[r.type] = (summary[r.type] || 0) + 1;
  });
  return summary;
}

export function getPalaceConnections(palaceId: string, relations: PalaceRelation[]) {
  const connections: { palace: string; type: PalaceRelation['type'] }[] = [];
  relations.forEach(r => {
    if (r.source === palaceId) {
      connections.push({ palace: r.target, type: r.type });
    }
    if (r.target === palaceId) {
      connections.push({ palace: r.source, type: r.type });
    }
  });
  return connections;
}
