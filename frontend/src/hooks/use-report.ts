/**
 * Report API Hook
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import type { Report, ReportMetrics, ReportSection } from '@/types/report';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

async function fetchReport(reportId: string): Promise<Report> {
  const response = await fetch(`${API_BASE}/report/${reportId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch report');
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch report');
  }

  return data.data;
}

async function fetchReportSections(reportId: string): Promise<{
  sections: ReportSection[];
  total_sections: number;
  is_complete: boolean;
}> {
  const response = await fetch(`${API_BASE}/report/${reportId}/sections`);

  if (!response.ok) {
    throw new Error('Failed to fetch report sections');
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch report sections');
  }

  return data.data;
}

async function fetchReportMetrics(reportId: string): Promise<ReportMetrics> {
  const response = await fetch(`${API_BASE}/report/${reportId}/metrics`);

  if (!response.ok) {
    throw new Error('Failed to fetch report metrics');
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch report metrics');
  }

  return data.data;
}

async function generateReport(simulationId: string): Promise<{ task_id: string }> {
  const response = await fetch(`${API_BASE}/report/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ simulation_id: simulationId }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate report');
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Failed to generate report');
  }

  return data.data;
}

export function useReport(reportId: string | null) {
  return useQuery({
    queryKey: ['report', reportId],
    queryFn: () => fetchReport(reportId!),
    enabled: !!reportId,
  });
}

export function useReportSections(reportId: string | null) {
  return useQuery({
    queryKey: ['report', reportId, 'sections'],
    queryFn: () => fetchReportSections(reportId!),
    enabled: !!reportId,
    refetchInterval: (query) => {
      // Keep polling until report is complete
      const data = query.state.data as { is_complete?: boolean } | undefined;
      if (!data?.is_complete) {
        return 3000;
      }
      return false;
    },
  });
}

export function useReportMetrics(reportId: string | null) {
  return useQuery({
    queryKey: ['report', reportId, 'metrics'],
    queryFn: () => fetchReportMetrics(reportId!),
    enabled: !!reportId,
  });
}

export function useGenerateReport() {
  return useMutation({
    mutationFn: generateReport,
  });
}
