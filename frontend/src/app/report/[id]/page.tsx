'use client';

import { use } from 'react';
import Link from 'next/link';
import { ReportViewerMemoized } from '@/components/report/report-viewer';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

interface ReportDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function ReportDetailPage({ params }: ReportDetailPageProps) {
  const { id } = use(params);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/report">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-100">报告详情</h1>
          <p className="text-slate-400 text-sm">ID: {id}</p>
        </div>
      </div>

      <ReportViewerMemoized reportId={id} className="min-h-[600px]" />
    </div>
  );
}
