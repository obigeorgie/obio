import { getAuthHeaders } from "./lib/auth";

export const API_BASE = import.meta.env.VITE_API_URL || "https://api.obiomacare.com/v1";
const API_KEY = import.meta.env.VITE_API_KEY || "";

async function apiFetch(path: string, options: RequestInit = {}) {
  const url = `${API_BASE}${path}`;
  const authHeaders = getAuthHeaders();
  const res = await fetch(url, {
    ...options,
    headers: {
      ...authHeaders,
      "X-API-Key": API_KEY,
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  health: () => apiFetch("/health"),
  searchTopics: (q: string) => apiFetch(`/topics/search?q=${encodeURIComponent(q)}`),
  getTopic: (id: string) => apiFetch(`/topics/${id}`),
  computePath: (body: any) => apiFetch("/paths/compute", { method: "POST", body: JSON.stringify(body) }),
  analyzeGaps: (body: any) => apiFetch("/gaps/analyze", { method: "POST", body: JSON.stringify(body) }),
  generateDiagnostic: (body: any) => apiFetch("/diagnostics/generate", { method: "POST", body: JSON.stringify(body) }),
  explain: (body: any) => apiFetch("/explain", { method: "POST", body: JSON.stringify(body) }),
  createLearner: (body: any) => apiFetch("/learners", { method: "POST", body: JSON.stringify(body) }),
  getLearner: (id: string) => apiFetch(`/learners/${id}`),
  updateMastery: (body: any) => apiFetch("/learners/mastery", { method: "POST", body: JSON.stringify(body) }),
  createPlan: (body: any) => apiFetch("/plans/create", { method: "POST", body: JSON.stringify(body) }),
  getStats: () => apiFetch("/stats"),
  listLearners: () => apiFetch("/learners"),
  // Auth
  register: (body: any) => apiFetch("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body: any) => apiFetch("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  me: () => apiFetch("/auth/me"),
  forgotPassword: (body: any) => apiFetch("/auth/forgot-password", { method: "POST", body: JSON.stringify(body) }),
  resetPassword: (body: any) => apiFetch("/auth/reset-password", { method: "POST", body: JSON.stringify(body) }),
  updatePassword: (body: any) => apiFetch("/auth/update-password", { method: "POST", body: JSON.stringify(body) }),
  updateProfile: (body: any) => apiFetch("/auth/update-profile", { method: "POST", body: JSON.stringify(body) }),
  // Payments
  createCheckout: (body: any) => apiFetch("/payments/create-checkout-session", { method: "POST", body: JSON.stringify(body) }),
  // Tutor
  tutorExplain: (body: any) => apiFetch("/tutor/explain", { method: "POST", body: JSON.stringify(body) }),
  tutorPractice: (body: any) => apiFetch("/tutor/practice", { method: "POST", body: JSON.stringify(body) }),
  tutorAsk: (body: any) => apiFetch("/tutor/ask", { method: "POST", body: JSON.stringify(body) }),
  tutorHint: (body: any) => apiFetch("/tutor/hint", { method: "POST", body: JSON.stringify(body) }),
  tutorPathSummary: (body: any) => apiFetch("/tutor/path-summary", { method: "POST", body: JSON.stringify(body) }),
  tutorAssess: (body: any) => apiFetch("/tutor/assess", { method: "POST", body: JSON.stringify(body) }),
  // Parent Dashboard
  getParentChildren: () => apiFetch("/parent/children"),
  getParentSummary: () => apiFetch("/parent/summary"),
  // Gamification
  getGamificationStats: (learnerId: string) => apiFetch(`/gamification/stats/${learnerId}`),
  recordActivity: (learnerId: string) => apiFetch(`/gamification/activity/${learnerId}`, { method: "POST" }),
  awardBadge: (learnerId: string, badgeId: string, badgeName?: string) => apiFetch(`/gamification/award-badge/${learnerId}`, { method: "POST", body: JSON.stringify({ badge_id: badgeId, badge_name: badgeName }) }),
  // Export
  exportData: (body: any) => apiFetch("/export", { method: "POST", body: JSON.stringify(body) }),
  // Admin
  getAdminStats: () => apiFetch("/admin/stats"),
};
