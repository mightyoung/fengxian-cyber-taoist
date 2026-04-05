'use client';

import { memo } from 'react';
import type { ReactNode } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useReportSections, useResolvedReport } from '@/hooks/use-report';
import { cn } from '@/lib/utils';
import { ANIMATIONS } from '@/lib/animation';
import { ReportMetrics } from './index';
import { ReportExport } from './index';

interface ReportViewerProps {
  reportId: string | null;
  className?: string;
}

const markdownComponents = {
  h1: ({ children }: { children: ReactNode }) => (
    <h1 className="text-2xl font-heading font-semibold text-slate-100 mt-6 mb-4">
      {children}
    </h1>
  ),
  h2: ({ children }: { children: ReactNode }) => (
    <h2 className="text-xl font-heading font-semibold text-slate-200 mt-6 mb-3">
      {children}
    </h2>
  ),
  h3: ({ children }: { children: ReactNode }) => (
    <h3 className="text-lg font-heading font-medium text-slate-200 mt-4 mb-2">
      {children}
    </h3>
  ),
  p: ({ children }: { children: ReactNode }) => (
    <p className="text-slate-300 leading-relaxed mb-4">
      {children}
    </p>
  ),
  ul: ({ children }: { children: ReactNode }) => (
    <ul className="list-disc list-inside text-slate-300 mb-4 space-y-1">
      {children}
    </ul>
  ),
  ol: ({ children }: { children: ReactNode }) => (
    <ol className="list-decimal list-inside text-slate-300 mb-4 space-y-1">
      {children}
    </ol>
  ),
  li: ({ children }: { children: ReactNode }) => (
    <li className="text-slate-300">{children}</li>
  ),
  code: ({ children, className }: { children: ReactNode; className?: string }) => (
    <code className={cn('bg-slate-900 px-2 py-1 rounded text-sm', className)}>
      {children}
    </code>
  ),
  pre: ({ children }: { children: ReactNode }) => (
    <pre className="bg-slate-900 p-4 rounded-lg overflow-x-auto mb-4">
      {children}
    </pre>
  ),
  a: ({ href, children }: { href?: string; children: ReactNode }) => {
    const isSafe = href && (
      href.startsWith('http://') ||
      href.startsWith('https://') ||
      href.startsWith('/') ||
      href.startsWith('#')
    );
    if (!isSafe) return <span className="text-red-400">[链接]</span>;
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-400 hover:underline"
      >
        {children}
      </a>
    );
  },
};

function MarkdownBlock({ content }: { content: string }) {
  return (
    <div className="prose prose-invert prose-slate max-w-none">
      <ReactMarkdown components={markdownComponents}>
        {content}
      </ReactMarkdown>
    </div>
  );
}

function ReportViewer({ reportId, className }: ReportViewerProps) {
  const { data: resolved, isLoading: isReportLoading, error } = useResolvedReport(reportId);
  const isSimulationReport = resolved?.kind === 'simulation';
  const { data: sectionsData, isLoading: isSectionsLoading } = useReportSections(
    isSimulationReport ? reportId : null
  );

  const isLoading = isReportLoading || (isSimulationReport && isSectionsLoading);

  if (isLoading) {
    return (
      <div className={cn('w-full h-full flex flex-col gap-4 p-6', className)}>
        <Skeleton className="h-8 w-1/3 bg-slate-800" />
        <Skeleton className="h-4 w-full bg-slate-800" />
        <Skeleton className="h-4 w-2/3 bg-slate-800" />
        <Skeleton className="h-64 w-full bg-slate-800" />
      </div>
    );
  }

  if (error || !resolved) {
    return (
      <div className={cn('w-full h-full flex items-center justify-center', className)}>
        <div className="text-center p-6 bg-red-950/30 border border-red-900 rounded-lg">
          <p className="text-red-400">Failed to load report</p>
          <p className="text-slate-400 text-sm mt-2">
            {error?.message || 'Report not found'}
          </p>
        </div>
      </div>
    );
  }

  if (resolved.kind === 'divination') {
    const report = resolved.report;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: ANIMATIONS.standard.duration / 1000 }}
        className={cn('w-full h-full flex flex-col gap-6 p-6 overflow-auto', className)}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-heading font-semibold text-slate-100">
                {report.title || 'Divination Report'}
              </h1>
              <span className="text-xs px-2 py-0.5 rounded bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/20">
                命理报告
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {report.format}
              </span>
            </div>
            <p className="text-slate-400 text-sm">
              {report.chart_id ? `命盘ID: ${report.chart_id}` : `报告ID: ${report.report_id}`}
            </p>
          </div>

          <div className="text-right text-xs text-slate-500">
            <div>{report.status}</div>
            <div>{report.created_at ? `Generated: ${new Date(report.created_at).toLocaleString('zh-CN')}` : ''}</div>
          </div>
        </div>

        {report.metadata && Object.keys(report.metadata).length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {Object.entries(report.metadata).slice(0, 6).map(([key, value]) => (
              <div key={key} className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
                <div className="text-xs uppercase tracking-wider text-slate-500 mb-1">{key}</div>
                <div className="text-sm text-slate-200 break-words">
                  {typeof value === 'string' ? value : JSON.stringify(value)}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-6">
          <MarkdownBlock content={report.markdown_content || 'No content available'} />
        </div>
      </motion.div>
    );
  }

  const report = resolved.report;
  const metricsReportId = reportId && resolved.kind === 'simulation' ? reportId : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: ANIMATIONS.standard.duration / 1000 }}
      className={cn('w-full h-full flex flex-col gap-6 p-6 overflow-auto', className)}
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-heading font-semibold text-slate-100">
            Prediction Report
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Simulation ID: {report.simulation_id}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs text-slate-500">
            {report.completed_at
              ? `Generated: ${new Date(report.completed_at).toLocaleDateString()}`
              : ''}
          </span>
          {metricsReportId && report.status === 'completed' && (
            <ReportExport reportId={metricsReportId} />
          )}
        </div>
      </div>

      {/* Metrics Section */}
      {metricsReportId && <ReportMetrics reportId={metricsReportId} />}

      {/* Content Tabs */}
      <Tabs defaultValue="content" className="flex-1 flex flex-col min-h-0">
        <TabsList className="bg-slate-900 border-slate-800">
          <TabsTrigger value="content" className="data-[state=active]:bg-slate-800">
            Content
          </TabsTrigger>
          <TabsTrigger value="sections" className="data-[state=active]:bg-slate-800">
            Sections
          </TabsTrigger>
        </TabsList>

        <TabsContent value="content" className="flex-1 mt-4 min-h-0 overflow-auto">
          <MarkdownBlock content={report.markdown_content || 'No content available'} />
        </TabsContent>

        <TabsContent value="sections" className="flex-1 mt-4 min-h-0 overflow-auto">
          <div className="space-y-4">
            {sectionsData?.sections.map((section, index) => (
              <div
                key={index}
                className="bg-slate-900/50 border border-slate-800 rounded-lg p-4"
              >
                <h3 className="text-lg font-medium text-slate-200 mb-2">
                  {section.title || `Section ${index + 1}`}
                </h3>
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      a: markdownComponents.a,
                    }}
                  >
                    {section.content}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}

export const ReportViewerMemoized = memo(ReportViewer);
ReportViewerMemoized.displayName = 'ReportViewer';
