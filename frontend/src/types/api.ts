/**
 * API Contract - FengxianCyberTaoist Frontend-Backend Contract
 *
 * All API responses follow the standard wrapper format.
 * Field naming: snake_case from backend, camelCase in frontend types.
 */

// =============================================================================
// RESPONSE WRAPPER
// =============================================================================

/**
 * Standard API response wrapper
 * All backend endpoints return this format.
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  count?: number;
}

// =============================================================================
// SIMULATION API
// =============================================================================

/**
 * Simulation status enum (backend: string values)
 */
export enum SimulationStatus {
  PENDING = 'pending',
  CREATED = 'created',
  PREPARING = 'preparing',
  READY = 'ready',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  PAUSED = 'paused',
}

/**
 * Simulation state (backend: simulation_manager.SimulationState.to_dict())
 * Field naming: snake_case from backend
 */
export interface Simulation {
  simulation_id: string;
  project_id: string;
  graph_id: string;
  enable_twitter: boolean;
  enable_reddit: boolean;
  status: SimulationStatus | string;
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
}

/**
 * Create simulation request
 */
export interface CreateSimulationRequest {
  project_id: string;
  graph_id?: string;
  enable_twitter?: boolean;
  enable_reddit?: boolean;
}

/**
 * Start simulation request
 */
export interface StartSimulationRequest {
  simulation_id: string;
  platform?: 'twitter' | 'reddit' | 'parallel';
  max_rounds?: number;
  enable_graph_memory_update?: boolean;
  force?: boolean;
}

/**
 * Simulation run status (from /simulation/{id}/run-status)
 */
export interface SimulationRunStatus {
  simulation_id: string;
  runner_status: 'idle' | 'running' | 'completed' | 'failed';
  current_round: number;
  total_rounds: number;
  progress_percent: number;
  simulated_hours: number;
  total_simulation_hours: number;
  twitter_running: boolean;
  reddit_running: boolean;
  twitter_actions_count: number;
  reddit_actions_count: number;
  total_actions_count: number;
  started_at?: string;
  updated_at?: string;
}

// =============================================================================
// REPORT API
// =============================================================================

/**
 * Report status (backend: report_agent.ReportStatus)
 */
export type ReportStatus = 'generating' | 'completed' | 'failed';

/**
 * Report outline (backend: report_agent.ReportOutline)
 */
export interface ReportOutline {
  title: string;
  summary: string;
  sections: ReportSection[];
}

/**
 * Report section (backend: report_agent.ReportSection)
 */
export interface ReportSection {
  title: string;
  content: string;
}

/**
 * Report (backend: report_agent.ReportManager)
 * Used for simulation prediction reports.
 */
export interface Report {
  report_id: string;
  simulation_id: string;
  graph_id: string;
  simulation_requirement: string;
  status: ReportStatus;
  outline?: ReportOutline;
  markdown_content?: string;
  created_at: string;
  completed_at?: string;
  error?: string;
}

/**
 * Divination Report (backend: report_service.Report)
 * Used for astrology/divination analysis reports.
 */
export interface DivinationReport {
  report_id: string;
  report_type: 'divination' | 'simulation';
  format: 'markdown' | 'pdf';
  status: ReportStatus;
  title: string;
  markdown_content: string;
  pdf_path?: string;
  metadata?: Record<string, unknown>;
  error?: string;
  created_at: string;
  completed_at?: string;
}

/**
 * Generate report request
 */
export interface GenerateReportRequest {
  simulation_id: string;
  force_regenerate?: boolean;
}

/**
 * Report metrics
 */
export interface ReportMetrics {
  totalPosts: number;
  totalEngagement: number;
  sentimentScore: number;
  topInfluencers: { name: string; score: number }[];
}

// =============================================================================
// GRAPH API
// =============================================================================

/**
 * Project (backend: models.project.Project)
 */
export interface Project {
  project_id: string;
  name: string;
  simulation_requirement: string;
  status: string;
  files: { filename: string; size: number }[];
  total_text_length?: number;
  ontology?: {
    entity_types: string[];
    edge_types: string[];
  };
  analysis_summary?: string;
  graph_id?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Build graph request
 */
export interface BuildGraphRequest {
  project_id: string;
  graph_name?: string;
  chunk_size?: number;
  chunk_overlap?: number;
  force?: boolean;
}

// =============================================================================
// DIVINATION API
// =============================================================================

/**
 * Real-time Vibe (backend: /report/vibe)
 */
export interface RealtimeVibe {
  timestamp: string;
  vibe_score: number;
  current_focus: string;
  instant_transforms: string[];
  advice: string;
}

/**
 * Cyber Poster / Talisman (backend: /v1/system/poster)
 */
export interface VibePoster {
  title: string;
  date: string;
  vibe_score: number;
  keywords: string[];
  talisman_svg_params: {
    core: string;
    energy_color: string;
  };
  motto: string;
}

/**
 * Consultation Request (backend: /report/consult)
 */
export interface ConsultRequest {
  message: string;
  simulation_id?: string;
  chart_id?: string;
  chat_history: { role: 'user' | 'assistant'; content: string }[];
}

/**
 * Birth chart input (Extended to support raw text pasting)
 */
export interface BirthChartInput {
  year?: number;
  month?: number;
  day?: number;
  hour?: number;
  minute?: number;
  gender: 'male' | 'female';
  name?: string;
  raw_text?: string; // For Wenmo Tianji pasting
}

/**
 * Refined Divination Report (Three-Layer Fusion)
 */
export interface DivinationReport {
  report_id: string;
  user_name: string;
  target_year: number;
  report_type: string;
  markdown_content: string;
  metadata?: {
    overall_judgment?: string;
    overall_confidence?: number;
    user_rating?: number;
    user_comment?: string;
    [key: string]: unknown;
  };
  created_at: string;
  status: string;
}

/**
 * Divination chart summary used by the content center
 */
export interface DivinationChartSummary {
  chart_id: string;
  birth_info: BirthChartInput;
  status: string;
  created_at: string;
  updated_at: string;
  analysis?: Record<string, unknown> | null;
  report_count: number;
}

// =============================================================================
// SIMULATION API EXTENSIONS
// =============================================================================

/**
 * Simulation Fork Request
 */
export interface ForkSimulationRequest {
  parent_id: string;
  intervention_config?: Record<string, unknown>;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

/**
 * Pagination helpers
 */
export interface PaginatedResponse<T> {
  data: T[];
  count: number;
  total?: number;
  page?: number;
  limit?: number;
}

/**
 * Task status (backend: task.TaskStatus)
 */
export interface TaskStatus {
  task_id: string;
  task_type?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  error?: string;
  result?: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
}
