'use client';

import { useBirthChartStore } from '@/stores/birthChartStore';
import { EducationAnalysis } from '@/components/divination';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle } from 'lucide-react';
import Link from 'next/link';

export default function EducationPage() {
  const { currentChart } = useBirthChartStore();

  if (!currentChart) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="border-amber-500/20 bg-gradient-to-br from-amber-950/30 to-slate-900/50 max-w-md mx-auto">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-400">
              <AlertTriangle className="h-5 w-5" />
              需要命盘数据
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-slate-400">
              请先生成命盘，然后才能进行学业分析。
            </p>
            <Link
              href="/birth-chart"
              className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition-colors"
            >
              生成命盘
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Convert chart data to the format expected by the API
  const chartData = {
    palaces: currentChart.palaces.reduce((acc, palace) => {
      acc[palace.name] = {
        stars: palace.stars,
        tiangan: palace.tiangan,
        transforms: palace.transforms,
      };
      return acc;
    }, {} as Record<string, unknown>),
    birth_info: {
      year: currentChart.input?.year || 1990,
      month: currentChart.input?.month || 1,
      day: currentChart.input?.day || 1,
      hour: currentChart.input?.hour || 0,
    },
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-6">
        <h1 className="text-2xl font-heading text-accent mb-2">学业分析</h1>
        <p className="text-slate-400 text-sm">
          基于命盘信息分析学习能力、学历层次及学业运势
        </p>
      </div>

      <EducationAnalysis chartData={chartData} />
    </div>
  );
}
