'use client';

import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useReport, useReportSections } from '@/hooks/use-report';
import { cn } from '@/lib/utils';
import { ANIMATIONS } from '@/lib/animation';
import { ReportMetrics } from './index';
import { ReportExport } from './index';

interface ReportViewerProps {
  reportId: string | null;
  className?: string;
}

function ReportViewer({ reportId, className }: ReportViewerProps) {
  const { data: report, isLoading: isReportLoading, error } = useReport(reportId);
  const { data: sectionsData, isLoading: isSectionsLoading } = useReportSections(reportId);

  const isLoading = isReportLoading || isSectionsLoading;

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

  if (error || !report) {
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

  const isGenerating = report.status === 'generating';

  if (isGenerating) {
    return (
      <div className={cn('w-full h-full flex items-center justify-center', className)}>
        <div className="text-center p-6 bg-slate-900/50 border border-slate-800 rounded-lg">
          <div className="w-12 h-12 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-300">Generating report...</p>
          <p className="text-slate-500 text-sm mt-2">
            This may take a few minutes
          </p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: ANIMATIONS.standard.duration / 1000 }}
      className={cn('w-full h-full flex flex-col gap-6 p-6 overflow-auto', className)}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
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
          {reportId && report.status === 'completed' && (
            <ReportExport reportId={reportId} />
          )}
        </div>
      </div>

      {/* Metrics Section */}
      {reportId && <ReportMetrics reportId={reportId} />}

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
          <div className="prose prose-invert prose-slate max-w-none">
            <ReactMarkdown
              components={{
                h1: ({ children }) => (
                  <h1 className="text-2xl font-heading font-semibold text-slate-100 mt-6 mb-4">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-xl font-heading font-semibold text-slate-200 mt-6 mb-3">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-lg font-heading font-medium text-slate-200 mt-4 mb-2">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="text-slate-300 leading-relaxed mb-4">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-inside text-slate-300 mb-4 space-y-1">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside text-slate-300 mb-4 space-y-1">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="text-slate-300">{children}</li>
                ),
                code: ({ children, className }) => (
                  <code className={cn('bg-slate-900 px-2 py-1 rounded text-sm', className)}>
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-slate-900 p-4 rounded-lg overflow-x-auto mb-4">
                    {children}
                  </pre>
                ),
                a: ({ href, children }) => {
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
              }}
            >
              {report.markdown_content || 'No content available'}
            </ReactMarkdown>
          </div>
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
                      a: ({ href, children }) => {
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
