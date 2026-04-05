/**
 * Unified API client for FengxianCyberTaoist frontend
 * Handles all API calls to the backend
 */

import type {
  ApiResponse,
  BirthChartInput,
  CreateSimulationRequest,
  StartSimulationRequest,
  BuildGraphRequest,
  GenerateReportRequest,
  Simulation,
  Report,
  Project,
  SimulationRunStatus,
  DivinationChartSummary,
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api/v1';

async function handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
  let json: { success?: boolean; data?: T; error?: string; count?: number } = {};
  try {
    json = await response.json();
  } catch {
    // If JSON parsing fails, return error
    return {
      success: false,
      error: `HTTP ${response.status}: ${response.statusText}`,
    };
  }

  // Handle backend response format: {success, data, error}
  if (response.ok && json.success) {
    return {
      success: true,
      data: json.data,
      count: json.count,
    };
  }

  // Handle error responses
  return {
    success: false,
    error: json.error || `HTTP ${response.status}: ${response.statusText}`,
  };
}

// Default fetch options
const defaultOptions: RequestInit = {
  headers: {
    'Content-Type': 'application/json',
  },
};

// Divination API
export const divinationApi = {
  // Generate birth chart
  generateChart: async (input: BirthChartInput) => {
    const response = await fetch(`${API_BASE_URL}/divination/chart/generate`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify(input),
    });
    return handleResponse(response);
  },

  // Get birth chart by ID
  getChart: async (chartId: string) => {
    const response = await fetch(`${API_BASE_URL}/divination/chart/${chartId}`);
    return handleResponse(response);
  },

  // List birth charts
  listCharts: async () => {
    const response = await fetch(`${API_BASE_URL}/divination/chart/list`);
    return handleResponse<DivinationChartSummary[]>(response);
  },

  // Analyze birth chart
  analyzeChart: async (chartId: string) => {
    const response = await fetch(`${API_BASE_URL}/divination/agents/analyze`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ chart_id: chartId }),
    });
    return handleResponse(response);
  },

  // Analyze palaces
  analyzePalaces: async (chartId: string) => {
    const response = await fetch(`${API_BASE_URL}/divination/palaces/analyze`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ chart_id: chartId }),
    });
    return handleResponse(response);
  },

  // Analyze stars
  analyzeStars: async (chartId: string) => {
    const response = await fetch(`${API_BASE_URL}/divination/stars/analyze`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ chart_id: chartId }),
    });
    return handleResponse(response);
  },

  // Analyze relationship
  analyzeRelationship: async (
    chartData: Record<string, unknown>,
    timingTransforms?: Record<string, unknown> | null
  ) => {
    const response = await fetch(`${API_BASE_URL}/divination/relationship/analyze`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({
        chart: chartData,
        timing_transforms: timingTransforms,
      }),
    });
    return handleResponse(response);
  },

  // Get real-time vibe
  getVibe: async (chartId: string) => {
    const response = await fetch(`${API_BASE_URL}/divination/report/vibe`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ chart_id: chartId }),
    });
    return handleResponse(response);
  },

  // Deep consultation
  consult: async (data: Record<string, unknown>) => {
    const response = await fetch(`${API_BASE_URL}/report/consult`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
};

// Graph API
export const graphApi = {
  // Build knowledge graph
  buildGraph: async (data: BuildGraphRequest) => {
    const response = await fetch(`${API_BASE_URL}/graph/build`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse<Project>(response);
  },

  // Get graph info
  getGraph: async (graphId: string) => {
    const response = await fetch(`${API_BASE_URL}/graph/data/${graphId}`);
    return handleResponse<Project>(response);
  },

  // List graphs
  listGraphs: async () => {
    const response = await fetch(`${API_BASE_URL}/graph/project/list`);
    return handleResponse<Project[]>(response);
  },
};

// Simulation API
export const simulationApi = {
  // Create simulation
  createSimulation: async (data: CreateSimulationRequest) => {
    const response = await fetch(`${API_BASE_URL}/simulation/create`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse<Simulation>(response);
  },

  // Fork simulation (Karmic Branching)
  forkSimulation: async (data: Record<string, unknown>) => {
    const response = await fetch(`${API_BASE_URL}/simulation/fork`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse<Simulation>(response);
  },

  // Get simulation
  getSimulation: async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/simulation/${id}`);
    return handleResponse<Simulation>(response);
  },

  // Start simulation
  startSimulation: async (data: StartSimulationRequest) => {
    const response = await fetch(`${API_BASE_URL}/simulation/start`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse<SimulationRunStatus>(response);
  },

  // Pause simulation
  pauseSimulation: async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/simulation/${id}/pause`, {
      method: 'POST',
    });
    return handleResponse<Simulation>(response);
  },

  // Stop simulation
  stopSimulation: async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/simulation/stop`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ simulation_id: id }),
    });
    return handleResponse<Simulation>(response);
  },

  // List simulations
  listSimulations: async () => {
    const response = await fetch(`${API_BASE_URL}/simulation/list`);
    return handleResponse<Simulation[]>(response);
  },

  // Get simulation run status
  getSimulationRunStatus: async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/simulation/${id}/run-status`);
    return handleResponse<SimulationRunStatus>(response);
  },
};

// Report API
export const reportApi = {
  // Generate report
  generateReport: async (data: GenerateReportRequest) => {
    const response = await fetch(`${API_BASE_URL}/report/generate`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse<Report>(response);
  },

  // Get report
  getReport: async (reportId: string) => {
    const response = await fetch(`${API_BASE_URL}/report/${reportId}`);
    return handleResponse<Report>(response);
  },

  // List reports
  listReports: async () => {
    const response = await fetch(`${API_BASE_URL}/report/list`);
    return handleResponse<Report[]>(response);
  },

  // Get vibe poster
  getPoster: async (chartId: string) => {
    const response = await fetch(`${API_BASE_URL}/system/poster`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ chart_id: chartId }),
    });
    return handleResponse(response);
  },

  // Save report feedback
  saveFeedback: async (reportId: string, rating: number, comment?: string) => {
    const response = await fetch(`${API_BASE_URL}/divination/report/id/${reportId}/feedback`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ rating, comment }),
    });
    return handleResponse(response);
  },
};
