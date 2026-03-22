'use client';

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { cn } from '@/lib/utils';
import { COLORS } from '@/lib/colors';
import { GRAPH_CONFIG } from '@/lib/config';

interface GraphNodeData {
  label: string;
  description?: string;
  type: string;
  isSelected?: boolean;
}

const NODE_COLORS: Record<string, string> = {
  person: '#8B5CF6',
  organization: '#3B82F6',
  location: '#10B981',
  event: '#F59E0B',
  concept: '#EC4899',
};

function GraphNode({ data, selected }: NodeProps) {
  const nodeData = data as unknown as GraphNodeData;
  const nodeColor = NODE_COLORS[nodeData.type] || GRAPH_CONFIG.DEFAULT_NODE_COLOR;
  const isSelected = selected || nodeData.isSelected;

  return (
    <div
      className={cn(
        'px-4 py-3 rounded-lg border-2 min-w-[150px] transition-all duration-200',
        'bg-[#0F172A]/90 backdrop-blur-sm',
        isSelected
          ? 'border-[#D4AF37] shadow-lg shadow-[#D4AF37]/20'
          : 'border-slate-700 hover:border-slate-600'
      )}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-slate-500 !w-2 !h-2"
      />

      <div className="flex items-center gap-2">
        <div
          className="w-3 h-3 rounded-full"
          style={{
            backgroundColor: nodeColor,
            boxShadow: `0 0 8px ${nodeColor}60`,
          }}
        />
        <span className="text-sm font-medium text-slate-100">
          {nodeData.label}
        </span>
      </div>

      {nodeData.description && (
        <p className="mt-2 text-xs text-slate-400 line-clamp-2">
          {nodeData.description}
        </p>
      )}

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-slate-500 !w-2 !h-2"
      />
    </div>
  );
}

export const GraphNodeMemoized = memo(GraphNode);
GraphNodeMemoized.displayName = 'GraphNode';
