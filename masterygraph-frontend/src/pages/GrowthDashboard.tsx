import { useState, useEffect } from "react";
import { API_BASE } from "../api";

interface GrowthMetrics {
  today: { events: number; unique_users: number; new_signups: number; checkouts: number };
  this_week: { events: number; unique_users: number; new_signups: number; checkouts: number };
  this_month: { events: number; unique_users: number; new_signups: number; checkouts: number };
  funnel: any;
  growth: any;
  estimated_cac: number;
  estimated_ltv: number;
  ltv_cac_ratio: number;
  mrr_estimate: number;
}

export default function GrowthDashboard() {
  const [metrics, setMetrics] = useState<GrowthMetrics | null>(null);
  const [contentStats, setContentStats] = useState<any>(null);
  const [assessmentStats, setAssessmentStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Get analytics dashboard
      const dashRes = await fetch(`${API_BASE}/analytics/dashboard`, {
        headers: { "X-API-Key": "mg-api-key-2024-dev" },
      });
      if (dashRes.ok) setMetrics(await dashRes.json());

      // Get content stats
      const contentRes = await fetch(`${API_BASE}/content/stats`);
      if (contentRes.ok) setContentStats(await contentRes.json());

      // Get assessment stats
      const assessRes = await fetch(`${API_BASE}/assessment/stats`);
      if (assessRes.ok) setAssessmentStats(await assessRes.json());
    } catch (e) {
      console.error("Failed to fetch growth data:", e);
    } finally {
      setLoading(false);
    }
  };

  const generateContent = async () => {
    await fetch(`${API_BASE}/content/generate?count=5`, {
      method: "POST",
      headers: { "X-API-Key": "mg-api-key-2024-dev" },
    });
    fetchData();
  };

  if (loading) return <div style={{ padding: "2rem" }}>Loading growth metrics...</div>;

  return (
    <div style={{ padding: "2rem", maxWidth: 1200, margin: "0 auto" }}>
      <h1 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "0.5rem" }}>
        🚀 Growth Dashboard
      </h1>
      <p style={{ color: "#64748b", marginBottom: "2rem" }}>
        Real-time metrics to track our path to $100K
      </p>

      {/* Key Metrics Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <MetricCard
          title="Today's Events"
          value={metrics?.today.events || 0}
          subtitle={`${metrics?.today.unique_users || 0} unique users`}
          color="#6366f1"
        />
        <MetricCard
          title="New Signups (Week)"
          value={metrics?.this_week.new_signups || 0}
          subtitle={`${metrics?.this_week.checkouts || 0} conversions`}
          color="#10b981"
        />
        <MetricCard
          title="Est. MRR"
          value={`$${metrics?.mrr_estimate?.toFixed(0) || 0}`}
          subtitle={`LTV:CAC = ${metrics?.ltv_cac_ratio?.toFixed(1) || 0}`}
          color="#f59e0b"
        />
        <MetricCard
          title="Assessments"
          value={assessmentStats?.total_assessments || 0}
          subtitle={`${assessmentStats?.today || 0} today`}
          color="#8b5cf6"
        />
      </div>

      {/* Content & Growth Actions */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.5rem", marginBottom: "2rem" }}>
        {/* Content Engine */}
        <div style={{ background: "white", borderRadius: 16, padding: "1.5rem", border: "1px solid #e2e8f0" }}>
          <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "1rem" }}>📝 Content Engine</h3>
          <p style={{ color: "#64748b", marginBottom: "1rem" }}>
            {contentStats?.total_posts || 0} SEO blog posts generated
          </p>
          <button
            onClick={generateContent}
            style={{
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              color: "white",
              border: "none",
              padding: "0.75rem 1.5rem",
              borderRadius: 10,
              fontWeight: 600,
              cursor: "pointer",
              width: "100%",
            }}
          >
            Generate 5 More Posts
          </button>
        </div>

        {/* Funnel */}
        <div style={{ background: "white", borderRadius: 16, padding: "1.5rem", border: "1px solid #e2e8f0" }}>
          <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "1rem" }}>🔄 Funnel (30 days)</h3>
          {metrics?.funnel?.stage_counts && (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {Object.entries(metrics.funnel.stage_counts)
                .filter(([_, count]) => (count as number) > 0)
                .slice(0, 6)
                .map(([stage, count]) => (
                  <div key={stage} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "0.875rem", color: "#64748b", textTransform: "capitalize" }}>
                      {stage.replace(/_/g, " ")}
                    </span>
                    <span style={{ fontWeight: 700, color: "#1e293b" }}>{count as number}</span>
                  </div>
                ))}
            </div>
          )}
        </div>

        {/* Revenue Progress */}
        <div style={{ background: "white", borderRadius: 16, padding: "1.5rem", border: "1px solid #e2e8f0" }}>
          <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "1rem" }}>💰 Revenue Progress</h3>
          <div style={{ marginBottom: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <span style={{ color: "#64748b" }}>Goal: $100K in 6 months</span>
              <span style={{ fontWeight: 700 }}>${((metrics?.mrr_estimate || 0) * 6).toFixed(0)}</span>
            </div>
            <div style={{ height: 8, background: "#f1f5f9", borderRadius: 4, overflow: "hidden" }}>
              <div
                style={{
                  width: `${Math.min(((metrics?.mrr_estimate || 0) * 6) / 100000 * 100, 100)}%`,
                  height: "100%",
                  background: "linear-gradient(90deg, #6366f1, #10b981)",
                  borderRadius: 4,
                  transition: "width 0.5s",
                }}
              />
            </div>
          </div>
          <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
            Current MRR: ${metrics?.mrr_estimate?.toFixed(0) || 0}/mo
          </p>
        </div>
      </div>

      {/* Top Content */}
      {contentStats?.posts && contentStats.posts.length > 0 && (
        <div style={{ background: "white", borderRadius: 16, padding: "1.5rem", border: "1px solid #e2e8f0" }}>
          <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "1rem" }}>📄 Generated Content</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: "0.75rem" }}>
            {contentStats.posts.map((post: any) => (
              <a
                key={post.slug}
                href={`${API_BASE}/content/${post.slug}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  padding: "1rem",
                  background: "#f8fafc",
                  borderRadius: 10,
                  textDecoration: "none",
                  color: "inherit",
                  display: "block",
                }}
              >
                <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "#1e293b", marginBottom: "0.25rem" }}>
                  {post.title}
                </div>
                <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>{post.slug}</div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value, subtitle, color }: { title: string; value: string | number; subtitle: string; color: string }) {
  return (
    <div style={{ background: "white", borderRadius: 16, padding: "1.5rem", border: "1px solid #e2e8f0" }}>
      <div style={{ fontSize: "0.875rem", color: "#64748b", marginBottom: "0.5rem" }}>{title}</div>
      <div style={{ fontSize: "2rem", fontWeight: 800, color, marginBottom: "0.25rem" }}>{value}</div>
      <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>{subtitle}</div>
    </div>
  );
}
