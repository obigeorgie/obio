import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import { AlertTriangle, User, Loader, Target, CheckCircle, ArrowRight } from "lucide-react";

export default function GapAnalysis() {
  const [searchParams] = useSearchParams();
  const initialTopic = searchParams.get("topic") || "";
  const initialLearner = searchParams.get("learner") || "";

  const [topicId, setTopicId] = useState(initialTopic);
  const [learnerId, setLearnerId] = useState(initialLearner);
  const [gaps, setGaps] = useState<any>(null);
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

  async function handleAnalyze(e: React.FormEvent) {
    e.preventDefault();
    if (!topicId.trim()) return;
    setLoading(true);
    setError("");
    try {
      const body: any = { topic_id: topicId };
      if (learnerId) {
        body.learner_id = learnerId;
      }
      const data = await api.analyzeGaps(body);
      setGaps(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Gap Analysis</h2>

      <p className="text-gray-600 mb-6">
        Identify the exact prerequisite topics a learner needs to master before tackling a target topic.
        Find the root cause of learning difficulties.
      </p>

      {/* Input Form */}
      <form onSubmit={handleAnalyze} className="bg-white rounded-lg border p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Topic</label>
            <div className="relative">
              <Target className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={topicId}
                onChange={(e) => setTopicId(e.target.value)}
                placeholder="e.g., topic_123 or topic name"
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
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
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
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
          className="inline-flex items-center gap-2 bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-700 disabled:opacity-50 font-medium"
        >
          {loading ? <Loader className="w-4 h-4 animate-spin" /> : <AlertTriangle className="w-4 h-4" />}
          {loading ? "Analyzing..." : "Analyze Gaps"}
        </button>
      </form>

      {error && <div className="text-red-600 mb-4">{error}</div>}

      {/* Results */}
      {gaps && (
        <div className="space-y-6">
          {/* Summary Card */}
          <div className="bg-white rounded-lg border p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Gap Analysis Results</h3>
                <p className="text-sm text-gray-500">
                  Target: {gaps.target?.name || topicId}
                </p>
              </div>
              <div className={`px-4 py-2 rounded-lg text-sm font-medium ${
                (gaps.gaps?.length || 0) === 0
                  ? "bg-green-100 text-green-700"
                  : "bg-orange-100 text-orange-700"
              }`}>
                {(gaps.gaps?.length || 0) === 0 ? (
                  <span className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    No gaps found
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    {gaps.gaps.length} gap{gaps.gaps.length !== 1 ? "s" : ""} identified
                  </span>
                )}
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">{gaps.total_prerequisites || 0}</div>
                <div className="text-xs text-gray-500">Total Prerequisites</div>
              </div>
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{gaps.gaps?.length || 0}</div>
                <div className="text-xs text-gray-500">Missing (Gaps)</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{gaps.mastered?.length || 0}</div>
                <div className="text-xs text-gray-500">Already Mastered</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{gaps.in_progress?.length || 0}</div>
                <div className="text-xs text-gray-500">In Progress</div>
              </div>
            </div>
          </div>

          {/* Gaps List */}
          {gaps.gaps && gaps.gaps.length > 0 && (
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Identified Gaps</h3>
              <p className="text-sm text-gray-500 mb-4">
                These topics must be mastered before {gaps.target?.name || topicId}. 
                Start with the first one and work your way down.
              </p>
              <div className="space-y-3">
                {gaps.gaps.map((gap: any, index: number) => (
                  <div key={gap.id || index} className="flex items-start gap-4 p-4 bg-red-50 rounded-lg border border-red-100">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center font-bold text-sm">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold text-gray-900">{gap.name || gap.id}</h4>
                        {gap.relationship === "hard" && (
                          <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full font-medium">
                            Required
                          </span>
                        )}
                        {gap.relationship === "soft" && (
                          <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full font-medium">
                            Recommended
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {gap.subject} {gap.domain && `• ${gap.domain}`}
                        {gap.ageRangeStart && ` • Ages ${gap.ageRangeStart}-${gap.ageRangeEnd}`}
                      </p>
                      {gap.description && (
                        <p className="text-sm text-gray-500 mt-1">{gap.description}</p>
                      )}
                    </div>
                    <a
                      href={`/paths?topic=${gap.id}`}
                      className="flex-shrink-0 inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                    >
                      Learn
                      <ArrowRight className="w-4 h-4" />
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Already Mastered */}
          {gaps.mastered && gaps.mastered.length > 0 && (
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                <CheckCircle className="w-5 h-5 inline text-green-600 mr-2" />
                Already Mastered
              </h3>
              <div className="flex flex-wrap gap-2">
                {gaps.mastered.map((m: any) => (
                  <span
                    key={m.id}
                    className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                  >
                    {m.name || m.id}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* In Progress */}
          {gaps.in_progress && gaps.in_progress.length > 0 && (
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">In Progress</h3>
              <div className="flex flex-wrap gap-2">
                {gaps.in_progress.map((p: any) => (
                  <span
                    key={p.id}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                  >
                    {p.name || p.id}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* No Gaps */}
          {gaps.gaps?.length === 0 && (
            <div className="bg-green-50 rounded-lg border border-green-200 p-6 text-center">
              <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-green-900">No Gaps Found!</h3>
              <p className="text-green-700 mt-2">
                This learner has all the prerequisites needed for {gaps.target?.name || topicId}.
                They're ready to start!
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
