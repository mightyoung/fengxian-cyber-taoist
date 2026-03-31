'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSimulationStore } from '@/stores/simulationStore';
import { Simulation, SimulationStatus, ApiResponse } from '@/types/simulation';
import { Agent, AgentStatus, TimelineEvent } from '@/types/agent';

const API_BASE = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api'}/simulation`;

// Helper to extract data from API response
function extractData<T>(response: ApiResponse<T>): T {
  if (!response.success) {
    throw new Error(response.error || 'Unknown error');
  }
  if (!response.data) {
    throw new Error('No data in response');
  }
  return response.data;
}

// Map backend fields to frontend convenience fields
function mapSimulation(sim: Simulation): Simulation {
  return {
    ...sim,
    id: sim.simulation_id,
    name: `Simulation ${sim.simulation_id.slice(0, 8)}`,
    progress: sim.status === SimulationStatus.RUNNING
      ? Math.round((sim.current_round / (sim.profiles_count * 10 || 1)) * 100)
      : sim.status === SimulationStatus.COMPLETED ? 100 : 0,
    agentCount: sim.profiles_count,
    platform: sim.enable_twitter && sim.enable_reddit
      ? 'parallel'
      : sim.enable_twitter ? 'twitter' : 'reddit',
  };
}

// Simulation API functions
async function fetchSimulations(): Promise<Simulation[]> {
  const response = await fetch(`${API_BASE}/list`);
  if (!response.ok) {
    throw new Error('Failed to fetch simulations');
  }
  const apiResponse: ApiResponse<Simulation[]> = await response.json();
  const data = extractData(apiResponse);
  return data.map(mapSimulation);
}

async function fetchSimulation(id: string): Promise<Simulation> {
  const response = await fetch(`${API_BASE}/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch simulation');
  }
  const apiResponse: ApiResponse<Simulation> = await response.json();
  return mapSimulation(extractData(apiResponse));
}

async function fetchAgents(simulationId: string): Promise<Agent[]> {
  const response = await fetch(`${API_BASE}/${simulationId}/profiles`);
  if (!response.ok) {
    throw new Error('Failed to fetch agents');
  }
  const apiResponse = await response.json() as ApiResponse<{ profiles: Record<string, unknown>[] }>;
  const data = extractData(apiResponse);

  // Transform profiles to agents
  return (data.profiles || []).map((profile: Record<string, unknown>, index: number): Agent => ({
    id: profile.id?.toString() || `agent-${index}`,
    name: profile.name?.toString() || profile.username?.toString() || `Agent ${index}`,
    role: profile.persona?.toString() || profile.role?.toString() || 'user',
    status: profile.status === 'active' ? AgentStatus.RUNNING : AgentStatus.IDLE,
    activity: profile.activity_score as number || 0,
    tweets: profile.tweet_count as number || 0,
    mentions: profile.mention_count as number || 0,
    engagements: profile.engagement_count as number || 0,
    avatar: profile.avatar_url as string | undefined,
  }));
}

async function createSimulation(data: {
  project_id: string;
  graph_id?: string;
  enable_twitter?: boolean;
  enable_reddit?: boolean;
}): Promise<Simulation> {
  const response = await fetch(`${API_BASE}/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to create simulation');
  }
  const apiResponse: ApiResponse<Simulation> = await response.json();
  return mapSimulation(extractData(apiResponse));
}

