/**
 * Unified API client for FengxianCyberTaoist frontend
 * Handles all API calls to the backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

async function handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
  let json: { success?: boolean; data?: T; error?: string } = {};
  try {
    json = await response.json();
  } catch {
    // If JSON parsing fails, return error
    return {
      error: `HTTP ${response.status}: ${response.statusText}`,
    };
  }

  // Handle backend response format: {success, data, error}
  if (response.ok && json.success && json.data) {
    return { data: json.data };
  }

  // Handle error responses
  return {
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
  generateChart: async (input: {
    year: number;
    month: number;
    day: number;
    hour: number;
    gender: 'male' | 'female';
  }) => {
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

  // Analyze birth chart
  analyzeChart: async (chartId: string) => {
    const response = await fetch(`${API_BASE_URL}/divination/agents/analyze`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ chartId }),
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
};

// Graph API
export const graphApi = {
  // Build knowledge graph
  buildGraph: async (text: string) => {
    const response = await fetch(`${API_BASE_URL}/graph/build`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ text }),
    });
    return handleResponse(response);
  },

  // Get graph info
  getGraph: async (graphId: string) => {
    const response = await fetch(`${API_BASE_URL}/graph/${graphId}`);
    return handleResponse(response);
  },

  // List graphs
  listGraphs: async () => {
    const response = await fetch(`${API_BASE_URL}/graph`);
    return handleResponse(response);
  },
};

// Simulation API
export const simulationApi = {
  // Create simulation
  createSimulation: async (data: {
    name: string;
    graphId: string;
    platform: 'twitter' | 'reddit';
    totalRounds: number;
    agentCount: number;
  }) => {
    const response = await fetch(`${API_BASE_URL}/simulation`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Get simulation
  getSimulation: async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/simulation/${id}`);
    return handleResponse(response);
  },

  // Start simulation
  startSimulation: async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/simulation/${id}/start`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  // Pause simulation
  pauseSimulation: async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/simulation/${id}/pause`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  // Stop simulation
  stopSimulation: async (id: string) => {
    const response = await fetch(`${API_BASE_URL}/simulation/${id}/stop`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  // List simulations
  listSimulations: async () => {
    const response = await fetch(`${API_BASE_URL}/simulation`);
    return handleResponse(response);
  },
};

// Report API
export const reportApi = {
  // Generate report
  generateReport: async (simulationId: string) => {
    const response = await fetch(`${API_BASE_URL}/report/generate`, {
      ...defaultOptions,
      method: 'POST',
      body: JSON.stringify({ simulationId }),
    });
    return handleResponse(response);
  },

  // Get report
  getReport: async (reportId: string) => {
    const response = await fetch(`${API_BASE_URL}/report/${reportId}`);
    return handleResponse(response);
  },
};
