'use client';

/**
 * Auth hook - thin wrapper around AuthContext for backward compatibility.
 * Prefer importing useAuthContext directly for new code.
 */
export { useAuthContext as useAuth } from '@/contexts/AuthContext';
export type { AuthUser, AuthTokens } from '@/contexts/AuthContext';