async function startSimulation(simulationId: string): Promise<Simulation> {
  const response = await fetch(`${API_BASE}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ simulation_id: simulationId }),
  });
  if (!response.ok) {
    throw new Error('Failed to start simulation');
  }
  const apiResponse: ApiResponse<Record<string, unknown>> = await response.json();
  extractData(apiResponse);
  // Return updated simulation state
  return fetchSimulation(simulationId);
}

async function stopSimulation(simulationId: string): Promise<Simulation> {
  const response = await fetch(`${API_BASE}/stop`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ simulation_id: simulationId }),
  });
  if (!response.ok) {
    throw new Error('Failed to stop simulation');
  }
  const apiResponse: ApiResponse<Record<string, unknown>> = await response.json();
  extractData(apiResponse);
  // Return updated simulation state
  return fetchSimulation(simulationId);
}

// Run status response type
export interface SimulationRunStatus {
  simulation_id: string;
  runner_status: 'idle' | 'running' | 'completed' | 'failed';
  current_round: number;
  total_rounds: number;
  progress_percent: number;
  simulated_hours: number;
  total_simulation_hours: number;
  twitter_running: boolean;
  reddit_running: boolean;
  twitter_actions_count: number;
  reddit_actions_count: number;
  total_actions_count: number;
  started_at?: string;
  updated_at?: string;
}

async function fetchRunStatus(simulationId: string): Promise<SimulationRunStatus> {
  const response = await fetch(`${API_BASE}/${simulationId}/run-status`);
  if (!response.ok) {
    throw new Error('Failed to fetch run status');
  }
  const apiResponse: ApiResponse<SimulationRunStatus> = await response.json();
  return extractData(apiResponse);
}

// Run status detail response (includes all_actions for timeline)
export interface SimulationRunStatusDetail {
  simulation_id: string;
  runner_status: 'idle' | 'running' | 'completed' | 'failed';
  current_round: number;
  total_rounds: number;
  progress_percent: number;
  simulated_hours: number;
  total_simulation_hours: number;
  twitter_running: boolean;
  reddit_running: boolean;
  twitter_actions_count: number;
  reddit_actions_count: number;
  total_actions_count: number;
  started_at?: string;
  updated_at?: string;
  all_actions: SimulationAction[];
  twitter_actions: SimulationAction[];
  reddit_actions: SimulationAction[];
}

export interface SimulationAction {
  round_num: number;
  timestamp: string;
  platform: 'twitter' | 'reddit';
  agent_id: number;
  agent_name: string;
  action_type: string;
  action_args: Record<string, unknown>;
  result: unknown;
  success: boolean;
}

async function fetchRunStatusDetail(simulationId: string): Promise<SimulationRunStatusDetail> {
  const response = await fetch(`${API_BASE}/${simulationId}/run-status/detail`);
  if (!response.ok) {
    throw new Error('Failed to fetch run status detail');
  }
  const apiResponse: ApiResponse<SimulationRunStatusDetail> = await response.json();
  return extractData(apiResponse);
}

// Hook for fetching all simulations
export function useSimulations() {
  return useQuery({
    queryKey: ['simulations'],
    queryFn: fetchSimulations,
  });
}

// Hook for fetching a single simulation
export function useSimulation(id: string | null) {
  return useQuery({
    queryKey: ['simulation', id],
    queryFn: () => fetchSimulation(id!),
    enabled: !!id,
  });
}

// Hook for fetching agents for a simulation
export function useSimulationAgents(simulationId: string | null) {
  const { setAgents, setAgentsLoading } = useSimulationStore();

  return useQuery({
    queryKey: ['simulation-agents', simulationId],
    queryFn: async () => {
      setAgentsLoading(true);
      try {
        const agents = await fetchAgents(simulationId!);
        setAgents(agents);
        return agents;
      } finally {
        setAgentsLoading(false);
      }
    },
    enabled: !!simulationId,
    refetchInterval: 3000,
  });
}

// Hook for creating a new simulation
export function useCreateSimulation() {
  const queryClient = useQueryClient();
  const { setSimulation, setError } = useSimulationStore();

  return useMutation({
    mutationFn: createSimulation,
    onSuccess: (simulation) => {
      setSimulation(simulation);
      queryClient.invalidateQueries({ queryKey: ['simulations'] });
    },
    onError: (error) => {
      setError(error.message);
    },
  });
}

// Hook for starting a simulation
export function useStartSimulation() {
  const queryClient = useQueryClient();
  const { updateSimulationStatus, setError } = useSimulationStore();

  return useMutation({
    mutationFn: startSimulation,
    onSuccess: (simulation) => {
      updateSimulationStatus(simulation.simulation_id, SimulationStatus.RUNNING);
      queryClient.invalidateQueries({ queryKey: ['simulation', simulation.simulation_id] });
    },
    onError: (error) => {
      setError(error.message);
    },
  });
}

// Hook for stopping a simulation
export function useStopSimulation() {
  const queryClient = useQueryClient();
  const { updateSimulationStatus, setError } = useSimulationStore();

  return useMutation({
    mutationFn: stopSimulation,
    onSuccess: (simulation) => {
      updateSimulationStatus(simulation.simulation_id, SimulationStatus.FAILED);
      queryClient.invalidateQueries({ queryKey: ['simulation', simulation.simulation_id] });
    },
    onError: (error) => {
      setError(error.message);
    },
  });
}

// Stub for pause - not implemented in backend
export function usePauseSimulation() {
  const { setError } = useSimulationStore();

  return {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    mutate: (_: string) => {
      setError('Pause is not supported in this version');
    },
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    mutateAsync: async (_: string) => {
      throw new Error('Pause is not supported in this version');
    },
    isPending: false,
    isError: false,
    isSuccess: false,
    reset: () => {},
  };
}

// Hook for getting simulation status
export function useSimulationStatus(simulationId: string | null) {
  const { data: simulation, isLoading, error, refetch } = useSimulation(simulationId);

  const isRunning = simulation?.status === SimulationStatus.RUNNING;
  const isCompleted = simulation?.status === SimulationStatus.COMPLETED;
  const isPaused = simulation?.status === SimulationStatus.PAUSED;
  const isPending = simulation?.status === SimulationStatus.CREATED || simulation?.status === SimulationStatus.PREPARING;
  const isReady = simulation?.status === SimulationStatus.READY;
  const isFailed = simulation?.status === SimulationStatus.FAILED;

  return {
    simulation,
    isLoading,
    error,
    isRunning,
    isCompleted,
    isPaused,
    isPending,
    isReady,
    isFailed,
    refetch,
  };
}

// Hook for real-time simulation run status (for polling during simulation)
export function useSimulationRunStatus(simulationId: string | null) {
  return useQuery({
    queryKey: ['simulation-run-status', simulationId],
    queryFn: () => fetchRunStatus(simulationId!),
    enabled: !!simulationId,
    refetchInterval: 3000,
  });
}

// Hook for real-time simulation run status detail (includes all_actions for timeline)
export function useSimulationRunStatusDetail(simulationId: string | null) {
  return useQuery({
    queryKey: ['simulation-run-status-detail', simulationId],
    queryFn: () => fetchRunStatusDetail(simulationId!),
    enabled: !!simulationId,
    refetchInterval: 3000,
  });
}

// Helper to transform simulation actions to timeline events
export function transformActionsToTimelineEvents(actions: SimulationAction[]) {
  return actions.map((action, index): TimelineEvent => ({
    id: `${action.timestamp}-${index}`,
    timestamp: new Date(action.timestamp),
    platform: action.platform,
    agentId: action.agent_id.toString(),
    action: action.action_type,
    content: action.action_args.content as string | undefined,
  }));
}

// Helper hook to get agents from store
export function useAgents() {
  const agents = useSimulationStore((state) => state.agents);
  const isLoading = useSimulationStore((state) => state.isLoading);
  const error = useSimulationStore((state) => state.error);

  return { agents, isLoading, error };
}
