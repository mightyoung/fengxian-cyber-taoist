/**
 * Graph API Hook
 */

import { useQuery } from '@tanstack/react-query';
import type { GraphData, GraphNode, GraphEdge } from '@/types/graph';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

/**
 * Backend node structure from Zep API
 */
interface BackendNode {
  uuid: string;
  name: string;
  labels: string[];
  summary: string;
  attributes: Record<string, unknown>;
  created_at: string;
}

/**
 * Backend edge structure from Zep API
 */
interface BackendEdge {
  uuid: string;
  name: string;
  fact: string;
  fact_type: string;
  source_node_uuid: string;
  target_node_uuid: string;
  source_node_name: string;
  target_node_name: string;
  attributes: Record<string, unknown>;
  created_at: string | null;
}

/**
 * Backend graph data response
 */
interface BackendGraphData {
  graph_id: string;
  nodes: BackendNode[];
  edges: BackendEdge[];
  node_count: number;
  edge_count: number;
}

/**
 * Transform backend node to frontend format
 */
function transformNode(backendNode: BackendNode): GraphNode {
  return {
    id: backendNode.uuid,
    label: backendNode.name,
    type: backendNode.labels?.[0] || 'concept',
    description: backendNode.summary || undefined,
    properties: backendNode.attributes,
  };
}

/**
 * Transform backend edge to frontend format
 */
function transformEdge(backendEdge: BackendEdge): GraphEdge {
  return {
    id: backendEdge.uuid,
    source: backendEdge.source_node_uuid,
    target: backendEdge.target_node_uuid,
    label: backendEdge.fact || backendEdge.name || '',
    type: backendEdge.fact_type || undefined,
  };
}

async function fetchGraphData(graphId: string): Promise<GraphData> {
  const response = await fetch(`${API_BASE}/graph/data/${graphId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch graph data');
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.error || 'Failed to fetch graph data');
  }

  const backendData: BackendGraphData = result.data;

  // Transform backend data to frontend format
  return {
    nodes: backendData.nodes.map(transformNode),
    edges: backendData.edges.map(transformEdge),
  };
}

export function useGraphData(graphId: string | null) {
  return useQuery({
    queryKey: ['graph', graphId],
    queryFn: () => fetchGraphData(graphId!),
    enabled: !!graphId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
