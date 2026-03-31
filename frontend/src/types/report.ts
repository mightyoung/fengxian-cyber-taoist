/**
 * Report Types
 *
 * Re-exports from api.ts as single source of truth,
 * with additional frontend-specific types.
 */

// Re-export API types as types (interfaces are always type-only)
export type { Report, ReportOutline, ReportSection, ReportStatus, ReportMetrics } from './api';

// Additional frontend-specific types
export interface ExportFormat {
  type: 'pdf' | 'json' | 'markdown';
  label: string;
  icon?: string;
}
