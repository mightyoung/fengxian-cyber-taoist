'use client';

import Link from 'next/link';
import { useReports } from '@/hooks/use-report';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { FileText, ArrowLeft, Clock, ExternalLink } from 'lucide-react';

export default function ReportListPage() {
  const { data: reports, isLoading, error } = useReports();

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link href="/">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-100">报告列表</h1>
          <p className="text-slate-400">所有预测报告</p>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <Card className="bg-slate-800/50 border-slate-700/50">
          <CardContent className="py-8">
            <div className="text-center text-red-400">
              <p>加载失败: {error.message}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="bg-slate-800/50 border-slate-700/50">
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-1/2 mb-2" />
                <Skeleton className="h-4 w-1/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !error && (!reports || reports.length === 0) && (
        <Card className="bg-slate-800/50 border-slate-700/50">
          <CardContent className="py-12">
            <div className="text-center">
              <FileText className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-200 mb-2">暂无报告</h3>
              <p className="text-slate-400 text-sm mb-4">
                运行模拟后生成预测报告
              </p>
              <Link href="/simulation">
                <Button className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900">
                  前往模拟
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Report list */}
      {!isLoading && !error && reports && reports.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((report) => (
            <Link key={report.report_id} href={`/report/${report.report_id}`}>
              <Card className="bg-slate-800/50 border-slate-700/50 hover:border-[#D4AF37]/30 transition-all duration-200 cursor-pointer h-full">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-slate-100 text-lg flex items-center gap-2">
                      <FileText className="h-4 w-4 text-[#D4AF37]" />
                      {report.outline?.title || `报告 ${report.report_id.slice(0, 8)}`}
                    </CardTitle>
                    <ExternalLink className="h-4 w-4 text-slate-500" />
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-1 text-sm text-slate-400">
                    <Clock className="h-3 w-3" />
                    <span>{formatDate(report.created_at)}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <StatusBadge status={report.status} />
                  </div>

                  {report.simulation_id && (
                    <div className="pt-2 border-t border-slate-700">
                      <Link
                        href={`/simulation/${report.simulation_id}`}
                        className="text-sm text-[#D4AF37] hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        查看关联模拟 →
                      </Link>
                    </div>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status?: string }) {
  const statusConfig: Record<string, { label: string; className: string }> = {
    completed: { label: '已完成', className: 'bg-green-500/20 text-green-400 border-green-500/30' },
    generating: { label: '生成中', className: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
    failed: { label: '失败', className: 'bg-red-500/20 text-red-400 border-red-500/30' },
  };

  const config = statusConfig[status || ''] || statusConfig.generating;

  return (
    <span className={`px-2 py-0.5 rounded text-xs border ${config.className}`}>
      {config.label}
    </span>
  );
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr.slice(0, 10);
  }
}
