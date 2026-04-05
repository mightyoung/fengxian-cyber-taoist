'use client';

import { useState, use } from 'react';
import Link from 'next/link';
import {
  useStartSimulation,
  useStopSimulation,
  useSimulationStatus,
  useSimulationAgents,
  useSimulationRunStatusDetail,
  transformActionsToTimelineEvents,
} from '@/hooks/use-simulation';
import { SimulationStatusBar } from '@/components/simulation/simulation-status-bar';
import { SimulationControls } from '@/components/simulation/simulation-controls';
import { AgentGrid } from '@/components/simulation/agent-grid';
import { SimulationTimeline } from '@/components/simulation/simulation-timeline';
import { SimulationStatus } from '@/types/simulation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Sparkles, ArrowLeft, GitFork } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import { simulationApi } from '@/hooks/use-api';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';

interface SimulationDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function SimulationDetailPage({ params }: SimulationDetailPageProps) {
  const { id } = use(params);
  const router = useRouter();
  const [selectedAgentId, setSelectedAgentId] = useState<string | undefined>();

  const { simulation, isRunning } = useSimulationStatus(id);
  const { data: agents, isLoading: agentsLoading } = useSimulationAgents(id);
  const { data: runStatusDetail } = useSimulationRunStatusDetail(id);
  const startMutation = useStartSimulation();
  const stopMutation = useStopSimulation();

  const forkMutation = useMutation({
    mutationFn: () => simulationApi.forkSimulation({ parent_id: id }),
    onSuccess: (res) => {
      if (res.success) {
        toast.success('已成功开启因果分支模拟');
        router.push(`/simulation/${res.data.simulation_id}`);
      }
    }
  });

  const handleFork = () => {
    forkMutation.mutate();
  };

  // Transform run status actions to timeline events
  const timelineEvents = runStatusDetail?.all_actions
    ? transformActionsToTimelineEvents(runStatusDetail.all_actions)
    : [];

  const currentStatus = (simulation?.status as SimulationStatus) || SimulationStatus.PENDING;
  const progress = simulation?.progress || 0;
  const currentRound = (simulation?.current_round as number) || 1;
  const totalRounds = ((simulation?.profiles_count as number) ?? 0) * 10 || 10;

  const handleStart = () => {
    if (id) {
      startMutation.mutate(id);
    }
  };

  const handleStop = () => {
    if (id) {
      stopMutation.mutate(id);
    }
  };

  // No simulation data available for this ID
  if (!simulation && !agentsLoading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/simulation">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">模拟详情</h1>
            <p className="text-slate-400">实时监控AI智能体社交媒体模拟</p>
          </div>
        </div>

        <Card className="bg-slate-800/50 border-slate-700/50">
          <CardContent className="py-12">
            <div className="text-center">
              <Sparkles className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-200 mb-2">模拟不存在</h3>
              <p className="text-slate-400 text-sm mb-4">
                未找到 ID 为 {id} 的模拟任务
              </p>
              <Link href="/simulation">
                <Button className="bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-slate-900">
                  返回模拟列表
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-4">
        <Link href="/simulation">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-100">模拟详情</h1>
          <p className="text-slate-400 text-sm">ID: {id}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            className="border-accent/20 hover:bg-accent/10 text-accent gap-2"
            onClick={handleFork}
            disabled={forkMutation.isPending}
          >
            <GitFork className="h-4 w-4" />
            开启分支推演
          </Button>
          <SimulationControls
            status={currentStatus}
            onStart={handleStart}
            onPause={() => {}}
            onStop={handleStop}
            isLoading={startMutation.isPending || stopMutation.isPending}
          />
        </div>
      </div>

      {/* Status Bar */}
      <Card className="bg-slate-800/50 border-slate-700/50">
        <CardContent className="pt-6">
          <SimulationStatusBar
            progress={progress}
            status={currentStatus}
            currentRound={currentRound}
            totalRounds={totalRounds}
          />
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="agents" className="space-y-4">
        <TabsList className="bg-slate-800">
          <TabsTrigger value="agents" className="data-[state=active]:bg-slate-700">
            智能体
          </TabsTrigger>
          <TabsTrigger value="timeline" className="data-[state=active]:bg-slate-700">
            时间线
          </TabsTrigger>
          <TabsTrigger value="details" className="data-[state=active]:bg-slate-700">
            详情
          </TabsTrigger>
        </TabsList>

        <TabsContent value="agents">
          {agentsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <Card key={i} className="bg-slate-800/50 border-slate-700/50">
                  <CardHeader>
                    <Skeleton className="h-10 w-10 rounded-full" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-20 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : agents && agents.length > 0 ? (
            <AgentGrid
              agents={agents}
              selectedAgentId={selectedAgentId}
              onSelectAgent={(agent) => setSelectedAgentId(agent.id)}
            />
          ) : (
            <Card className="bg-slate-800/50 border-slate-700/50">
              <CardContent className="py-8">
                <div className="text-center text-slate-400">
                  <p>暂无智能体数据</p>
                  <p className="text-sm mt-1">请等待模拟准备完成</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="timeline">
          <Card className="bg-slate-800/50 border-slate-700/50">
            <CardHeader>
              <CardTitle className="text-slate-100">事件时间线</CardTitle>
            </CardHeader>
            <CardContent>
              <SimulationTimeline
                events={timelineEvents}
                isRunning={isRunning}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="details">
          <Card className="bg-slate-800/50 border-slate-700/50">
            <CardHeader>
              <CardTitle className="text-slate-100">模拟详情</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-slate-400">模拟ID</div>
                  <div className="text-slate-100 font-mono">{id}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-400">平台</div>
                  <div className="text-slate-100">
                    {simulation?.enable_twitter && simulation?.enable_reddit
                      ? '双平台'
                      : simulation?.enable_twitter
                        ? 'Twitter'
                        : simulation?.enable_reddit
                          ? 'Reddit'
                          : '未设置'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-slate-400">智能体数量</div>
                  <div className="text-slate-100">{simulation?.profiles_count ?? 0}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-400">总轮次</div>
                  <div className="text-slate-100">{totalRounds}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
