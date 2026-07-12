import { useEffect, useState } from "react";
import { api } from "../api";
import { Link } from "react-router-dom";
import {
  Users, BookOpen, GitFork, TrendingUp, Plus, ArrowRight,
  Sparkles, Target, Award, Clock, ChevronRight, Activity,
  Zap, BrainCircuit
} from "lucide-react";
import OnboardingModal, { useOnboarding } from "../components/Onboarding";

function StatCard({
  icon,
  label,
  value,
  subtitle,
  color = "#6366f1",
  delay = 0,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | string;
  subtitle?: string;
  color?: string;
  delay?: number;
}) {
  return (
    <div
      className="bg-white rounded-2xl border border-[#e8e5df] p-5 hover:shadow-lg transition-all duration-300 animate-fade-in-up"
      style={{ animationDelay: `${delay}ms`, opacity: 0 }}
    >
      <div className="flex items-start justify-between">
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: `${color}12` }}
        >
          <div style={{ color }}>{icon}</div>
        </div>
        {typeof value === 'number' && value > 0 && (
          <div className="flex items-center gap-1 text-emerald-500 text-xs font-medium bg-emerald-50 px-2 py-1 rounded-full">
            <TrendingUp className="w-3 h-3" />
            <span>Active</span>
          </div>
        )}
      </div>
      <div className="mt-4">
        <div className="text-2xl font-extrabold text-[#1f1c19] tracking-tight">{value}</div>
        <div className="text-sm font-medium text-[#7c756d] mt-0.5">{label}</div>
        {subtitle && <div className="text-xs text-[#a8a198] mt-0.5">{subtitle}</div>}
      </div>
    </div>
  );
}

function QuickActionCard({
  to,
  icon,
  title,
  description,
  color,
  bgColor,
  delay = 0,
}: {
  to: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
  bgColor: string;
  delay?: number;
}) {
  return (
    <Link
      to={to}
      className="group flex items-start gap-4 p-5 rounded-2xl border border-[#e8e5df] bg-white hover:shadow-lg hover:border-[#d4cfc5] transition-all duration-300 animate-fade-in-up"
      style={{ animationDelay: `${delay}ms`, opacity: 0 }}
    >
      <div
        className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-110"
        style={{ backgroundColor: bgColor }}
      >
        <div style={{ color }}>{icon}</div>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h4 className="font-semibold text-[#1f1c19] text-[15px]">{title}</h4>
          <ChevronRight className="w-4 h-4 text-[#a8a198] opacity-0 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all duration-200" />
        </div>
        <p className="text-sm text-[#7c756d] mt-0.5 leading-relaxed">{description}</p>
      </div>
    </Link>
  );
}

