import { useState } from "react";
import { api } from "../api";
import { Search, BookOpen, GitBranch, Clock, Target, ChevronDown, ChevronUp } from "lucide-react";

export default function TopicSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedTopic, setExpandedTopic] = useState<string | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await api.searchTopics(query);
      setResults(data.results || []);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadTopicDetail(topicId: string) {
    if (expandedTopic === topicId) {
      setExpandedTopic(null);
      return;
    }
    setExpandedTopic(topicId);
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Topic Search</h2>

      {/* Search */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search topics (e.g., fractions, counting, phonics)..."
              className="w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </form>

      {error && <div className="text-red-600 mb-4">{error}</div>}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-gray-500">{results.length} topics found</p>
          {results.map((topic: any) => (
            <div key={topic.id} className="bg-white rounded-lg border overflow-hidden">
              <button
                onClick={() => loadTopicDetail(topic.id)}
                className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <BookOpen className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{topic.name}</div>
                    <div className="text-sm text-gray-500">
                      {topic.subject} {topic.domain && `• ${topic.domain}`}
                      {topic.ageRangeStart && ` • Ages ${topic.ageRangeStart}-${topic.ageRangeEnd}`}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {topic.prerequisites && topic.prerequisites.length > 0 && (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      {topic.prerequisites.length} prereqs
                    </span>
                  )}
                  {expandedTopic === topic.id ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </button>

              {expandedTopic === topic.id && (
                <div className="px-4 pb-4 border-t bg-gray-50">
                  <div className="pt-4 space-y-4">
                    {/* Description */}
                    {topic.description && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-1">Description</h4>
                        <p className="text-sm text-gray-600">{topic.description}</p>
                      </div>
                    )}

                    {/* Details Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="bg-white p-3 rounded-lg border">
                        <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                          <Target className="w-4 h-4" />
                          Type
                        </div>
                        <div className="font-medium text-gray-900">{topic.type || "N/A"}</div>
                      </div>
                      <div className="bg-white p-3 rounded-lg border">
                        <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                          <Clock className="w-4 h-4" />
                          Age Range
                        </div>
                        <div className="font-medium text-gray-900">
                          {topic.ageRangeStart ? `${topic.ageRangeStart}-${topic.ageRangeEnd}` : "N/A"}
                        </div>
                      </div>
                      <div className="bg-white p-3 rounded-lg border">
                        <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                          <GitBranch className="w-4 h-4" />
                          Prerequisites
                        </div>
                        <div className="font-medium text-gray-900">{topic.prerequisites?.length || 0}</div>
                      </div>
                      <div className="bg-white p-3 rounded-lg border">
                        <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                          <BookOpen className="w-4 h-4" />
                          Curriculum
                        </div>
                        <div className="font-medium text-gray-900">{topic.curriculum || "General"}</div>
                      </div>
                    </div>

                    {/* Prerequisites */}
                    {topic.prerequisites && topic.prerequisites.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Prerequisites</h4>
                        <div className="flex flex-wrap gap-2">
                          {topic.prerequisites.map((prereq: any) => (
                            <span
                              key={prereq.id}
                              className={`px-3 py-1 rounded-full text-xs font-medium ${
                                prereq.relationship === "hard"
                                  ? "bg-red-100 text-red-700"
                                  : "bg-yellow-100 text-yellow-700"
                              }`}
                            >
                              {prereq.name} ({prereq.relationship})
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Assessment Prompts */}
                    {topic.assessmentPrompts && topic.assessmentPrompts.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Assessment Prompts</h4>
                        <ul className="space-y-1">
                          {topic.assessmentPrompts.slice(0, 3).map((prompt: string, i: number) => (
                            <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                              <span className="text-blue-600 mt-1">•</span>
                              {prompt}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex gap-2 pt-2">
                      <a
                        href={`/paths?topic=${topic.id}`}
                        className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm"
                      >
                        <GitBranch className="w-4 h-4" />
                        Find Path to This Topic
                      </a>
                      <a
                        href={`/gaps?topic=${topic.id}`}
                        className="inline-flex items-center gap-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 text-sm"
                      >
                        <Target className="w-4 h-4" />
                        Check Prerequisites
                      </a>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {!loading && results.length === 0 && query && (
        <div className="text-center py-12 text-gray-500">
          <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No topics found for "{query}"</p>
          <p className="text-sm mt-1">Try different keywords like "fractions", "counting", "phonics"</p>
        </div>
      )}

      {!query && (
        <div className="text-center py-12 text-gray-500">
          <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Search for topics to explore the taxonomy</p>
          <p className="text-sm mt-1">Try "addition", "reading comprehension", or "shapes"</p>
        </div>
      )}
    </div>
  );
}
