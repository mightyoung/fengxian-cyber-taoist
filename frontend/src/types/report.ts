/**
 * Report Types
 */

export interface ReportSection {
  filename: string;
  section_index: number;
  content: string;
}

export interface ReportOutline {
  title: string;
  sections: string[];
}

export interface Report {
  report_id: string;
  simulation_id: string;
  status: ReportStatus;
  outline?: ReportOutline;
  markdown_content?: string;
  created_at: string;
  completed_at?: string;
}

export type ReportStatus = 'generating' | 'completed' | 'failed';

export interface ReportMetrics {
  totalPosts: number;
  totalEngagement: number;
  sentimentScore: number;
  topInfluencers: { name: string; score: number }[];
}

export interface ExportFormat {
  type: 'pdf' | 'json' | 'markdown';
  label: string;
  icon?: string;
}
