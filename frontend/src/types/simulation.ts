export enum SimulationStatus {
  CREATED = 'created',
  PREPARING = 'preparing',
  READY = 'ready',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  PAUSED = 'paused',
  // Legacy aliases for compatibility
  PENDING = 'created',
}

export interface Simulation {
  // Backend fields
  simulation_id: string;
  project_id: string;
  graph_id: string;
  enable_twitter: boolean;
  enable_reddit: boolean;
  status: SimulationStatus;
  entities_count: number;
  profiles_count: number;
  entity_types: string[];
  config_generated: boolean;
  config_reasoning?: string;
  current_round: number;
  twitter_status: string;
  reddit_status: string;
  created_at: string;
  updated_at: string;
  error?: string;

  // Frontend convenience fields (mapped from backend)
  id?: string;
  name?: string;
  progress?: number;
  totalRounds?: number;
  platform?: 'twitter' | 'reddit' | 'parallel';
  agentCount?: number;
  startedAt?: Date;
  completedAt?: Date;
}

// API response wrapper
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  count?: number;
}
