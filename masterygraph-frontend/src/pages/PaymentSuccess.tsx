import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CheckCircle, Sparkles, ArrowRight, Star, BookOpen, Users, Zap } from "lucide-react";

export default function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [plan, setPlan] = useState<string>("");
  const [error, setError] = useState("");
  const sessionId = searchParams.get("session_id");

  useEffect(() => {
    // Verify the session with backend (optional but good practice)
    if (sessionId) {
      verifySession();
    } else {
      setLoading(false);
    }
  }, [sessionId]);

  async function verifySession() {
    try {
      // We could call backend to verify session_id, but for now just show success
      // In production, verify the session and get plan details
      setPlan("Family Plan"); // Default
    } catch (e: any) {
      setError("Could not verify payment. Please contact support.");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#faf9f7] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-3 border-[#6366f1] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-[#7c756d]">Confirming your subscription...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#faf9f7] flex items-center justify-center">
        <div className="text-center max-w-md px-4">
          <div className="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">⚠️</span>
          </div>
          <h1 className="text-xl font-bold text-[#1f1c19]">Something went wrong</h1>
          <p className="text-sm text-[#7c756d] mt-2">{error}</p>
          <Link
            to="/pricing"
            className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-[#6366f1] text-white rounded-xl text-sm font-semibold"
          >
            Back to Pricing
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#faf9f7] flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* Success animation */}
        <div className="relative mb-6">
          <div className="w-20 h-20 rounded-full bg-emerald-50 flex items-center justify-center mx-auto animate-bounce">
            <CheckCircle className="w-10 h-10 text-emerald-500" />
          </div>
          <div className="absolute -top-1 -right-1/4">
            <Sparkles className="w-5 h-5 text-[#f59e0b] animate-pulse" />
          </div>
          <div className="absolute -bottom-2 -left-1/4">
            <Star className="w-4 h-4 text-[#f59e0b] animate-pulse" style={{ animationDelay: "0.2s" }} />
          </div>
        </div>

        <h1 className="text-2xl font-extrabold text-[#1f1c19] tracking-tight">
          Welcome to MasteryGraph!
        </h1>
        <p className="text-sm text-[#7c756d] mt-2">
          Your subscription is active. You're ready to start building personalized learning paths.
        </p>

        {plan && (
          <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-[#6366f1]/10 text-[#6366f1] rounded-full text-sm font-semibold">
            <Star className="w-4 h-4" />
            {plan} Active
          </div>
        )}

        {/* Quick setup suggestions */}
        <div className="mt-8 space-y-3">
          <h3 className="text-xs font-bold text-[#a8a198] uppercase tracking-wider">Get Started</h3>
          
          <Link
            to="/learners"
            className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-[#e8e5df] hover:shadow-md transition-all group"
          >
            <div className="w-10 h-10 rounded-xl bg-[#6366f1]/10 flex items-center justify-center">
              <Users className="w-5 h-5 text-[#6366f1]" />
            </div>
            <div className="text-left flex-1">
              <div className="font-semibold text-[#1f1c19] text-sm">Add Your First Learner</div>
              <div className="text-xs text-[#a8a198]">Create a profile for your child</div>
            </div>
            <ArrowRight className="w-4 h-4 text-[#a8a198] group-hover:text-[#6366f1] transition-colors" />
          </Link>

          <Link
            to="/gaps"
            className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-[#e8e5df] hover:shadow-md transition-all group"
          >
            <div className="w-10 h-10 rounded-xl bg-[#10b981]/10 flex items-center justify-center">
              <Zap className="w-5 h-5 text-[#10b981]" />
            </div>
            <div className="text-left flex-1">
              <div className="font-semibold text-[#1f1c19] text-sm">Run a Gap Analysis</div>
              <div className="text-xs text-[#a8a198]">Find the exact prerequisites to master</div>
            </div>
            <ArrowRight className="w-4 h-4 text-[#a8a198] group-hover:text-[#10b981] transition-colors" />
          </Link>

          <Link
            to="/tutor"
            className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-[#e8e5df] hover:shadow-md transition-all group"
          >
            <div className="w-10 h-10 rounded-xl bg-[#f59e0b]/10 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-[#f59e0b]" />
            </div>
            <div className="text-left flex-1">
              <div className="font-semibold text-[#1f1c19] text-sm">Try the AI Tutor</div>
              <div className="text-xs text-[#a8a198]">Get explanations for any topic</div>
            </div>
            <ArrowRight className="w-4 h-4 text-[#a8a198] group-hover:text-[#f59e0b] transition-colors" />
          </Link>
        </div>

        <Link
          to="/"
          className="mt-8 inline-flex items-center gap-2 px-6 py-3 bg-[#6366f1] text-white rounded-xl text-sm font-semibold hover:bg-[#4f46e5] transition-all shadow-sm hover:shadow-md"
        >
          Go to Dashboard
          <ArrowRight className="w-4 h-4" />
        </Link>

        <p className="mt-6 text-xs text-[#a8a198]">
          Questions? Contact us at{" "}
          <a href="mailto:nnamdiokorafor@gmail.com" className="text-[#6366f1] hover:underline">
            nnamdiokorafor@gmail.com
          </a>
        </p>
      </div>
    </div>
  );
}
