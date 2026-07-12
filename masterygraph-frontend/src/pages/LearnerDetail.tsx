import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api";
import { ArrowLeft, BookOpen, Target, Activity, Award, Clock } from "lucide-react";

export default function LearnerDetail() {
  const { id } = useParams<{ id: string }>();
  const [learner, setLearner] = useState<any>(null);
  const [mastery, setMastery] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"overview" | "mastery" | "goals" | "activity">("overview");

  useEffect(() => {
    if (id) loadLearnerData();
  }, [id]);

  async function loadLearnerData() {
    try {
      const [learnerData, masteryData] = await Promise.all([
        api.getLearner(id!),
        apiFetch(`/learners/${id}/mastery`),
      ]);
      setLearner(learnerData);
      setMastery(masteryData.mastery || []);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function apiFetch(path: string) {
    const base = import.meta.env.VITE_API_URL || "https://api.obiomacare.com/v1";
    const res = await fetch(`${base}${path}`, {
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": import.meta.env.VITE_API_KEY || "",
      },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  const masteredCount = mastery.filter((m: any) => m.status === "mastered").length;
  const inProgressCount = mastery.filter((m: any) => m.status === "in-progress").length;

  if (loading) return <div className="text-gray-500">Loading...</div>;
  if (error) return <div className="text-red-600">Error: {error}</div>;
  if (!learner) return <div className="text-gray-500">Learner not found</div>;

  return (
    <div>
      <Link to="/learners" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
        <ArrowLeft className="w-4 h-4" />
        Back to Learners
      </Link>

      {/* Header */}
      <div className="bg-white rounded-lg border p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{learner.name || learner.id}</h2>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
              {learner.age && <span>Age: {learner.age}</span>}
              {learner.grade && <span>Grade: {learner.grade}</span>}
              <span>ID: {learner.id}</span>
            </div>
            {learner.notes && <p className="mt-3 text-gray-600">{learner.notes}</p>}
          </div>
          <div className="flex gap-2">
            <Link
              to={`/paths?learner=${learner.id}`}
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm"
            >
              <BookOpen className="w-4 h-4" />
              Find Path
            </Link>
            <Link
              to={`/gaps?learner=${learner.id}`}
              className="inline-flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 text-sm"
            >
              <Target className="w-4 h-4" />
              Check Gaps
            </Link>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{masteredCount}</div>
            <div className="text-sm text-gray-500">Mastered</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{inProgressCount}</div>
            <div className="text-sm text-gray-500">In Progress</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {mastery.length > 0 ? Math.round((masteredCount / mastery.length) * 100) : 0}%
            </div>
            <div className="text-sm text-gray-500">Completion</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border">
        <div className="flex border-b">
          {[
            { id: "overview", label: "Overview", icon: Activity },
            { id: "mastery", label: "Mastery Map", icon: Award },
            { id: "goals", label: "Goals", icon: Target },
            { id: "activity", label: "Activity", icon: Clock },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === "overview" && (
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Recent Activity</h3>
              {mastery.length === 0 ? (
                <p className="text-gray-500">No mastery records yet. Start by finding a learning path.</p>
              ) : (
                <div className="space-y-2">
                  {mastery.slice(0, 10).map((m: any) => (
                    <div key={m.topic_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-gray-900">{m.topic_id}</div>
                        <div className="text-sm text-gray-500">{m.status}</div>
                      </div>
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
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "mastery" && (
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Mastery Map</h3>
              {mastery.length === 0 ? (
                <p className="text-gray-500">No topics tracked yet.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {mastery.map((m: any) => (
                    <div key={m.topic_id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-sm">{m.topic_id}</span>
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
                      </div>
                      {m.confidence && (
                        <div className="text-xs text-gray-500">Confidence: {Math.round(m.confidence * 100)}%</div>
                      )}
                      {m.last_assessed && (
                        <div className="text-xs text-gray-400 mt-1">
                          Last assessed: {new Date(m.last_assessed).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "goals" && (
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Learning Goals</h3>
              <p className="text-gray-500">No goals set yet. Create a goal from the Path Finder.</p>
            </div>
          )}

          {activeTab === "activity" && (
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Activity Log</h3>
              <p className="text-gray-500">Activity tracking coming soon.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
