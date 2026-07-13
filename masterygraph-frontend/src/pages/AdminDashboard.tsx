import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Users, BookOpen, CreditCard, Activity, TrendingUp, Shield,
  AlertTriangle, ArrowLeft, BarChart3, BrainCircuit, GraduationCap
} from "lucide-react";
import { api } from "../api";

interface AdminStats {
  users: { total: number; by_role: Record<string, number>; recent_signups_7d: number };
  subscriptions: { active: number; plan_breakdown: Record<string, number>; total_revenue_dollars: number };
  content: { learners: number; diagnostics: number; learning_paths: number };
  activity: { recent_events_24h: number };
  timestamp: string;
}

function StatCard({
  icon: Icon, title, value, subtext, color
}: {
  icon: any; title: string; value: string | number; subtext?: string; color: string;
}) {
  return (
    <div className="bg-white rounded-2xl border border-[#e8e5df] p-5 hover:shadow-md transition-all">
      <div className="flex items-center justify-between mb-3">
        <div className={`w-10 h-10 rounded-xl ${color} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <span className="text-xs text-[#a8a198] font-medium">{title}</span>
      </div>
      <div className="text-2xl font-extrabold text-[#1f1c19]">{value}</div>
      {subtext && <div className="text-xs text-[#a8a198] mt-1">{subtext}</div>}
    </div>
  );
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    checkAdmin();
  }, []);

  function checkAdmin() {
    const auth = localStorage.getItem("auth");
    if (!auth) {
      setError("Please login to access admin dashboard");
      setLoading(false);
      return;
    }
    try {
      const user = JSON.parse(auth);
      if (user.role !== "admin") {
        setError("Admin access required");
        setLoading(false);
        return;
      }
      loadStats();
    } catch {
      setError("Invalid auth data");
      setLoading(false);
    }
  }

  async function loadStats() {
    try {
      const data = await api.getAdminStats();
      setStats(data);
    } catch (e: any) {
      setError(e.message || "Failed to load stats");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#faf9f7] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-3 border-[#6366f1] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-[#7c756d]">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#faf9f7] flex items-center justify-center">
        <div className="text-center max-w-md px-4">
          <div className="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
          <h1 className="text-xl font-bold text-[#1f1c19]">Access Denied</h1>
          <p className="text-sm text-[#7c756d] mt-2">{error}</p>
          <Link
            to="/"
            className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-[#6366f1] text-white rounded-xl text-sm font-semibold"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="min-h-screen bg-[#faf9f7]">
      <div className="max-w-6xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#1f1c19] flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-[#1f1c19]">Admin Dashboard</h1>
              <p className="text-xs text-[#a8a198]">MasteryGraph Operations Center</p>
            </div>
          </div>
          <div className="text-xs text-[#a8a198]">
            Last updated: {new Date(stats.timestamp).toLocaleTimeString()}
          </div>
        </div>

        {/* Key Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatCard
            icon={Users}
            title="Total Users"
            value={stats.users.total}
            subtext={`+${stats.users.recent_signups_7d} this week`}
            color="bg-[#6366f1]"
          />
          <StatCard
            icon={CreditCard}
            title="Active Subs"
            value={stats.subscriptions.active}
            subtext={`$${stats.subscriptions.total_revenue_dollars} MRR`}
            color="bg-[#10b981]"
          />
          <StatCard
            icon={GraduationCap}
            title="Learners"
            value={stats.content.learners}
            subtext={`${stats.content.diagnostics} diagnostics run`}
            color="bg-[#f59e0b]"
          />
          <StatCard
            icon={Activity}
            title="Events 24h"
            value={stats.activity.recent_events_24h}
            subtext="System activity"
            color="bg-[#8b5cf6]"
          />
        </div>

        {/* Secondary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-2xl border border-[#e8e5df] p-5">
            <h3 className="text-sm font-bold text-[#1f1c19] mb-4 flex items-center gap-2">
              <Users className="w-4 h-4 text-[#6366f1]" />
              Users by Role
            </h3>
            <div className="space-y-3">
              {Object.entries(stats.users.by_role).map(([role, count]) => (
                <div key={role} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      role === "admin" ? "bg-red-400" :
                      role === "teacher" ? "bg-[#f59e0b]" : "bg-[#6366f1]"
                    }`} />
                    <span className="text-sm text-[#7c756d] capitalize">{role}</span>
                  </div>
                  <span className="text-sm font-semibold text-[#1f1c19]">{count}</span>
                </div>
              ))}
              {Object.keys(stats.users.by_role).length === 0 && (
                <p className="text-sm text-[#a8a198]">No users yet</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-[#e8e5df] p-5">
            <h3 className="text-sm font-bold text-[#1f1c19] mb-4 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-[#10b981]" />
              Plan Breakdown
            </h3>
            <div className="space-y-3">
              {Object.entries(stats.subscriptions.plan_breakdown).map(([plan, count]) => (
                <div key={plan} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      plan === "educator" ? "bg-[#8b5cf6]" :
                      plan === "family" ? "bg-[#10b981]" : "bg-[#6366f1]"
                    }`} />
                    <span className="text-sm text-[#7c756d] capitalize">{plan}</span>
                  </div>
                  <span className="text-sm font-semibold text-[#1f1c19]">{count}</span>
                </div>
              ))}
              {Object.keys(stats.subscriptions.plan_breakdown).length === 0 && (
                <p className="text-sm text-[#a8a198]">No active subscriptions</p>
              )}
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-[#e8e5df] p-5">
            <h3 className="text-sm font-bold text-[#1f1c19] mb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-[#f59e0b]" />
              Content Stats
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#7c756d]">Learning Paths</span>
                <span className="text-sm font-semibold text-[#1f1c19]">{stats.content.learning_paths}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#7c756d]">Diagnostics</span>
                <span className="text-sm font-semibold text-[#1f1c19]">{stats.content.diagnostics}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#7c756d]">Total Learners</span>
                <span className="text-sm font-semibold text-[#1f1c19]">{stats.content.learners}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="bg-white rounded-2xl border border-[#e8e5df] p-5">
          <h3 className="text-sm font-bold text-[#1f1c19] mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Link
              to="/analytics"
              className="flex items-center gap-3 p-4 rounded-xl border border-[#e8e5df] hover:border-[#6366f1] hover:shadow-md transition-all"
            >
              <div className="w-10 h-10 rounded-xl bg-[#6366f1]/10 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-[#6366f1]" />
              </div>
              <div>
                <div className="font-semibold text-[#1f1c19] text-sm">Analytics</div>
                <div className="text-xs text-[#a8a198]">View growth metrics</div>
              </div>
            </Link>

            <Link
              to="/gaps"
              className="flex items-center gap-3 p-4 rounded-xl border border-[#e8e5df] hover:border-[#10b981] hover:shadow-md transition-all"
            >
              <div className="w-10 h-10 rounded-xl bg-[#10b981]/10 flex items-center justify-center">
                <BrainCircuit className="w-5 h-5 text-[#10b981]" />
              </div>
              <div>
                <div className="font-semibold text-[#1f1c19] text-sm">Gap Analysis</div>
                <div className="text-xs text-[#a8a198]">Check learner paths</div>
              </div>
            </Link>

            <a
              href="https://api.obiomacare.com/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-4 rounded-xl border border-[#e8e5df] hover:border-[#8b5cf6] hover:shadow-md transition-all"
            >
              <div className="w-10 h-10 rounded-xl bg-[#8b5cf6]/10 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-[#8b5cf6]" />
              </div>
              <div>
                <div className="font-semibold text-[#1f1c19] text-sm">API Docs</div>
                <div className="text-xs text-[#a8a198]">View documentation</div>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
