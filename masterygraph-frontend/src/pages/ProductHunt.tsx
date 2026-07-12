import { Brain, Zap, Target, BarChart3, ArrowRight, Check } from "lucide-react";
import "../styles/producthunt.css";

export default function ProductHuntLaunch() {
  return (
    <div className="ph-page">
      {/* Hero */}
      <section className="ph-hero">
        <div className="ph-badge">
          🚀 Featured on Product Hunt — July 2026
        </div>
        <div className="ph-hero-icon">
          <Brain size={64} strokeWidth={1.5} />
        </div>
        <h1>
          OBIO
        </h1>
        <p className="ph-tagline">
          The GPS for your child's learning journey.
          <br />
          1,590 topics. 3,221 prerequisite relationships. One clear path.
        </p>
        <div className="ph-hero-cta">
          <a href="https://app.obiomacare.com/assessment" className="ph-btn-primary">
            Try Free Assessment <ArrowRight size={18} />
          </a>
          <a href="https://app.obiomacare.com/register" className="ph-btn-secondary">
            Start Free Trial
          </a>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="ph-stats">
        <div className="ph-stat">
          <div className="ph-stat-num">1,590</div>
          <div className="ph-stat-label">Research-Backed Topics</div>
        </div>
        <div className="ph-stat">
          <div className="ph-stat-num">3,221</div>
          <div className="ph-stat-label">Prerequisite Relationships</div>
        </div>
        <div className="ph-stat">
          <div className="ph-stat-num">7</div>
          <div className="ph-stat-label">Curricula Aligned</div>
        </div>
        <div className="ph-stat">
          <div className="ph-stat-num">50+</div>
          <div className="ph-stat-label">SEO Guides Published</div>
        </div>
      </section>

      {/* Problem / Solution */}
      <section className="ph-section">
        <h2>Parents are flying blind. We fixed that.</h2>
        <div className="ph-problem-grid">
          <div className="ph-problem-card">
            <div className="ph-problem-icon">❌</div>
            <h3>The Problem</h3>
            <ul>
              <li>"What should my child learn next?" → No clear answer</li>
              <li>Worksheets don't teach prerequisites</li>
              <li>Tutors cost $50-100/hour with no roadmap</li>
              <li>Kids hit walls because foundational gaps are invisible</li>
            </ul>
          </div>
          <div className="ph-solution-card">
            <div className="ph-solution-icon">✅</div>
            <h3>The Solution</h3>
            <ul>
              <li>Enter any topic + age → get the exact prerequisite path</li>
              <li>AI tutor explains concepts in kid-friendly language</li>
              <li>Mastery tracking shows progress on every micro-topic</li>
              <li>$12/month vs $400/month for tutoring</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="ph-section ph-alt">
        <h2>How It Works</h2>
        <div className="ph-features">
          <div className="ph-feature">
            <div className="ph-feature-icon">
              <Target size={32} />
            </div>
            <h3>1. Free Assessment</h3>
            <p>Pick any topic. Enter your child's age. Get a complete readiness report with prerequisite chain and learning path — no signup required.</p>
          </div>
          <div className="ph-feature">
            <div className="ph-feature-icon">
              <Zap size={32} />
            </div>
            <h3>2. AI Tutor</h3>
            <p>Stuck on a concept? Ask the AI tutor. It explains using the prerequisite chain, adapts to your child's level, and never skips foundations.</p>
          </div>
          <div className="ph-feature">
            <div className="ph-feature-icon">
              <BarChart3 size={32} />
            </div>
            <h3>3. Track Mastery</h3>
            <p>See exactly which micro-topics are mastered, which need work, and what's next. Weekly email reports keep you in the loop without micromanaging.</p>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="ph-section">
        <h2>Simple Pricing</h2>
        <div className="ph-pricing">
          <div className="ph-plan">
            <div className="ph-plan-name">Free</div>
            <div className="ph-plan-price">$0</div>
            <ul>
              <li><Check size={16} /> Unlimited assessments</li>
              <li><Check size={16} /> 1 learner</li>
              <li><Check size={16} /> 5 AI tutor sessions/day</li>
              <li><Check size={16} /> Basic progress tracking</li>
            </ul>
            <a href="https://app.obiomacare.com/assessment" className="ph-plan-btn">Get Started</a>
          </div>
          <div className="ph-plan ph-plan-popular">
            <div className="ph-plan-badge">Most Popular</div>
            <div className="ph-plan-name">Family</div>
            <div className="ph-plan-price">$12<span>/month</span></div>
            <ul>
              <li><Check size={16} /> Unlimited learners</li>
              <li><Check size={16} /> Unlimited AI tutor</li>
              <li><Check size={16} /> Weekly email reports</li>
              <li><Check size={16} /> Full mastery analytics</li>
              <li><Check size={16} /> Learning path generation</li>
            </ul>
            <a href="https://app.obiomacare.com/pricing" className="ph-plan-btn ph-plan-btn-primary">Start Free Trial</a>
          </div>
          <div className="ph-plan">
            <div className="ph-plan-name">Educator</div>
            <div className="ph-plan-price">$29<span>/month</span></div>
            <ul>
              <li><Check size={16} /> Everything in Family</li>
              <li><Check size={16} /> Up to 20 learners</li>
              <li><Check size={16} /> Bulk import/export</li>
              <li><Check size={16} /> Priority support</li>
            </ul>
            <a href="https://app.obiomacare.com/pricing" className="ph-plan-btn">Get Started</a>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="ph-section ph-alt">
        <h2>Built by a parent who needed this.</h2>
        <div className="ph-maker">
          <div className="ph-maker-avatar">N</div>
          <div className="ph-maker-info">
            <h3>Nnamdi Okorafor</h3>
            <p>15-year RN, homeschool dad, and founder of OBIO. Built this because I couldn't find a tool that told me exactly what my kids needed to learn next — so I mapped the entire K-5 curriculum prerequisite chain myself.</p>
            <div className="ph-maker-links">
              <a href="https://app.obiomacare.com" target="_blank" rel="noopener noreferrer">
                🌐 app.obiomacare.com
              </a>
              <a href="mailto:admin@obiomacare.com">
                ✉️ admin@obiomacare.com
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="ph-section ph-cta">
        <h2>Ready to stop guessing?</h2>
        <p>Get your child's free learning readiness assessment in 60 seconds.</p>
        <a href="https://app.obiomacare.com/assessment" className="ph-btn-primary ph-btn-large">
          Start Free Assessment →
        </a>
      </section>

      {/* Footer */}
      <footer className="ph-footer">
        <p>© 2026 OBIO. Built with ❤️ for parents everywhere.</p>
      </footer>
    </div>
  );
}
