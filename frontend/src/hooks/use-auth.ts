/**
 * Authentication Hook - 认证Hook
 *
 * 提供用户注册、登录、令牌管理等前端功能。
 */

import { useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api/v1';

export interface AuthUser {
  user_id: string;
  email: string;
  nickname?: string;
  avatar_url?: string;
  subscription_tier: 'free' | 'pro' | 'premium';
  subscription_status?: string;
  subscription_expires_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  phone?: string;
  nickname?: string;
}

// Token storage
const ACCESS_TOKEN_KEY = 'auth_access_token';
const REFRESH_TOKEN_KEY = 'auth_refresh_token';

export function getStoredTokens(): AuthTokens | null {
  if (typeof window === 'undefined') return null;

  const access_token = localStorage.getItem(ACCESS_TOKEN_KEY);
  const refresh_token = localStorage.getItem(REFRESH_TOKEN_KEY);

  if (access_token && refresh_token) {
    return { access_token, refresh_token };
  }
  return null;
}

export function storeTokens(tokens: AuthTokens): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// API functions
async function fetchAuthUser(accessToken: string): Promise<AuthUser> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }

  const data = await response.json();
  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch user');
  }

  return data.data;
}

async function loginApi(data: LoginRequest): Promise<AuthTokens & { user: AuthUser }> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  const json = await response.json();

  if (!json.success) {
    throw new Error(json.error || 'Login failed');
  }

  return {
    access_token: json.data.access_token,
    refresh_token: json.data.refresh_token,
    user: {
      user_id: json.data.user_id,
      email: json.data.email,
      nickname: json.data.nickname,
      avatar_url: json.data.avatar_url,
      subscription_tier: json.data.subscription_tier,
    },
  };
}

async function registerApi(data: RegisterRequest): Promise<AuthTokens & { user: AuthUser }> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  const json = await response.json();

  if (!json.success) {
    throw new Error(json.error || 'Registration failed');
  }

  return {
    access_token: json.data.access_token,
    refresh_token: json.data.refresh_token,
    user: {
      user_id: json.data.user_id,
      email: json.data.email,
      nickname: json.data.nickname,
      subscription_tier: json.data.subscription_tier,
    },
  };
}

async function refreshTokenApi(refreshToken: string): Promise<AuthTokens> {
  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  const json = await response.json();

  if (!json.success) {
    throw new Error(json.error || 'Token refresh failed');
  }

  return {
    access_token: json.data.access_token,
    refresh_token: json.data.refresh_token,
  };
}

// React Query hooks
export function useAuthUser() {
  const tokens = getStoredTokens();

  return useQuery({
    queryKey: ['auth-user'],
    queryFn: () => fetchAuthUser(tokens!.access_token),
    enabled: !!tokens,
    retry: false,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: loginApi,
    onSuccess: (data) => {
      storeTokens({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
      });
      queryClient.setQueryData(['auth-user'], data.user);
    },
  });
}

export function useRegister() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: registerApi,
    onSuccess: (data) => {
      storeTokens({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
      });
      queryClient.setQueryData(['auth-user'], data.user);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return useCallback(() => {
    clearTokens();
    queryClient.removeQueries({ queryKey: ['auth-user'] });
  }, [queryClient]);
}

export function useRefreshToken() {
  return useMutation({
    mutationFn: refreshTokenApi,
    onSuccess: (data) => {
      storeTokens(data);
    },
  });
}

// Auto-refresh token hook
export function useAutoRefreshToken() {
  const refreshMutation = useRefreshToken();
  const tokens = getStoredTokens();

  useEffect(() => {
    if (!tokens) return;

    // Decode JWT to get expiration (simple base64 decode, not verification)
    try {
      const payload = JSON.parse(atob(tokens.access_token.split('.')[1]));
      const exp = payload.exp * 1000; // Convert to milliseconds
      const now = Date.now();
      const refreshBuffer = 5 * 60 * 1000; // Refresh 5 minutes before expiry

      if (exp - now < refreshBuffer) {
        refreshMutation.mutate(tokens.refresh_token);
      }
    } catch {
      // Ignore decode errors
    }
  }, [tokens, refreshMutation]);
}

// Auth context for global state
export interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: ReturnType<typeof useLogin>['mutate'];
  register: ReturnType<typeof useRegister>['mutate'];
  logout: () => void;
}

export function createAuthState(): AuthState {
  return {
    user: null,
    isLoading: false,
    isAuthenticated: false,
    login: () => {},
    register: () => {},
    logout: () => {},
  };
}
