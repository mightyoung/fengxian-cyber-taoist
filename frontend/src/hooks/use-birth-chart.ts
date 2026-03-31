'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useBirthChartStore } from '@/stores/birthChartStore';
import { divinationApi } from './use-api';
import { BirthChartInput, BirthChart, Palace, Wuxing, StarLevel, TransformType } from '@/types/birth-chart';

// Query keys
const allKeys = ['birthChart'] as const;

const birthChartKeys = {
  all: allKeys,
  chart: (id: string) => [allKeys[0], 'chart', id] as const,
  analysis: (id: string) => [allKeys[0], 'analysis', id] as const,
  history: [allKeys[0], 'history'] as const,
};

export { birthChartKeys };

// Generate a chart from birth input
export function useGenerateChart() {
  const queryClient = useQueryClient();
  const { setChart, setLoading, setError } = useBirthChartStore();

  return useMutation({
    mutationFn: async (input: BirthChartInput) => {
      const result = await divinationApi.generateChart(input);
      if (result.error) {
        throw new Error(result.error);
      }
      // Transform backend response to frontend BirthChart format
      const backendData = result.data as {
        chart_id: string;
        chart: {
          palaces: Array<{
            id?: string;
            name: string;
            branch?: string;
            tiangan: string;
            stars?: Array<{ name: string; wuxing: string; level: string }>;
            transforms?: Array<{ type: string; star: string; wuxing: string }>;
          }>;
          birth_info: { year: number; month: number; day: number; hour: number; gender: string };
        };
      };
      const { chart_id, chart } = backendData;

      // Backend returns palaces as an object (dict), convert to array
      const palacesArray = Object.entries(chart.palaces || {}).map(([name, p], idx) => ({
        id: (p as { id?: string }).id || String(idx + 1),
        name: name,
        branch: (p as { branch?: string }).branch || '',
        tiangan: (p as { tiangan?: string }).tiangan || '',
        stars: (((p as { stars?: Array<{ name: string; wuxing: string; level: string }> }).stars || []) as Array<{ name: string; wuxing: string; level: string }>).map(s => ({
          name: s.name,
          wuxing: s.wuxing as Wuxing,
          level: s.level as StarLevel,
        })),
        transforms: (((p as { transforms?: Array<{ type: string; star: string; wuxing: string }> }).transforms || []) as Array<{ type: string; star: string; wuxing: string }>)?.map(t => ({
          type: t.type as TransformType,
          star: t.star,
          wuxing: t.wuxing as Wuxing,
        })),
      }));

      // Transform to BirthChart format
      const birthChart: BirthChart = {
        id: chart_id,
        input: chart.birth_info as BirthChartInput,
        palaces: palacesArray,
        createdAt: new Date().toISOString(),
      };
      return birthChart;
    },
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: (data) => {
      if (data) {
        setChart(data);
        queryClient.setQueryData(birthChartKeys.chart(data.id), data);
      }
      setLoading(false);
    },
    onError: (error) => {
      setError(error instanceof Error ? error.message : 'Failed to generate chart');
      setLoading(false);
    },
  });
}

// Get a chart by ID
export function useBirthChart(chartId: string | undefined) {
  return useQuery({
    queryKey: birthChartKeys.chart(chartId || ''),
    queryFn: async () => {
      if (!chartId) return null;
      const result = await divinationApi.getChart(chartId);
      if (result.error) {
        throw new Error(result.error);
      }
      // Transform backend response to frontend BirthChart format
      const backendData = result.data as {
        chart_id: string;
        chart: {
          palaces: Record<string, {
            id?: string;
            name: string;
            branch?: string;
            tiangan: string;
            stars?: Array<{ name: string; wuxing: string; level: string }>;
            transforms?: Array<{ type: string; star: string; wuxing: string }>;
          }>;
          birth_info: { year: number; month: number; day: number; hour: number; gender: string };
        };
      };
      const { chart_id, chart } = backendData;

      // Backend returns palaces as an object (dict), convert to array
      const palacesArray = Object.entries(chart.palaces || {}).map(([name, p], idx) => ({
        id: p.id || String(idx + 1),
        name: name,
        branch: p.branch || '',
        tiangan: p.tiangan || '',
        stars: (p.stars || []).map(s => ({
          name: s.name,
          wuxing: s.wuxing as Wuxing,
          level: s.level as StarLevel,
        })),
        transforms: p.transforms?.map(t => ({
          type: t.type as TransformType,
          star: t.star,
          wuxing: t.wuxing as Wuxing,
        })),
      }));

      // Transform to BirthChart format
      const birthChart: BirthChart = {
        id: chart_id,
        input: chart.birth_info as BirthChartInput,
        palaces: palacesArray,
        createdAt: new Date().toISOString(),
      };
      return birthChart;
    },
    enabled: !!chartId,
  });
}

