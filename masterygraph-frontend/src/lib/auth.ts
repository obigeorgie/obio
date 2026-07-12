// Auth state management
const AUTH_KEY = 'mg_auth';

export interface AuthUser {
  id: string;
  email: string;
  name: string | null;
  role: string;
  subscription?: {
    plan: string;
    status: string;
  };
}

export interface AuthState {
  token: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
}

export function getAuth(): AuthState {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    if (!raw) return { token: null, user: null, isAuthenticated: false };
    const data = JSON.parse(raw);
    return {
      token: data.token || null,
      user: data.user || null,
      isAuthenticated: !!data.token,
    };
  } catch {
    return { token: null, user: null, isAuthenticated: false };
  }
}

export function setAuth(token: string, user: AuthUser): void {
  localStorage.setItem(AUTH_KEY, JSON.stringify({ token, user }));
}

export function clearAuth(): void {
  localStorage.removeItem(AUTH_KEY);
}

export function getAuthHeaders(): Record<string, string> {
  const auth = getAuth();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (auth.token) {
    headers['Authorization'] = `Bearer ${auth.token}`;
  }
  // Also include API key for backward compatibility
  const apiKey = import.meta.env.VITE_API_KEY;
  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }
  return headers;
}
