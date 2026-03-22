'use client';

import { use, useState } from 'react';
import { ReportViewerMemoized } from '@/components/report/report-viewer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface ReportRoutePageProps {
  params: Promise<{ id?: string }>;
}

export default function ReportRoutePage({ params }: ReportRoutePageProps) {
  const { id } = use(params);
  const [reportId, setReportId] = useState<string | null>(id || null);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-100">预测报告</h1>
          <p className="text-slate-400">AI 生成的预测分析报告</p>
        </div>
      </div>

      {reportId ? (
        <ReportViewerMemoized reportId={reportId} className="min-h-[600px]" />
      ) : (
        <Card className="bg-slate-800/50 border-slate-700/50">
          <CardContent className="py-12">
            <div className="text-center">
              <FileText className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-200 mb-2">暂无报告</h3>
              <p className="text-slate-400 text-sm mb-4">
                请先运行模拟生成预测报告
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
    </div>
  );
}
