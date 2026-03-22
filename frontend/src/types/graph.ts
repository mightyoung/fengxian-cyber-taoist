/**
 * Knowledge Graph Types
 */

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  description?: string;
  properties?: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  type?: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphFilters {
  nodeTypes: string[];
  searchQuery: string;
}

export type NodeType = 'person' | 'organization' | 'location' | 'event' | 'concept';

export interface GraphViewport {
  x: number;
  y: number;
  zoom: number;
}
