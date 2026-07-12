import { useState } from "react";
import { API_BASE } from "../api";
import "../styles/assessment.css";

export default function FreeAssessment() {
  const [formData, setFormData] = useState({
    child_age: 7,
    topic_query: "",
    child_name: "",
    parent_email: "",
    notes: "",
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/assessment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();
      if (data.error) {
        setError(data.error);
        if (data.suggestions) {
          setResult({ suggestions: data.suggestions });
        }
      } else {
        setResult(data);
        // Track event
        fetch(`${API_BASE}/analytics/track`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            event_type: "assessment_complete",
            properties: {
              topic: data.topic?.name,
              readiness: data.readiness?.level,
              has_email: !!formData.parent_email,
            },
          }),
        }).catch(() => {});
      }
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleShare = (platform: string) => {
    if (!result?.share_url) return;
    const text = `I just got a free learning readiness assessment for my child from OBIO! Check it out:`;
    const url = result.share_url;

    if (platform === "twitter") {
      window.open(
        `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`,
        "_blank"
      );
    } else if (platform === "facebook") {
      window.open(
        `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
        "_blank"
      );
    }
  };

  const handleCopyLink = () => {
    if (result?.share_url) {
      navigator.clipboard.writeText(result.share_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getReadinessClass = (level: string) => {
    const map: Record<string, string> = {
      ready: "readiness-ready",
      almost_ready: "readiness-almost_ready",
      needs_prep: "readiness-needs_prep",
      too_advanced: "readiness-too_advanced",
    };
    return map[level] || "";
  };

  if (result && !result.suggestions) {
    return (
      <div className="assessment-page">
        <div className="assessment-result" style={{ maxWidth: 700, width: "100%" }}>
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <h1 style={{ fontSize: "1.75rem", fontWeight: 800, color: "#1e293b", marginBottom: "1rem" }}>
              {result.child.name}&apos;s Learning Assessment
            </h1>
            <span className={`readiness-badge ${getReadinessClass(result.readiness.level)}`}>
              {result.readiness.level.replace("_", " ")}
            </span>
            <p style={{ marginTop: "1rem", color: "#64748b", fontSize: "1.1rem" }}>
              {result.readiness.explanation}
            </p>
          </div>

          <div style={{ marginBottom: "2rem" }}>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#1e293b", marginBottom: "1rem" }}>
              📚 Topic: {result.topic.name}
            </h3>
            <p style={{ color: "#64748b", marginBottom: "0.5rem" }}>{result.topic.description}</p>
            <p style={{ color: "#94a3b8", fontSize: "0.875rem" }}>
              Subject: {result.topic.subject} | Domain: {result.topic.domain} | 
              Age Range: {result.topic.age_range}
            </p>
          </div>

          {result.learning_path.length > 0 && (
            <div style={{ marginBottom: "2rem" }}>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#1e293b", marginBottom: "1rem" }}>
                🗺️ Recommended Learning Path
              </h3>
              <ul className="learning-path-list">
                {result.learning_path.map((step: any) => (
                  <li key={step.step} className="learning-path-item">
                    <span className="path-step-number">{step.step}</span>
                    <div>
                      <div style={{ fontWeight: 600, color: "#1e293b" }}>{step.topic_name}</div>
                      <div style={{ fontSize: "0.875rem", color: "#64748b" }}>
                        {step.estimated_time} — {step.why}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ marginBottom: "2rem" }}>
            <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#1e293b", marginBottom: "1rem" }}>
              💡 Recommendations
            </h3>
            <ul style={{ paddingLeft: "1.25rem", color: "#475569" }}>
              {result.recommendations.map((rec: string, i: number) => (
                <li key={i} style={{ marginBottom: "0.5rem" }}>{rec}</li>
              ))}
            </ul>
          </div>

          <div className="share-section">
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#1e293b" }}>
              📤 Share this assessment
            </h3>
            <p style={{ color: "#64748b", fontSize: "0.875rem", marginBottom: "1rem" }}>
              Help other parents discover their child&apos;s learning path
            </p>
            <div className="share-buttons">
              <button className="share-btn share-twitter" onClick={() => handleShare("twitter")}>
                Share on X
              </button>
              <button className="share-btn share-facebook" onClick={() => handleShare("facebook")}>
                Share on Facebook
              </button>
              <button className="share-btn share-copy" onClick={handleCopyLink}>
                {copied ? "Copied!" : "Copy Link"}
              </button>
            </div>
          </div>

          <div className="upgrade-banner">
            <h3>🚀 Unlock the Full Learning Experience</h3>
            <p>
              Get personalized plans for every topic, AI tutoring, progress tracking, 
              and weekly reports for {result.child.name}.
            </p>
            <button
              className="upgrade-cta"
              onClick={() => window.location.href = result.upgrade_cta.url}
            >
              Start Free Trial →
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="assessment-page">
      <div style={{ width: "100%", maxWidth: 600 }}>
        {/* Stats bar */}
        <div className="stats-bar">
          <div className="stat-item">
            <div className="stat-number">15K+</div>
            <div className="stat-label">Assessments Created</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">98%</div>
            <div className="stat-label">Parent Satisfaction</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">2x</div>
            <div className="stat-label">Faster Mastery</div>
          </div>
        </div>

        <div className="assessment-container">
          <div className="assessment-header">
            <h1>Free Learning Readiness Assessment</h1>
            <p>
              Discover exactly what your child needs to learn next — 
              based on 1,590 research-backed topics and prerequisite chains
            </p>
          </div>

          {error && (
            <div className="assessment-error">
              <p>{error}</p>
              {result?.suggestions && (
                <div>
                  <p style={{ color: "#64748b", marginTop: "1rem" }}>Try these topics:</p>
                  <ul className="suggestions-list">
                    {result.suggestions.map((s: string, i: number) => (
                      <li key={i} onClick={() => setFormData({ ...formData, topic_query: s })}>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <form onSubmit={handleSubmit} className="assessment-form">
            <div className="form-group">
              <label>What topic do you want to assess?</label>
              <input
                type="text"
                placeholder="e.g., addition, fractions, reading comprehension"
                value={formData.topic_query}
                onChange={(e) => setFormData({ ...formData, topic_query: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Child&apos;s age</label>
              <select
                value={formData.child_age}
                onChange={(e) => setFormData({ ...formData, child_age: parseInt(e.target.value) })}
              >
                {Array.from({ length: 15 }, (_, i) => i + 4).map((age) => (
                  <option key={age} value={age}>{age} years old</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Child&apos;s name (optional)</label>
              <input
                type="text"
                placeholder="e.g., Emma"
                value={formData.child_name}
                onChange={(e) => setFormData({ ...formData, child_name: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Your email (optional, for results + tips)</label>
              <input
                type="email"
                placeholder="you@example.com"
                value={formData.parent_email}
                onChange={(e) => setFormData({ ...formData, parent_email: e.target.value })}
              />
            </div>

            <button type="submit" className="assessment-submit" disabled={loading}>
              {loading ? "Analyzing..." : "Get Free Assessment →"}
            </button>
          </form>

          {loading && (
            <div className="assessment-loading">
              <div className="spinner"></div>
              <p>Analyzing prerequisite chains...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
