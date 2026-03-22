'use client';

import { use } from 'react';
import { GraphPage } from '@/components/graph';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Upload } from 'lucide-react';
import Link from 'next/link';

interface GraphRoutePageProps {
  params: Promise<{ id?: string }>;
}

export default function GraphRoutePage({ params }: GraphRoutePageProps) {
  const { id } = use(params);

  // If no graph ID provided, show empty state with instructions
  if (!id) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-100">知识图谱</h1>
            <p className="text-slate-400">实体关系网络可视化</p>
          </div>
        </div>

        <Card className="bg-slate-800/50 border-slate-700/50">
          <CardContent className="py-12">
            <div className="text-center">
              <FileText className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-200 mb-2">暂无图谱</h3>
              <p className="text-slate-400 text-sm mb-4 max-w-md mx-auto">
                请先上传文档生成本体和图谱，然后才能在知识图谱中查看。
              </p>
              <div className="flex justify-center gap-4">
                <Link
                  href="/"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900 font-medium rounded-lg transition-colors text-sm"
                >
                  <Upload className="h-4 w-4" />
                  上传文档
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">知识图谱</h1>
          <p className="text-slate-400">实体关系网络可视化 - {id}</p>
        </div>
      </div>

      <GraphPage graphId={id} className="h-[calc(100vh-200px)]" />
    </div>
  );
}
