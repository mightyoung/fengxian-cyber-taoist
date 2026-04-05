'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, ArrowRight, Clock, FileText, Heart, LayoutGrid, Sparkles, Users } from 'lucide-react';
import { toast } from 'sonner';
import { useBirthChartStore } from '@/stores/birthChartStore';
import { divinationApi } from '@/hooks/use-api';
import { useReports, useDivinationReports } from '@/hooks/use-report';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { BirthChart, Palace, Star, Transform } from '@/types/birth-chart';
import type { BirthChartInput, DivinationChartSummary } from '@/types/api';

type ChartCardModel = {
  chart_id: string;
  birth_info: BirthChartInput;
  status: string;
  created_at: string;
  updated_at: string;
  report_count: number;
  source: 'backend' | 'local';
};

export default function InsightsPage() {
  const router = useRouter();
  const { currentChart, history, setChart } = useBirthChartStore();
  const [activatingChartId, setActivatingChartId] = useState<string | null>(null);

  const { data: backendCharts, isLoading: chartsLoading, error: chartsError } = useQuery({
    queryKey: ['divination-charts'],
    queryFn: async () => {
      const res = await divinationApi.listCharts();
      if (res.error) {
        throw new Error(res.error);
      }
      return (res.data || []) as DivinationChartSummary[];
    },
  });

  const { data: simulationReports, isLoading: simulationLoading, error: simulationError } = useReports();
  const { data: divinationReports, isLoading: divinationLoading, error: divinationError } = useDivinationReports();

  const backendChartCards = useMemo<ChartCardModel[]>(() => {
    return (backendCharts || []).map((chart) => ({
      chart_id: chart.chart_id,
      birth_info: chart.birth_info,
      status: chart.status,
      created_at: chart.created_at,
      updated_at: chart.updated_at,
      report_count: chart.report_count,
      source: 'backend',
    }));
  }, [backendCharts]);

  const localChartCards = useMemo<ChartCardModel[]>(() => {
    return history.map((chart) => ({
      chart_id: chart.id,
      birth_info: chart.input,
      status: chart.analysis ? 'analyzed' : 'generated',
      created_at: chart.createdAt,
      updated_at: chart.createdAt,
      report_count: 0,
      source: 'local',
    }));
  }, [history]);

  const latestCharts = useMemo(() => {
    const merged = new Map<string, ChartCardModel>();
    for (const chart of [...localChartCards, ...backendChartCards]) {
      merged.set(chart.chart_id, chart);
    }
    return [...merged.values()].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()).slice(0, 6);
  }, [backendChartCards, localChartCards]);

  const reportCounts = {
    simulation: simulationReports?.length || 0,
    divination: divinationReports?.length || 0,
  };

  const totalSavedCharts = backendChartCards.length || history.length;

  const handleActivateChart = async (chartId: string) => {
    try {
      setActivatingChartId(chartId);
      const res = await divinationApi.getChart(chartId);
      if (res.error) {
        throw new Error(res.error);
      }

      const data = res.data as {
        chart_id: string;
        chart: Record<string, unknown>;
        birth_info: BirthChartInput;
      };

      const fullChart = convertToBirthChart(data);
      setChart(fullChart);
      toast.success('已恢复到当前命盘');
      router.push('/birth-chart');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '恢复命盘失败');
    } finally {
      setActivatingChartId(null);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="flex items-center gap-4">
        <Link href="/">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-100">内容中心</h1>
          <p className="text-slate-400">
            聚合命盘、模拟和命理报告，支持继续上次分析、回看和对比
          </p>
        </div>
        <div className="hidden md:flex items-center gap-2">
          <Link href="/birth-chart">
            <Button className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900">
              <Sparkles className="h-4 w-4 mr-2" />
              新建命盘
            </Button>
          </Link>
          <Link href="/simulation">
            <Button variant="outline" className="border-slate-700 text-slate-200">
              查看模拟
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard icon={LayoutGrid} title="保存命盘" value={totalSavedCharts} hint="后端可列举资产" />
        <StatCard icon={FileText} title="模拟报告" value={reportCounts.simulation} hint="OASIS 预测报告" />
        <StatCard icon={Heart} title="命理报告" value={reportCounts.divination} hint="紫微斗数分析" />
        <StatCard icon={Users} title="当前命盘" value={currentChart ? '1' : '0'} hint={currentChart ? '已选中当前分析' : '未加载命盘'} />
      </div>

      <Card className="bg-slate-800/50 border-slate-700/50">
        <CardHeader>
          <CardTitle className="text-slate-100">继续上次分析</CardTitle>
        </CardHeader>
        <CardContent>
          {currentChart ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2 space-y-3">
                <div className="text-sm text-slate-400">
                  当前命盘
                </div>
                <div className="text-lg font-semibold text-slate-100">
                  {formatBirthInput(currentChart.input)}
                </div>
                <div className="text-sm text-slate-400">
                  {currentChart.palaces.length} 个宫位已加载，可直接继续姻缘、年度报告或模拟推演。
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <Link href="/birth-chart">
                  <Button className="w-full bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900">
                    打开命盘
                  </Button>
                </Link>
                <Link href="/divination/relationship">
                  <Button variant="outline" className="w-full border-slate-700 text-slate-200">
                    姻缘分析
                  </Button>
                </Link>
                <Link href="/report">
                  <Button variant="outline" className="w-full border-slate-700 text-slate-200">
                    模拟报告
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-slate-700 p-6 text-center">
              <p className="text-slate-300 mb-2">还没有当前命盘</p>
              <p className="text-sm text-slate-500 mb-4">
                先生成一张命盘，系统才有可恢复的分析上下文。
              </p>
              <Link href="/birth-chart">
                <Button className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900">
                  立即起卦
                </Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="charts" className="space-y-4">
        <TabsList className="bg-slate-800">
          <TabsTrigger value="charts" className="data-[state=active]:bg-slate-700">
            最近命盘
          </TabsTrigger>
          <TabsTrigger value="simulation" className="data-[state=active]:bg-slate-700">
            模拟报告
          </TabsTrigger>
          <TabsTrigger value="divination" className="data-[state=active]:bg-slate-700">
            命理报告
          </TabsTrigger>
        </TabsList>

        <TabsContent value="charts">
          {chartsLoading ? (
            <LoadingGrid />
          ) : chartsError ? (
            <ErrorCard message={chartsError.message} />
          ) : latestCharts.length === 0 ? (
            <EmptyState
              title="暂无命盘历史"
              description="生成命盘后，这里会保留最近的分析记录，方便你回看和继续分析。"
              actionHref="/birth-chart"
              actionLabel="去生成命盘"
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {latestCharts.map((chart) => (
                <ChartCard
                  key={chart.chart_id}
                  chart={chart}
                  activating={activatingChartId === chart.chart_id}
                  onUse={() => handleActivateChart(chart.chart_id)}
                  isActive={currentChart?.id === chart.chart_id}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="simulation">
          {simulationLoading ? (
            <LoadingGrid />
          ) : simulationError ? (
            <ErrorCard message={simulationError.message} />
          ) : !simulationReports || simulationReports.length === 0 ? (
            <EmptyState
              title="暂无模拟报告"
              description="完成一次模拟后，会在这里聚合成统一入口。"
              actionHref="/simulation"
              actionLabel="前往模拟"
            />
          ) : (
            <ReportGrid
              items={simulationReports.slice().reverse()}
              renderMeta={(report) => [
                report.simulation_id,
                report.status,
                report.created_at,
              ]}
              renderTitle={(report) => report.outline?.title || `报告 ${report.report_id.slice(0, 8)}`}
              hrefBuilder={(report) => `/report/${report.report_id}`}
            />
          )}
        </TabsContent>

        <TabsContent value="divination">
          {divinationLoading ? (
            <LoadingGrid />
          ) : divinationError ? (
            <ErrorCard message={divinationError.message} />
          ) : !divinationReports || divinationReports.length === 0 ? (
            <EmptyState
              title="暂无命理报告"
              description="命盘分析完成后，所有命理报告都会在这里统一收纳。"
              actionHref="/birth-chart"
              actionLabel="去生成命盘"
            />
          ) : (
            <ReportGrid
              items={divinationReports.slice().reverse()}
              renderMeta={(report) => [
                report.user_name || '命主',
                String(report.target_year),
                report.report_type,
              ]}
              renderTitle={(report) => report.title || `命理报告 ${report.report_id.slice(0, 8)}`}
              hrefBuilder={(report) => `/report/${report.report_id}`}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

function ChartCard({
  chart,
  onUse,
  activating,
  isActive,
}: {
  chart: ChartCardModel;
  onUse: () => void;
  activating: boolean;
  isActive: boolean;
}) {
  return (
    <Card className={`bg-slate-800/50 border-slate-700/50 ${isActive ? 'border-[#D4AF37]/40' : ''}`}>
      <CardHeader>
        <div className="flex items-center justify-between gap-3">
          <CardTitle className="text-slate-100 text-lg">
            {formatBirthInput(chart.birth_info)}
          </CardTitle>
          {isActive && (
            <span className="text-xs px-2 py-0.5 rounded bg-[#D4AF37]/20 text-[#D4AF37]">
              当前
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-slate-400 space-y-1">
          <div>命盘ID: {chart.chart_id.slice(0, 8)}</div>
          <div>宫位: {chart.source === 'backend' ? '后端持久化' : '本地会话'}</div>
          <div>关联报告: {chart.report_count}</div>
          <div>保存时间: {formatDate(chart.created_at)}</div>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={onUse}
            disabled={activating}
            className="flex-1 bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900"
          >
            {activating ? '恢复中...' : '设为当前'}
          </Button>
          <Link href="/birth-chart">
            <Button variant="outline" className="border-slate-700 text-slate-200">
              打开
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}

function StatCard({
  icon: Icon,
  title,
  value,
  hint,
}: {
  icon: ComponentType<{ className?: string }>;
  title: string;
  value: string | number;
  hint: string;
}) {
  return (
    <Card className="bg-slate-800/50 border-slate-700/50">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm text-slate-400">{title}</p>
            <p className="text-2xl font-bold text-slate-100 mt-1">{value}</p>
            <p className="text-xs text-slate-500 mt-2">{hint}</p>
          </div>
          <div className="rounded-lg bg-[#D4AF37]/10 p-2">
            <Icon className="h-5 w-5 text-[#D4AF37]" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ReportGrid<T extends { created_at?: string; report_id: string }>({
  items,
  renderMeta,
  renderTitle,
  hrefBuilder,
}: {
  items: T[];
  renderMeta: (item: T) => string[];
  renderTitle: (item: T) => string;
  hrefBuilder: (item: T) => string;
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {items.map((item) => (
        <Link key={item.report_id} href={hrefBuilder(item)}>
          <Card className="bg-slate-800/50 border-slate-700/50 hover:border-[#D4AF37]/30 transition-all duration-200 h-full">
            <CardHeader>
              <CardTitle className="text-slate-100 text-lg flex items-center gap-2">
                <FileText className="h-4 w-4 text-[#D4AF37]" />
                {renderTitle(item)}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-1 text-sm text-slate-400">
                <Clock className="h-3 w-3" />
                <span>{formatDate(item.created_at)}</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {renderMeta(item).map((meta) => (
                  <span key={meta} className="px-2 py-0.5 rounded text-xs bg-slate-700/60 text-slate-300">
                    {meta}
                  </span>
                ))}
              </div>
              <div className="flex items-center justify-end text-sm text-[#D4AF37]">
                查看详情 <ArrowRight className="h-4 w-4 ml-1" />
              </div>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}

function EmptyState({
  title,
  description,
  actionHref,
  actionLabel,
}: {
  title: string;
  description: string;
  actionHref: string;
  actionLabel: string;
}) {
  return (
    <Card className="bg-slate-800/50 border-slate-700/50">
      <CardContent className="py-12">
        <div className="text-center">
          <Sparkles className="h-12 w-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-200 mb-2">{title}</h3>
          <p className="text-slate-400 text-sm mb-4">{description}</p>
          <Link href={actionHref}>
            <Button className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900">
              {actionLabel}
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}

function ErrorCard({ message }: { message: string }) {
  return (
    <Card className="bg-slate-800/50 border-slate-700/50">
      <CardContent className="py-8">
        <div className="text-center text-red-400">
          <p>加载失败: {message}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function LoadingGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
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
  );
}

function convertToBirthChart(data: {
  chart_id: string;
  chart: Record<string, unknown>;
  birth_info: BirthChartInput;
}): BirthChart {
  const palaces = Object.entries((data.chart?.palaces as Record<string, unknown>) || {}).map(([name, palace], index) => {
    const p = palace as {
      id?: string;
      branch?: string;
      tiangan?: string;
      stars?: Array<{ name: string; wuxing: string; level: string }>;
      transforms?: Array<{ type: string; star: string; wuxing: string }>;
    };

    return {
      id: p.id || String(index + 1),
      name,
      branch: p.branch || '',
      tiangan: p.tiangan || '',
      stars: (p.stars || []).map((star) => ({
        name: star.name,
        wuxing: star.wuxing as Star['wuxing'],
        level: star.level as Star['level'],
      })) as Star[],
      transforms: (p.transforms || []).map((transform) => ({
        type: transform.type as Transform['type'],
        star: transform.star,
        wuxing: transform.wuxing as Transform['wuxing'],
      })) as Transform[],
    } satisfies Palace;
  });

  return {
    id: data.chart_id,
    input: data.birth_info,
    palaces,
    createdAt: new Date().toISOString(),
  };
}

function formatBirthInput(input: BirthChartInput): string {
  const { year, month, day, hour, gender } = input;
  return `${year ?? '-'}年${month ?? '-'}月${day ?? '-'}日 ${String(hour ?? 0).padStart(2, '0')}时 · ${gender === 'male' ? '男' : '女'}`;
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
