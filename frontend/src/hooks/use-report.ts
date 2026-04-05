/**
 * Report API Hook
 *
 * Handles both simulation reports and divination reports with a unified
 * frontend contract.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Report, ReportSection, DivinationReport } from '@/types/api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

type ReportDetail =
  | { kind: 'simulation'; report: Report }
  | { kind: 'divination'; report: DivinationReport };

interface ReportSectionsResponse {
  sections: ReportSection[];
  total_sections: number;
}

async function readJson<T>(response: Response): Promise<T> {
  const data = await response.json();
  if (!data.success) {
    throw new Error(data.error || 'Request failed');
  }
  return data.data as T;
}

// --- Simulation Reports ---

async function fetchReports(): Promise<Report[]> {
  const response = await fetch(`${API_BASE}/report/list`);
  return readJson<Report[]>(response);
}

async function fetchReport(reportId: string): Promise<Report> {
  const response = await fetch(`${API_BASE}/report/${reportId}`);
  const data = await readJson<{ report: Report }>(response);
  return data.report;
}

async function fetchReportSections(reportId: string): Promise<ReportSectionsResponse> {
  const response = await fetch(`${API_BASE}/report/${reportId}/sections`);
  return readJson<ReportSectionsResponse>(response);
}

// --- Divination Reports (Astrology) ---

async function fetchDivinationReports(chartId?: string): Promise<DivinationReport[]> {
  const url = chartId
    ? `${API_BASE}/divination/report/${chartId}`
    : `${API_BASE}/divination/report/list`;
  const response = await fetch(url);
  const data = await response.json();
  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch divination reports');
  }

  const payload = data.data as { reports?: DivinationReport[] } | DivinationReport[];
  if (Array.isArray(payload)) {
    return payload;
  }
  return payload.reports || [];
}

async function fetchDivinationReport(reportId: string): Promise<DivinationReport> {
  const response = await fetch(`${API_BASE}/divination/report/id/${reportId}`);
  const data = await response.json();
  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch divination report');
  }
  return (data.data.report || data.data) as DivinationReport;
}

async function fetchResolvedReport(reportId: string): Promise<ReportDetail> {
  try {
    const report = await fetchReport(reportId);
    return { kind: 'simulation', report };
  } catch (simulationError) {
    try {
      const report = await fetchDivinationReport(reportId);
      return { kind: 'divination', report };
    } catch {
      throw simulationError;
    }
  }
}

// --- Mutations ---

export function useGenerateDivinationReport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: { chart_id: string; year?: number; report_type?: string }) => {
      const response = await fetch(`${API_BASE}/divination/report/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const result = await response.json();
      if (!result.success) throw new Error(result.error || 'Failed to generate report');
      return result.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      queryClient.invalidateQueries({ queryKey: ['divination-reports'] });
    },
  });
}

export function useReport(reportId: string | null) {
  return useQuery({
    queryKey: ['report', reportId],
    queryFn: () => fetchReport(reportId!),
    enabled: !!reportId,
  });
}

export function useResolvedReport(reportId: string | null) {
  return useQuery({
    queryKey: ['resolved-report', reportId],
    queryFn: () => fetchResolvedReport(reportId!),
    enabled: !!reportId,
  });
}

export function useReportSections(reportId: string | null) {
  return useQuery({
    queryKey: ['report-sections', reportId],
    queryFn: () => fetchReportSections(reportId!),
    enabled: !!reportId,
  });
}

export function useDivinationReport(reportId: string | null) {
  return useQuery({
    queryKey: ['divination-report', reportId],
    queryFn: () => fetchDivinationReport(reportId!),
    enabled: !!reportId,
  });
}

export function useDivinationReports(chartId?: string) {
  return useQuery({
    queryKey: ['divination-reports', chartId || 'all'],
    queryFn: () => fetchDivinationReports(chartId),
  });
}

export function useReports() {
  return useQuery({
    queryKey: ['reports'],
    queryFn: fetchReports,
  });
}
