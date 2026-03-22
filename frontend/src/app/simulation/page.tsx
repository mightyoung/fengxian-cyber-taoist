'use client';

import { useState, use } from 'react';
import { useSimulationStore } from '@/stores/simulationStore';
import {
  useSimulation,
  useSimulationAgents,
  useStartSimulation,
  usePauseSimulation,
  useStopSimulation,
  useSimulationStatus,
  useSimulations,
  useAgents,
} from '@/hooks/use-simulation';
import { SimulationStatusBar } from '@/components/simulation/simulation-status-bar';
import { SimulationControls } from '@/components/simulation/simulation-controls';
import { AgentGrid } from '@/components/simulation/agent-grid';
import { SimulationTimeline } from '@/components/simulation/simulation-timeline';
import { Agent, TimelineEvent, AgentStatus } from '@/types/agent';
import { SimulationStatus } from '@/types/simulation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

// Demo data for testing - 紫微斗数命理模拟角色
const demoAgents: Agent[] = [
  {
    id: '1',
    name: '玄清真人',
    role: '道士',
    status: AgentStatus.RUNNING,
    activity: 85,
    tweets: 42,
    mentions: 156,
    engagements: 892,
  },
  {
    id: '2',
    name: '李命理',
    role: '命理师',
    status: AgentStatus.RUNNING,
    activity: 72,
    tweets: 38,
    mentions: 124,
    engagements: 567,
  },
  {
    id: '3',
    name: '王风水',
    role: '风水师',
    status: AgentStatus.IDLE,
    activity: 45,
    tweets: 20,
    mentions: 89,
    engagements: 234,
  },
  {
    id: '4',
    name: '赵修士',
    role: '修士',
    status: AgentStatus.COMPLETED,
    activity: 95,
    tweets: 67,
    mentions: 234,
    engagements: 1234,
  },
];

const demoEvents: TimelineEvent[] = [
  {
    id: '1',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    platform: 'twitter',
    agentId: '1',
    action: '发布推文',
    content: '刚刚发布了关于AI的最新观点！',
  },
  {
    id: '2',
    timestamp: new Date(Date.now() - 1000 * 60 * 4),
    platform: 'reddit',
    agentId: '2',
    action: '评论',
    content: '在r/technology上回复了关于产品发布的讨论',
  },
  {
    id: '3',
    timestamp: new Date(Date.now() - 1000 * 60 * 3),
    platform: 'twitter',
    agentId: '4',
    action: '转发',
    content: '转发了科技新闻',
  },
  {
    id: '4',
    timestamp: new Date(Date.now() - 1000 * 60 * 2),
    platform: 'twitter',
    agentId: '1',
    action: '回复',
    content: '回复了粉丝的评论',
  },
  {
    id: '5',
    timestamp: new Date(Date.now() - 1000 * 60),
    platform: 'reddit',
    agentId: '3',
    action: '发帖',
    content: '在r/startups上分享了创业经验',
  },
];

interface SimulationPageProps {
  params: Promise<{ id: string }>;
}

export default function SimulationPage({ params }: SimulationPageProps) {
  const { id } = use(params);
  const [selectedAgentId, setSelectedAgentId] = useState<string | undefined>();

  const {
    simulation,
    isRunning,
    isCompleted,
    isPaused,
  } = useSimulationStatus(id);

  const { agents, isLoading: agentsLoading } = useAgents();
  const startMutation = useStartSimulation();
  const pauseMutation = usePauseSimulation();
  const stopMutation = useStopSimulation();

  // Use demo data if no simulation
  const displayAgents = agents.length > 0 ? agents : demoAgents;
  const displayEvents = demoEvents;
  const currentStatus = simulation?.status || SimulationStatus.PENDING;
  const progress = simulation?.progress || 0;
  const currentRound = (simulation?.current_round as number) || 1;
  const totalRounds = ((simulation?.profiles_count as number) ?? 0) * 10 || 10;

  const handleStart = () => {
    if (id) {
      startMutation.mutate(id);
    }
  };

  const handlePause = () => {
    if (id) {
      pauseMutation.mutate(id);
    }
  };

  const handleStop = () => {
    if (id) {
      stopMutation.mutate(id);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">模拟监控</h1>
          <p className="text-slate-400">实时监控AI智能体社交媒体模拟</p>
        </div>
        <SimulationControls
          status={currentStatus}
          onStart={handleStart}
          onPause={handlePause}
          onStop={handleStop}
          isLoading={startMutation.isPending || pauseMutation.isPending || stopMutation.isPending}
        />
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
          ) : (
            <AgentGrid
              agents={displayAgents}
              selectedAgentId={selectedAgentId}
              onSelectAgent={(agent) => setSelectedAgentId(agent.id)}
            />
          )}
        </TabsContent>

        <TabsContent value="timeline">
          <Card className="bg-slate-800/50 border-slate-700/50">
            <CardHeader>
              <CardTitle className="text-slate-100">事件时间线</CardTitle>
              <CardDescription className="text-slate-400">
                模拟过程中的关键事件
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SimulationTimeline
                events={displayEvents}
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
                  <div className="text-slate-100 font-mono">{id || 'demo-123'}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-400">平台</div>
                  <div className="text-slate-100">Twitter</div>
                </div>
                <div>
                  <div className="text-sm text-slate-400">智能体数量</div>
                  <div className="text-slate-100">{displayAgents.length}</div>
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
