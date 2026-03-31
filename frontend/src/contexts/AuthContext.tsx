'use client';

import React, { createContext, useContext, useCallback, useEffect, useState } from 'react';
import { unstable_batchedUpdates } from 'react-dom';

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

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<AuthUser>;
  register: (email: string, password: string, nickname?: string) => Promise<AuthUser>;
  logout: () => void;
  getAuthHeaders: () => Record<string, string>;
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const ACCESS_TOKEN_KEY = 'auth_access_token';
const REFRESH_TOKEN_KEY = 'auth_refresh_token';

function getStoredTokens(): AuthTokens | null {
  if (typeof window === 'undefined') return null;
  const access = localStorage.getItem(ACCESS_TOKEN_KEY);
  const refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (access && refresh) return { access_token: access, refresh_token: refresh };
  return null;
}

function storeTokens(tokens: AuthTokens): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

async function doRefreshToken(refreshToken: string): Promise<AuthTokens> {
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  const data = await res.json();
  if (!data.success) throw new Error(data.error || 'Refresh failed');
  return {
    access_token: data.data.access_token,
    refresh_token: data.data.refresh_token,
  };
}

async function doFetchUser(accessToken: string): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const data = await res.json();
  if (!data.success) throw new Error(data.error || 'Failed to fetch user');
  return data.data;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Hydrate user from stored tokens on mount
  useEffect(() => {
    const tokens = getStoredTokens();
    if (!tokens) {
      unstable_batchedUpdates(() => {
        setLoading(false);
      });
      return;
    }
    doFetchUser(tokens.access_token)
      .then((u) => unstable_batchedUpdates(() => setUser(u)))
      .catch(() => clearTokens())
      .finally(() => unstable_batchedUpdates(() => setLoading(false)));
  }, []);

  const login = useCallback(async (email: string, password: string): Promise<AuthUser> => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || 'Login failed');
    const tokens: AuthTokens = {
      access_token: data.data.access_token,
      refresh_token: data.data.refresh_token,
    };
    storeTokens(tokens);
    const user: AuthUser = {
      user_id: data.data.user_id,
      email: data.data.email,
      nickname: data.data.nickname,
      avatar_url: data.data.avatar_url,
      subscription_tier: data.data.subscription_tier,
    };
    setUser(user);
    return user;
  }, []);

  const register = useCallback(async (email: string, password: string, nickname?: string): Promise<AuthUser> => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, nickname }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || 'Registration failed');
    const tokens: AuthTokens = {
      access_token: data.data.access_token,
      refresh_token: data.data.refresh_token,
    };
    storeTokens(tokens);
    const user: AuthUser = {
      user_id: data.data.user_id,
      email: data.data.email,
      nickname: data.data.nickname,
      subscription_tier: data.data.subscription_tier,
    };
    setUser(user);
    return user;
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  const getAuthHeaders = useCallback((): Record<string, string> => {
    const tokens = getStoredTokens();
    if (!tokens) return {};
    return { Authorization: `Bearer ${tokens.access_token}` };
  }, []);

  const fetchWithAuth = useCallback(async (input: RequestInfo, init?: RequestInit): Promise<Response> => {
    let tokens = getStoredTokens();
    if (!tokens) throw new Error('Not authenticated');

    let res = await fetch(input, {
      ...init,
      headers: {
        ...(init?.headers || {}),
        ...getAuthHeaders(),
      },
    });

    // 401 → try refresh token once
    if (res.status === 401) {
      try {
        const newTokens = await doRefreshToken(tokens.refresh_token);
        storeTokens(newTokens);
        tokens = newTokens;
        res = await fetch(input, {
          ...init,
          headers: {
            ...(init?.headers || {}),
            Authorization: `Bearer ${tokens.access_token}`,
          },
        });
      } catch {
        logout();
        throw new Error('Session expired. Please log in again.');
      }
    }

    return res;
  }, [getAuthHeaders, logout]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, getAuthHeaders, fetchWithAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be used within AuthProvider');
  return ctx;
}
