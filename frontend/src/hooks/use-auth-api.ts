/**
 * Authenticated API client for FengxianCyberTaoist frontend
 *
 * This module provides authenticated API calls that automatically:
 * - Include JWT tokens in requests
 * - Handle 401 errors by refreshing tokens and retrying
 * - Provide consistent error handling
 *
 * Use this for API calls that require authentication.
 * For public endpoints (no auth required), use use-api.ts instead.
 */

import { useAuthContext } from '@/contexts/AuthContext';
import type { ApiResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api/v1';

async function handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
  let json: { success?: boolean; data?: T; error?: string; count?: number } = {};
  try {
    json = await response.json();
  } catch {
    return {
      success: false,
      error: `HTTP ${response.status}: ${response.statusText}`,
    };
  }

  if (response.ok && json.success) {
    return {
      success: true,
      data: json.data,
      count: json.count,
    };
  }

  return {
    success: false,
    error: json.error || `HTTP ${response.status}: ${response.statusText}`,
  };
}

export function useAuthApi() {
  const { fetchWithAuth } = useAuthContext();

  const authFetch = async (endpoint: string, options: RequestInit = {}): Promise<ApiResponse<unknown>> => {
    try {
      const response = await fetchWithAuth(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      return handleResponse(response);
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  };

  return {
    // Payments
    createCheckoutSession: async (priceKey: string, successUrl: string, cancelUrl: string) => {
      return authFetch('/payments/checkout', {
        method: 'POST',
        body: JSON.stringify({ price_key: priceKey, success_url: successUrl, cancel_url: cancelUrl }),
      });
    },

    getSubscription: async () => {
      return authFetch('/payments/subscription', { method: 'GET' });
    },

    cancelSubscription: async (cancelAtPeriodEnd = true) => {
      return authFetch('/payments/cancel', {
        method: 'POST',
        body: JSON.stringify({ cancel_at_period_end: cancelAtPeriodEnd }),
      });
    },

    // User
    getCurrentUser: async () => {
      return authFetch('/auth/me', { method: 'GET' });
    },

    updateUser: async (data: Record<string, unknown>) => {
      return authFetch('/auth/me', {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    // Reports (authenticated)
    listReports: async () => {
      return authFetch('/report/list', { method: 'GET' });
    },

    getReport: async (reportId: string) => {
      return authFetch(`/report/${reportId}`, { method: 'GET' });
    },

    generateReport: async (data: {
      chart_id: string;
      user_name: string;
      target_year: number;
      report_type: string;
    }) => {
      return authFetch('/report/generate', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
  };
}
