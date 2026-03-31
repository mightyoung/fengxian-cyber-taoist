'use client';

import Link from 'next/link';
import { useSimulations } from '@/hooks/use-simulation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Sparkles, ArrowLeft, Clock, Users } from 'lucide-react';

export default function SimulationListPage() {
  const { data: simulations, isLoading, error } = useSimulations();

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
          <h1 className="text-2xl font-bold text-slate-100">模拟列表</h1>
          <p className="text-slate-400">所有模拟任务</p>
        </div>
        <Link href="/graph">
          <Button className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900">
            <Sparkles className="h-4 w-4 mr-2" />
            新建模拟
          </Button>
        </Link>
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
      {!isLoading && !error && (!simulations || simulations.length === 0) && (
        <Card className="bg-slate-800/50 border-slate-700/50">
          <CardContent className="py-12">
            <div className="text-center">
              <Sparkles className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-200 mb-2">暂无模拟</h3>
              <p className="text-slate-400 text-sm mb-4">
                从知识图谱开始，创建您的第一个模拟任务
              </p>
              <Link href="/graph">
                <Button className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900">
                  前往知识图谱
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Simulation list */}
      {!isLoading && !error && simulations && simulations.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {simulations.map((sim) => (
            <Link key={sim.id || sim.simulation_id} href={`/simulation/${sim.id || sim.simulation_id}`}>
              <Card className="bg-slate-800/50 border-slate-700/50 hover:border-[#D4AF37]/30 transition-all duration-200 cursor-pointer h-full">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-slate-100 text-lg">
                      {sim.name || `Simulation ${(sim.id || sim.simulation_id || '').slice(0, 8)}`}
                    </CardTitle>
                    <StatusBadge status={sim.status} />
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-4 text-sm text-slate-400">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{formatDate(sim.created_at)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      <span>{sim.agentCount || sim.profiles_count || 0} 智能体</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <PlatformBadge
                      enableTwitter={sim.enable_twitter}
                      enableReddit={sim.enable_reddit}
                    />
                  </div>

                  {sim.status === 'running' && (
                    <div className="pt-2">
                      <div className="flex items-center gap-2 text-sm">
                        <div className="flex-1 bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-[#D4AF37] h-2 rounded-full transition-all"
                            style={{ width: `${sim.progress || 0}%` }}
                          />
                        </div>
                        <span className="text-slate-400 text-xs">{sim.progress || 0}%</span>
                      </div>
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

function StatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { label: string; className: string }> = {
    running: { label: '运行中', className: 'bg-green-500/20 text-green-400 border-green-500/30' },
    completed: { label: '已完成', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
    failed: { label: '失败', className: 'bg-red-500/20 text-red-400 border-red-500/30' },
    paused: { label: '已暂停', className: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
    created: { label: '待启动', className: 'bg-slate-500/20 text-slate-400 border-slate-500/30' },
    preparing: { label: '准备中', className: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
    ready: { label: '就绪', className: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
  };

  const config = statusConfig[status] || statusConfig.created;

  return (
    <span className={`px-2 py-0.5 rounded text-xs border ${config.className}`}>
      {config.label}
    </span>
  );
}

function PlatformBadge({ enableTwitter, enableReddit }: { enableTwitter?: boolean; enableReddit?: boolean }) {
  return (
    <div className="flex gap-1">
      {enableTwitter && (
        <span className="px-2 py-0.5 rounded text-xs bg-sky-500/20 text-sky-400 border border-sky-500/30">
          Twitter
        </span>
      )}
      {enableReddit && (
        <span className="px-2 py-0.5 rounded text-xs bg-orange-500/20 text-orange-400 border border-orange-500/30">
          Reddit
        </span>
      )}
    </div>
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
