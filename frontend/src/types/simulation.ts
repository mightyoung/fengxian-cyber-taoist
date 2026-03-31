// Re-export API types as the single source of truth
export type { ApiResponse, Simulation as SimulationBase } from './api';
export { SimulationStatus } from './api';

// Extend Simulation with frontend convenience fields
import type { Simulation as SimulationBase } from './api';

export interface Simulation extends SimulationBase {
  // Frontend convenience fields (mapped from backend in hooks)
  id?: string;
  name?: string;
  progress?: number;
  totalRounds?: number;
  platform?: 'twitter' | 'reddit' | 'parallel';
  agentCount?: number;
  startedAt?: Date;
  completedAt?: Date;
}