function LearnerRow({ learner, index }: { learner: any; index: number }) {
  const progress = learner.masteryCount && learner.totalTopics
    ? Math.round((learner.masteryCount / learner.totalTopics) * 100)
    : 0;

  return (
    <Link
      to={`/learners/${learner.id}`}
      className="flex items-center gap-4 p-4 rounded-xl bg-white border border-[#e8e5df] hover:shadow-md hover:border-[#d4cfc5] transition-all duration-200 animate-fade-in-up group"
      style={{ animationDelay: `${200 + index * 60}ms`, opacity: 0 }}
    >
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
        {(learner.name || learner.id).charAt(0).toUpperCase()}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-[#1f1c19] text-sm truncate">{learner.name || learner.id}</div>
        <div className="text-xs text-[#a8a198] mt-0.5">
          {learner.age && `Age ${learner.age}`} {learner.grade && `• ${learner.grade}`}
          {learner.subjectFocus && `• ${learner.subjectFocus}`}
        </div>
      </div>
      {progress > 0 && (
        <div className="flex items-center gap-2">
          <div className="w-20 h-2 bg-[#f5f3ef] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#6366f1] to-[#8b5cf6] transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="text-xs font-semibold text-[#6366f1]">{progress}%</span>
        </div>
      )}
      <ChevronRight className="w-4 h-4 text-[#a8a198] opacity-0 group-hover:opacity-100 transition-opacity" />
    </Link>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [learners, setLearners] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { showOnboarding } = useOnboarding();

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [statsData, learnersData] = await Promise.all([
        api.getStats(),
        api.listLearners().catch(() => ({ learners: [] })),
      ]);
      setStats(statsData);
      setLearners(learnersData.learners || []);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-[#f5f3ef] rounded-lg shimmer" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-[#f5f3ef] rounded-2xl shimmer" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-64 bg-[#f5f3ef] rounded-2xl shimmer" />
          <div className="h-64 bg-[#f5f3ef] rounded-2xl shimmer" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
        <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center mb-4">
          <Activity className="w-8 h-8 text-red-400" />
        </div>
        <h3 className="text-lg font-semibold text-[#1f1c19]">Something went wrong</h3>
        <p className="text-sm text-[#7c756d] mt-1">{error}</p>
        <button
          onClick={loadData}
          className="mt-4 px-4 py-2 bg-[#6366f1] text-white rounded-xl text-sm font-medium hover:bg-[#4f46e5] transition-colors"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {showOnboarding && <OnboardingModal />}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 animate-fade-in-up">
        <div>
          <h1 className="text-[28px] font-extrabold text-[#1f1c19] tracking-tight leading-tight">
            Dashboard
          </h1>
          <p className="text-sm text-[#7c756d] mt-1">
            Welcome back — here's what's happening with your learners
          </p>
        </div>
        <Link
          to="/learners"
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-[#6366f1] text-white rounded-xl text-sm font-semibold hover:bg-[#4f46e5] transition-all shadow-sm hover:shadow-md self-start"
        >
          <Plus className="w-4 h-4" />
          Add Learner
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<BookOpen className="w-5 h-5" />}
          label="Topics"
          value={1590}
          subtitle="in taxonomy"
          color="#6366f1"
          delay={0}
        />
        <StatCard
          icon={<GitFork className="w-5 h-5" />}
          label="Dependencies"
          value={3221}
          subtitle="prerequisite links"
          color="#10b981"
          delay={50}
        />
        <StatCard
          icon={<Users className="w-5 h-5" />}
          label="Learners"
          value={stats?.db?.learners || 0}
          subtitle="tracked"
          color="#f59e0b"
          delay={100}
        />
        <StatCard
          icon={<Award className="w-5 h-5" />}
          label="Mastered"
          value={stats?.db?.masteredCount || 0}
          subtitle="topics"
          color="#8b5cf6"
          delay={150}
        />
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-bold text-[#1f1c19] mb-4 tracking-tight">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <QuickActionCard
            to="/learners"
            icon={<Users className="w-5 h-5" />}
            title="Manage Learners"
            description="Add profiles, track mastery, and view progress for each child."
            color="#6366f1"
            bgColor="#eef2ff"
            delay={200}
          />
          <QuickActionCard
            to="/topics"
            icon={<BookOpen className="w-5 h-5" />}
            title="Browse Topics"
            description="Explore 1,590 micro-topics across math, literacy, science, and more."
            color="#10b981"
            bgColor="#ecfdf5"
            delay={260}
          />
          <QuickActionCard
            to="/paths"
            icon={<BrainCircuit className="w-5 h-5" />}
            title="Find Learning Path"
            description="Compute the exact prerequisite path for any learning goal."
            color="#8b5cf6"
            bgColor="#f5f3ff"
            delay={320}
          />
          <QuickActionCard
            to="/gaps"
            icon={<Target className="w-5 h-5" />}
            title="Run Gap Analysis"
            description="Discover the exact micro-topics blocking your child's progress."
            color="#ef4444"
            bgColor="#fef2f2"
            delay={380}
          />
          <QuickActionCard
            to="/tutor"
            icon={<Sparkles className="w-5 h-5" />}
            title="AI Tutor"
            description="Get explanations, practice problems, and hints powered by the taxonomy."
            color="#f59e0b"
            bgColor="#fffbeb"
            delay={440}
          />
          <QuickActionCard
            to="/analytics"
            icon={<Zap className="w-5 h-5" />}
            title="View Analytics"
            description="See growth trends, completion rates, and learning velocity."
            color="#06b6d4"
            bgColor="#ecfeff"
            delay={500}
          />
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        {/* Learners list */}
        <div className="xl:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-[#1f1c19] tracking-tight">Your Learners</h2>
            <Link
              to="/learners"
              className="text-sm font-medium text-[#6366f1] hover:text-[#4f46e5] flex items-center gap-1 transition-colors"
            >
              View all
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {learners.length === 0 ? (
            <div className="bg-white rounded-2xl border border-[#e8e5df] p-10 text-center animate-fade-in-up">
              <div className="w-14 h-14 rounded-2xl bg-[#f5f3ef] flex items-center justify-center mx-auto mb-4">
                <Users className="w-7 h-7 text-[#a8a198]" />
              </div>
              <h3 className="text-base font-semibold text-[#1f1c19]">No learners yet</h3>
              <p className="text-sm text-[#7c756d] mt-1 max-w-sm mx-auto">
                Add your first learner to start tracking their mastery journey through the taxonomy.
              </p>
              <Link
                to="/learners"
                className="inline-flex items-center gap-2 mt-5 px-5 py-2.5 bg-[#6366f1] text-white rounded-xl text-sm font-semibold hover:bg-[#4f46e5] transition-all shadow-sm"
              >
                <Plus className="w-4 h-4" />
                Add first learner
              </Link>
            </div>
          ) : (
            <div className="space-y-2.5">
              {learners.slice(0, 5).map((learner, i) => (
                <LearnerRow key={learner.id} learner={learner} index={i} />
              ))}
            </div>
          )}
        </div>

        {/* System status + tips */}
        <div className="xl:col-span-2 space-y-4">
          {/* System Status */}
          <div className="bg-white rounded-2xl border border-[#e8e5df] p-5 animate-fade-in-up" style={{ animationDelay: '300ms', opacity: 0 }}>
            <h3 className="text-sm font-bold text-[#1f1c19] mb-4 tracking-tight uppercase text-[11px] text-[#a8a198]">
              System Status
            </h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-pulse-soft" />
                <span className="text-sm text-[#7c756d]">API</span>
                <span className="ml-auto text-sm font-semibold text-emerald-600">Healthy</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full" />
                <span className="text-sm text-[#7c756d]">Database</span>
                <span className="ml-auto text-sm font-medium text-[#5c554f]">{stats?.db?.db_path || "SQLite"}</span>
              </div>
              <div className="flex items-center gap-3">
                <Clock className="w-4 h-4 text-[#a8a198]" />
                <span className="text-sm text-[#7c756d]">Updated</span>
                <span className="ml-auto text-xs text-[#a8a198]">
                  {stats?.timestamp ? new Date(stats.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "—"}
                </span>
              </div>
            </div>
          </div>

          {/* Pro tip */}
          <div className="bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] rounded-2xl p-5 text-white animate-fade-in-up" style={{ animationDelay: '400ms', opacity: 0 }}>
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-lg bg-white/20 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Pro Tip</h4>
                <p className="text-xs text-white/80 mt-1 leading-relaxed">
                  Start with a gap analysis on your learner's weakest subject. The graph will find the exact prerequisite chain to build from.
                </p>
                <Link
                  to="/gaps"
                  className="inline-flex items-center gap-1 mt-3 text-xs font-semibold bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg transition-colors"
                >
                  Try it now
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
