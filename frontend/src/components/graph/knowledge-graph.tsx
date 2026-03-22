'use client';

import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  BackgroundVariant,
  Panel,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { motion } from 'framer-motion';
import { GraphNodeMemoized } from './graph-node';
import { GraphControlsMemoized } from './graph-controls';
import { useGraphData } from '@/hooks/use-graph';
import type { GraphData } from '@/types/graph';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { ANIMATIONS } from '@/lib/animation';

const nodeTypes = {
  graphNode: GraphNodeMemoized,
};

interface KnowledgeGraphProps {
  graphId: string | null;
  className?: string;
  onNodeClick?: (nodeId: string) => void;
  fallbackData?: GraphData;
}

export function KnowledgeGraph({
  graphId,
  className,
  onNodeClick,
}: KnowledgeGraphProps) {
  const { data: graphData, isLoading, error } = useGraphData(graphId);

  // Use real data from backend
  const displayData = graphData;

  const initialNodes = useMemo(() => {
    if (!graphData?.nodes) return [];

    return graphData.nodes.map((node): Node => ({
      id: node.id,
      type: 'graphNode',
      position: {
        x: Math.random() * 500,
        y: Math.random() * 500,
      },
      data: {
        label: node.label,
        description: node.description,
        type: node.type,
      },
    }));
  }, [graphData?.nodes]);

  const initialEdges = useMemo(() => {
    if (!graphData?.edges) return [];

    return graphData.edges.map((edge): Edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      type: 'smoothstep',
      animated: true,
      style: {
        stroke: '#486581',
        strokeWidth: 2,
      },
      labelStyle: {
        fill: '#94a3b8',
        fontSize: 12,
      },
    }));
  }, [graphData?.edges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onNodeClickHandler = useCallback(
    (_: React.MouseEvent, node: Node) => {
      onNodeClick?.(node.id);
    },
    [onNodeClick]
  );

  if (isLoading) {
    return (
      <div className={cn('w-full h-full flex items-center justify-center', className)}>
        <div className="flex flex-col items-center gap-4">
          <Skeleton className="w-[600px] h-[400px] bg-slate-800" />
          <p className="text-slate-400 text-sm">Loading knowledge graph...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn('w-full h-full flex items-center justify-center', className)}>
        <div className="text-center p-6 bg-red-950/30 border border-red-900 rounded-lg">
          <p className="text-red-400">Failed to load knowledge graph</p>
          <p className="text-slate-400 text-sm mt-2">{error.message}</p>
        </div>
      </div>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className={cn('w-full h-full flex items-center justify-center', className)}>
        <div className="text-center p-6 bg-slate-900/50 border border-slate-800 rounded-lg">
          <p className="text-slate-300">No graph data available</p>
          <p className="text-slate-500 text-sm mt-2">
            Build a graph first to visualize it here
          </p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: ANIMATIONS.standard.duration / 1000 }}
      className={cn('w-full h-full bg-slate-950 rounded-lg overflow-hidden', className)}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClickHandler}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
        }}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#1e293b"
        />

        <Controls
          showInteractive={false}
          className="!bg-slate-900/90 !border-slate-700"
        />

        <MiniMap
          nodeColor={(node) => {
            const type = node.data?.type as string;
            const colors: Record<string, string> = {
              person: '#8B5CF6',
              organization: '#3B82F6',
              location: '#10B981',
              event: '#F59E0B',
              concept: '#EC4899',
            };
            return colors[type] || '#486581';
          }}
          maskColor="rgba(15, 23, 42, 0.8)"
          className="!bg-slate-900/90 !border-slate-700"
        />

        <Panel position="top-right">
          <GraphControlsMemoized />
        </Panel>
      </ReactFlow>
    </motion.div>
  );
}
