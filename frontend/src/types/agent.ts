// Agent status enum
export enum AgentStatus {
  IDLE = 'idle',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

// Agent interface
export interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  activity: number; // 0-100
  tweets: number;
  mentions: number;
  engagements: number;
  avatar?: string;
}

// Timeline event platform
export type Platform = 'twitter' | 'reddit';

// Timeline event interface
export interface TimelineEvent {
  id: string;
  timestamp: Date;
  platform: Platform;
  agentId: string;
  action: string;
  content?: string;
}
