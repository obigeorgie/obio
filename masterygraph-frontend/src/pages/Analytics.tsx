import { useEffect, useState } from "react";
import { api } from "../api";
import { BarChart3, TrendingUp, Award, Clock, BookOpen } from "lucide-react";

// Simple SVG Bar Chart Component
function BarChart({ data, maxValue }: { data: { label: string; value: number; color: string }[]; maxValue: number }) {
  const height = 200;
  const barWidth = 40;
  const gap = 20;
  const chartWidth = data.length * (barWidth + gap) + gap;
  
  return (
    <svg width={chartWidth} height={height + 40} className="mx-auto">
      {/* Y-axis grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((pct) => (
        <line
          key={pct}
          x1={gap}
          y1={height - pct * height}
          x2={chartWidth - gap}
          y2={height - pct * height}
          stroke="#e5e7eb"
          strokeDasharray="4"
        />
      ))}
      
      {data.map((item, i) => {
        const barHeight = (item.value / maxValue) * height;
        const x = gap + i * (barWidth + gap);
        const y = height - barHeight;
        
        return (
          <g key={item.label}>
            <rect
              x={x}
              y={y}
              width={barWidth}
              height={barHeight}
              fill={item.color}
              rx={4}
            />
            <text
              x={x + barWidth / 2}
              y={height + 20}
              textAnchor="middle"
              className="text-xs fill-gray-600"
              style={{ fontSize: '12px' }}
            >
              {item.label}
            </text>
            <text
              x={x + barWidth / 2}
              y={y - 8}
              textAnchor="middle"
              className="text-xs fill-gray-700 font-medium"
              style={{ fontSize: '12px' }}
            >
              {item.value}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// Progress Ring Component
function ProgressRing({ progress, size = 120, strokeWidth = 8 }: { progress: number; size?: number; strokeWidth?: number }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;
  
  return (
    <svg width={size} height={size} className="transform -rotate-90">
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke="#e5e7eb"
        strokeWidth={strokeWidth}
        fill="none"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke={progress >= 80 ? "#22c55e" : progress >= 50 ? "#3b82f6" : "#f97316"}
        strokeWidth={strokeWidth}
        fill="none"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        className="transition-all duration-1000"
      />
    </svg>
  );
}

export default function Analytics() {
  const [, setStats] = useState<any>(null);
  const [learners, setLearners] = useState<any[]>([]);
  const [selectedLearner, setSelectedLearner] = useState<string>("");
  const [learnerMastery, setLearnerMastery] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedLearner) {
      loadLearnerMastery(selectedLearner);
    }
  }, [selectedLearner]);

  async function loadData() {
    try {
      const [statsData, learnersData] = await Promise.all([
        api.getStats(),
        api.listLearners().catch(() => ({ learners: [] })),
      ]);
      setStats(statsData);
      setLearners(learnersData.learners || []);
      if (learnersData.learners?.length > 0) {
        setSelectedLearner(learnersData.learners[0].id);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function loadLearnerMastery(learnerId: string) {
    try {
      const base = import.meta.env.VITE_API_URL || "https://api.obiomacare.com/v1";
      const res = await fetch(`${base}/learners/${learnerId}/mastery`, {
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": import.meta.env.VITE_API_KEY || "",
        },
      });
      if (res.ok) {
        const data = await res.json();
        setLearnerMastery(data.mastery || []);
      }
    } catch (e) {
      console.error(e);
    }
  }

  // Calculate subject breakdown
  const subjectBreakdown = learnerMastery.reduce((acc: any, m: any) => {
    const subject = m.subject || "Unknown";
    if (!acc[subject]) acc[subject] = { total: 0, mastered: 0 };
    acc[subject].total++;
    if (m.status === "mastered") acc[subject].mastered++;
    return acc;
  }, {});

  const subjectChartData = Object.entries(subjectBreakdown).map(([subject, data]: [string, any]) => ({
    label: subject.length > 8 ? subject.slice(0, 8) + "..." : subject,
    value: data.mastered,
    color: "#6366f1",
  }));

  const masteryStats = {
    total: learnerMastery.length,
    mastered: learnerMastery.filter((m: any) => m.status === "mastered").length,
    inProgress: learnerMastery.filter((m: any) => m.status === "in-progress").length,
    notStarted: learnerMastery.filter((m: any) => m.status === "not-started").length,
  };

  const completionRate = masteryStats.total > 0 ? Math.round((masteryStats.mastered / masteryStats.total) * 100) : 0;

  if (loading) return <div className="text-gray-500">Loading...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Analytics & Progress</h2>

      {/* Learner Selector */}
      {learners.length > 0 && (
        <div className="bg-white rounded-lg border p-4 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Learner</label>
          <select
            value={selectedLearner}
            onChange={(e) => setSelectedLearner(e.target.value)}
            className="w-full md:w-64 border rounded-lg px-3 py-2"
          >
            {learners.map((l: any) => (
              <option key={l.id} value={l.id}>
                {l.name || l.id}
              </option>
            ))}
          </select>
        </div>
      )}

      {learners.length === 0 ? (
        <div className="bg-white rounded-lg border p-8 text-center">
          <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No learners to analyze. Add a learner first.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg border p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <BookOpen className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{masteryStats.total}</div>
                  <div className="text-sm text-gray-500">Topics Tracked</div>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-50 rounded-lg">
                  <Award className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{masteryStats.mastered}</div>
                  <div className="text-sm text-gray-500">Mastered</div>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-50 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-orange-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{masteryStats.inProgress}</div>
                  <div className="text-sm text-gray-500">In Progress</div>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg border p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-50 rounded-lg">
                  <Clock className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">{completionRate}%</div>
                  <div className="text-sm text-gray-500">Completion</div>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Ring & Subject Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Completion Ring */}
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">Overall Progress</h3>
              <div className="flex items-center justify-center">
                <div className="relative">
                  <ProgressRing progress={completionRate} size={160} strokeWidth={12} />
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold text-gray-900">{completionRate}%</span>
                    <span className="text-sm text-gray-500">Complete</span>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-6 text-center">
                <div>
                  <div className="text-lg font-semibold text-green-600">{masteryStats.mastered}</div>
                  <div className="text-xs text-gray-500">Mastered</div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-blue-600">{masteryStats.inProgress}</div>
                  <div className="text-xs text-gray-500">In Progress</div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-gray-600">{masteryStats.notStarted}</div>
                  <div className="text-xs text-gray-500">Not Started</div>
                </div>
              </div>
            </div>

            {/* Subject Breakdown */}
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">Mastery by Subject</h3>
              {subjectChartData.length > 0 ? (
                <BarChart data={subjectChartData} maxValue={Math.max(...subjectChartData.map(d => d.value), 1)} />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No subject data yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Mastery Activity */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Mastery Updates</h3>
            {learnerMastery.length === 0 ? (
              <p className="text-gray-500">No mastery records yet. Start tracking progress from the Learners page.</p>
            ) : (
              <div className="space-y-2">
                {learnerMastery.slice(0, 10).map((m: any) => (
                  <div key={m.topic_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          m.status === "mastered"
                            ? "bg-green-500"
                            : m.status === "in-progress"
                            ? "bg-blue-500"
                            : "bg-gray-300"
                        }`}
                      />
                      <span className="font-medium text-gray-900">{m.topic_id}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          m.status === "mastered"
                            ? "bg-green-100 text-green-700"
                            : m.status === "in-progress"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {m.status}
                      </span>
                      {m.last_assessed && (
                        <span className="text-xs text-gray-400">
                          {new Date(m.last_assessed).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
