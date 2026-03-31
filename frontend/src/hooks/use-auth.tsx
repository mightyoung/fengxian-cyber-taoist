'use client';

import { useCallback, useEffect, useState } from 'react';

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

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  phone?: string;
  nickname?: string;
}

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

async function fetchAuthUser(accessToken: string): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  if (!res.ok) throw new Error('Failed to fetch user');
  const data = await res.json();
  if (!data.success) throw new Error(data.error || 'Failed to fetch user');
  return data.data;
}

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tokens = getStoredTokens();
    if (!tokens) {
      setLoading(false);
      return;
    }
    fetchAuthUser(tokens.access_token)
      .then(setUser)
      .catch(() => clearTokens())
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
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

  const register = useCallback(async (email: string, password: string, nickname?: string) => {
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

  return { user, loading, login, register, logout };
}
