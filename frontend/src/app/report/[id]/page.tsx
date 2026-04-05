'use client';

import { use } from 'react';
import Link from 'next/link';
import { ReportViewerMemoized } from '@/components/report/report-viewer';
import { Button } from '@/components/ui/button';
import { ArrowLeft, MessageCircle } from 'lucide-react';

interface ReportDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function ReportDetailPage({ params }: ReportDetailPageProps) {
  const { id } = use(params);

  return (
    <div className="relative space-y-6 pb-24">
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

      {/* Floating Consultation Trigger */}
      <div className="fixed bottom-8 right-8 z-50">
        <Link href={`/chat?report_id=${id}`}>
          <Button className="h-14 w-14 rounded-full bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900 shadow-2xl animate-pulse-gold group">
            <MessageCircle className="h-6 w-6 group-hover:scale-110 transition-transform" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
