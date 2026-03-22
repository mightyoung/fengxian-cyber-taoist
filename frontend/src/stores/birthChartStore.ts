import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Palace, BirthChart, BirthChartInput } from '@/types/birth-chart';

interface BirthChartState {
  // State
  currentChart: BirthChart | null;
  history: BirthChart[];
  activePalaceId: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions - Chart
  setChart: (chart: BirthChart | null) => void;
  clearChart: () => void;
  setInput: (input: BirthChartInput) => void;

  // Actions - Palace
  setActivePalace: (palaceId: string | null) => void;
  clearActivePalace: () => void;

  // Actions - Loading/Error
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useBirthChartStore = create<BirthChartState>()(
  persist(
    (set) => ({
      currentChart: null,
      history: [],
      activePalaceId: null,
      isLoading: false,
      error: null,

      // Chart actions
      setChart: (chart) =>
        set((state) => ({
          currentChart: chart,
          history: chart
            ? [...state.history.filter((c) => c.id !== chart.id), chart].slice(-10)
            : state.history,
          error: null,
        })),

      clearChart: () =>
        set({
          currentChart: null,
          activePalaceId: null,
          error: null,
        }),

      setInput: (input) =>
        set((state) => ({
          currentChart: state.currentChart
            ? { ...state.currentChart, input }
            : null,
        })),

      // Palace actions
      setActivePalace: (palaceId) =>
        set({ activePalaceId: palaceId }),

      clearActivePalace: () =>
        set({ activePalaceId: null }),

      // Loading/Error actions
      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error, isLoading: false }),

      clearError: () => set({ error: null }),
    }),
    {
      name: 'birth-chart-storage',
      partialize: (state) => ({
        history: state.history.slice(-10),
      }),
    }
  )
);

// Selector hooks for optimized re-renders
export const useCurrentChart = () =>
  useBirthChartStore((state) => state.currentChart);

export const useActivePalace = () => {
  const chart = useBirthChartStore((state) => state.currentChart);
  const activePalaceId = useBirthChartStore((state) => state.activePalaceId);

  if (!chart || !activePalaceId) return null;
  return chart.palaces.find((p) => p.id === activePalaceId) || null;
};

export const useChartHistory = () =>
  useBirthChartStore((state) => state.history);

export const useIsLoading = () =>
  useBirthChartStore((state) => state.isLoading);

export const useChartError = () =>
  useBirthChartStore((state) => state.error);