// Get palace analysis
export function usePalaceAnalysis(chartId: string | undefined, palaceId: string | undefined) {
  return useQuery({
    queryKey: [...birthChartKeys.analysis(chartId || ''), palaceId || ''],
    queryFn: async () => {
      if (!chartId || !palaceId) return null;

      const result = await divinationApi.analyzePalaces(chartId);
      if (result.error) {
        throw new Error(result.error);
      }

      const data = result.data as {
        palace_results: Array<{
          palace_name: string;
          branch: string;
          tiangan: string;
          score: {
            total: number;
            level: string;
            master_star_score: number;
            auxiliary_star_score: number;
            sha_star_deduction: number;
            transform_bonus_score: number;
            palace_environment_score: number;
          };
          stars_in_palace: Array<{ name: string; wuxing: string }>;
          focal_point: string;
          interpretation: string;
        }>;
        strongest_palace: string;
        weakest_palace: string;
        key_palaces: string[];
      };

      // Find the specific palace analysis by palaceId
      const palaceResult = data.palace_results.find(
        (p) => p.palace_name === palaceId || p.branch === palaceId
      );

      if (!palaceResult) {
        return null;
      }

      return {
        summary: palaceResult.interpretation,
        strength: palaceResult.score.level as 'strong' | 'balanced' | 'weak',
        notableStars: palaceResult.stars_in_palace.map((s) => s.name),
        score: palaceResult.score,
        focalPoint: palaceResult.focal_point,
      };
    },
    enabled: !!chartId && !!palaceId,
  });
}

// Get all star analyses
export function useStarAnalyses(chartId: string | undefined) {
  return useQuery({
    queryKey: [...birthChartKeys.analysis(chartId || ''), 'stars'],
    queryFn: async () => {
      if (!chartId) return {};

      const result = await divinationApi.analyzeStars(chartId);
      if (result.error) {
        throw new Error(result.error);
      }

      const data = result.data as {
        main_stars: Array<{
          name: string;
          wuxing: string;
          level: string;
          meaning: string;
          traits: string[];
        }>;
        auxiliary_stars: Array<{
          name: string;
          wuxing: string;
          level: string;
          meaning: string;
          traits: string[];
        }>;
        sha_stars: Array<{
          name: string;
          wuxing: string;
          level: string;
          meaning: string;
          traits: string[];
        }>;
        transform_stars: Array<{
          name: string;
          wuxing: string;
          level: string;
          meaning: string;
          traits: string[];
        }>;
        palace_star_summary: Record<string, string>;
        total_stars_count: number;
      };

      // Transform to a map keyed by star name
      const starAnalyses: Record<string, { meaning: string; traits: string[]; wuxing: string; level: string }> = {};

      [...data.main_stars, ...data.auxiliary_stars, ...data.sha_stars, ...data.transform_stars].forEach((star) => {
        starAnalyses[star.name] = {
          meaning: star.meaning,
          traits: star.traits,
          wuxing: star.wuxing,
          level: star.level,
        };
      });

      return starAnalyses;
    },
    enabled: !!chartId,
  });
}

// Sync with store - keep store in sync with query cache
export function useSyncBirthChart() {
  const { currentChart, setChart } = useBirthChartStore();

  // This hook can be used to sync server state with client store
  return {
    currentChart,
    setChart,
  };
}

// Get chart from store (no server sync)
export function useChartFromStore() {
  return useBirthChartStore((state) => state.currentChart);
}

// Get active palace from store
export function useActivePalaceFromStore() {
  const chart = useBirthChartStore((state) => state.currentChart);
  const activePalaceId = useBirthChartStore((state) => state.activePalaceId);

  if (!chart || !activePalaceId) return null;
  return chart.palaces.find((p: Palace) => p.id === activePalaceId) || null;
}

// Preload chart data (for faster navigation)
export function usePrefetchChart() {
  const queryClient = useQueryClient();

  return {
    prefetch: (chartId: string) => {
      queryClient.prefetchQuery({
        queryKey: birthChartKeys.chart(chartId),
        queryFn: async () => {
          const result = await divinationApi.getChart(chartId);
          if (result.error) {
            throw new Error(result.error);
          }
          // Transform backend response to frontend BirthChart format
          const backendData = result.data as {
            chart_id: string;
            chart: {
              palaces: Record<string, {
                id?: string;
                name: string;
                branch?: string;
                tiangan: string;
                stars?: Array<{ name: string; wuxing: string; level: string }>;
                transforms?: Array<{ type: string; star: string; wuxing: string }>;
              }>;
              birth_info: { year: number; month: number; day: number; hour: number; gender: string };
            };
          };
          const { chart_id, chart } = backendData;

          // Backend returns palaces as an object (dict), convert to array
          const palacesArray = Object.entries(chart.palaces || {}).map(([name, p], idx) => ({
            id: p.id || String(idx + 1),
            name: name,
            branch: p.branch || '',
            tiangan: p.tiangan || '',
            stars: (p.stars || []).map(s => ({
              name: s.name,
              wuxing: s.wuxing as Wuxing,
              level: s.level as StarLevel,
            })),
            transforms: p.transforms?.map(t => ({
              type: t.type as TransformType,
              star: t.star,
              wuxing: t.wuxing as Wuxing,
            })),
          }));

          // Transform to BirthChart format
          const birthChart: BirthChart = {
            id: chart_id,
            input: chart.birth_info as BirthChartInput,
            palaces: palacesArray,
            createdAt: new Date().toISOString(),
          };
          return birthChart;
        },
      });
    },
  };
}
