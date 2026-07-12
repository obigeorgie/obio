import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import { GitBranch, ArrowRight, BookOpen, Clock, User, Loader } from "lucide-react";

export default function PathFinder() {
  const [searchParams] = useSearchParams();
  const initialTopic = searchParams.get("topic") || "";
  const initialLearner = searchParams.get("learner") || "";

  const [topicId, setTopicId] = useState(initialTopic);
  const [learnerId, setLearnerId] = useState(initialLearner);
  const [path, setPath] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [learners, setLearners] = useState<any[]>([]);

  useEffect(() => {
    loadLearners();
  }, []);

  async function loadLearners() {
    try {
      const data = await api.listLearners();
      setLearners(data.learners || []);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleComputePath(e: React.FormEvent) {
    e.preventDefault();
    if (!topicId.trim()) return;
    setLoading(true);
    setError("");
    try {
      const body: any = { topic_id: topicId };
      if (learnerId) {
        body.learner_id = learnerId;
      }
      const data = await api.computePath(body);
      setPath(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Learning Path Finder</h2>

      {/* Input Form */}
      <form onSubmit={handleComputePath} className="bg-white rounded-lg border p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Topic</label>
            <div className="relative">
              <BookOpen className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={topicId}
                onChange={(e) => setTopicId(e.target.value)}
                placeholder="e.g., topic_123 or topic name"
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Learner (optional)</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={learnerId}
                onChange={(e) => setLearnerId(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select a learner...</option>
                {learners.map((l: any) => (
                  <option key={l.id} value={l.id}>
                    {l.name || l.id} {l.age && `(Age ${l.age})`}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
        >
          {loading ? <Loader className="w-4 h-4 animate-spin" /> : <GitBranch className="w-4 h-4" />}
          {loading ? "Computing..." : "Compute Path"}
        </button>
      </form>

      {error && <div className="text-red-600 mb-4">{error}</div>}

      {/* Path Results */}
      {path && (
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Learning Path</h3>
              <p className="text-sm text-gray-500">
                {path.path?.length || 0} topics from start to goal
                {path.learner_id && ` • Personalized for ${path.learner_id}`}
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
              Estimated: {path.estimated_time || "Varies"}
            </div>
          </div>

          {/* Path Visualization */}
          <div className="space-y-0">
            {path.path?.map((step: any, index: number) => (
              <div key={step.id || index} className="relative">
                {/* Connector line */}
                {index > 0 && (
                  <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-blue-200 -translate-y-1/2" />
                )}
                
                <div className="flex items-start gap-4 py-3">
                  {/* Step number */}
                  <div className="relative z-10 flex-shrink-0 w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-lg">
                    {index + 1}
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 pt-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold text-gray-900">{step.name || step.id}</h4>
                      {step.status && (
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            step.status === "mastered"
                              ? "bg-green-100 text-green-700"
                              : step.status === "in-progress"
                              ? "bg-blue-100 text-blue-700"
                              : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {step.status}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      {step.subject} {step.domain && `• ${step.domain}`}
                      {step.ageRangeStart && ` • Ages ${step.ageRangeStart}-${step.ageRangeEnd}`}
                    </p>
                    {step.description && (
                      <p className="text-sm text-gray-600 mt-2">{step.description}</p>
                    )}
                    {step.prerequisites && step.prerequisites.length > 0 && (
                      <div className="mt-2">
                        <span className="text-xs text-gray-400">Requires: </span>
                        <span className="text-xs text-gray-600">
                          {step.prerequisites.map((p: any) => p.name || p.id).join(", ")}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Arrow */}
                  {index < path.path.length - 1 && (
                    <ArrowRight className="w-5 h-5 text-gray-300 mt-3" />
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Summary */}
          {path.gap_count !== undefined && (
            <div className="mt-6 pt-6 border-t">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-blue-600">{path.path?.length || 0}</div>
                  <div className="text-sm text-gray-500">Total Steps</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-orange-600">{path.gap_count}</div>
                  <div className="text-sm text-gray-500">Gaps to Fill</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">
                    {path.path?.filter((s: any) => s.status === "mastered").length || 0}
                  </div>
                  <div className="text-sm text-gray-500">Already Mastered</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
