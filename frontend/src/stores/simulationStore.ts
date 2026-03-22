import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Simulation, SimulationStatus } from '@/types/simulation';
import { Agent } from '@/types/agent';

interface SimulationState {
  // State
  simulations: Simulation[];
  activeSimulationId: string | null;
  agents: Agent[];
  isLoading: boolean;
  error: string | null;

  // Simulation actions
  setSimulation: (simulation: Simulation) => void;
  setSimulations: (simulations: Simulation[]) => void;
  updateSimulationStatus: (id: string, status: SimulationStatus) => void;
  updateSimulationProgress: (id: string, progress: number) => void;
  setActiveSimulation: (id: string | null) => void;
  removeSimulation: (id: string) => void;
  clearSimulations: () => void;

  // Agent actions
  setAgents: (agents: Agent[]) => void;
  updateAgent: (agent: Agent) => void;
  setAgentsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useSimulationStore = create<SimulationState>()(
  persist(
    (set) => ({
      simulations: [],
      activeSimulationId: null,
      agents: [],
      isLoading: false,
      error: null,

      setSimulation: (simulation) =>
        set((state) => {
          const exists = state.simulations.find((s) => s.simulation_id === simulation.simulation_id);
          if (exists) {
            return {
              simulations: state.simulations.map((s) =>
                s.simulation_id === simulation.simulation_id ? simulation : s
              ),
              error: null,
            };
          }
          return {
            simulations: [...state.simulations, simulation],
            error: null,
          };
        }),

      setSimulations: (simulations) =>
        set({ simulations, error: null }),

      updateSimulationStatus: (id, status) =>
        set((state) => ({
          simulations: state.simulations.map((s) =>
            s.simulation_id === id ? { ...s, status, updated_at: new Date().toISOString() } : s
          ),
        })),

      updateSimulationProgress: (id, progress) =>
        set((state) => ({
          simulations: state.simulations.map((s) =>
            s.simulation_id === id ? { ...s, progress, updated_at: new Date().toISOString() } : s
          ),
        })),

      setActiveSimulation: (id) =>
        set({ activeSimulationId: id }),

      removeSimulation: (id) =>
        set((state) => ({
          simulations: state.simulations.filter((s) => s.simulation_id !== id),
          activeSimulationId:
            state.activeSimulationId === id ? null : state.activeSimulationId,
        })),

      clearSimulations: () =>
        set({ simulations: [], activeSimulationId: null }),

      setAgents: (agents) =>
        set({ agents, error: null }),

      updateAgent: (agent) =>
        set((state) => ({
          agents: state.agents.map((a) =>
            a.id === agent.id ? agent : a
          ),
        })),

      setAgentsLoading: (isLoading) =>
        set({ isLoading }),

      setError: (error) =>
        set({ error }),
    }),
    {
      name: 'fengxian-cyber-taoist-simulation',
      partialize: (state) => ({
        simulations: state.simulations,
        activeSimulationId: state.activeSimulationId,
      }),
    }
  )
);
