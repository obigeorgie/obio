import { Link } from "react-router-dom";
import { ArrowLeft, Heart, Clock, HelpCircle } from "lucide-react";

export default function PaymentCancel() {
  return (
    <div className="min-h-screen bg-[#faf9f7] flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* Icon */}
        <div className="w-20 h-20 rounded-full bg-[#f5f3ef] flex items-center justify-center mx-auto mb-6">
          <Clock className="w-10 h-10 text-[#a8a198]" />
        </div>

        <h1 className="text-2xl font-extrabold text-[#1f1c19] tracking-tight">
          No worries at all
        </h1>
        <p className="text-sm text-[#7c756d] mt-2 leading-relaxed">
          Your subscription wasn't started. You won't be charged. If you change your mind, we're here.
        </p>

        {/* What they're missing */}
        <div className="mt-8 bg-white rounded-2xl border border-[#e8e5df] p-5 text-left">
          <h3 className="text-sm font-bold text-[#1f1c19] mb-3 flex items-center gap-2">
            <Heart className="w-4 h-4 text-[#ef4444]" />
            What you're missing
          </h3>
          <ul className="space-y-2.5">
            <li className="flex items-start gap-3">
              <span className="text-[#6366f1] mt-0.5">✓</span>
              <span className="text-sm text-[#7c756d]">Personalized learning paths for every child based on their actual gaps, not grade levels</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-[#6366f1] mt-0.5">✓</span>
              <span className="text-sm text-[#7c756d]">AI tutor that explains concepts in age-appropriate language, available 24/7</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-[#6366f1] mt-0.5">✓</span>
              <span className="text-sm text-[#7c756d]">Gap analysis that finds the exact micro-topics blocking your child's progress</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-[#6366f1] mt-0.5">✓</span>
              <span className="text-sm text-[#7c756d]">Gamification: streaks, badges, and points that motivate kids to keep learning</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-[#6366f1] mt-0.5">✓</span>
              <span className="text-sm text-[#7c756d]">Multiple learners per account — perfect for families with 2+ kids</span>
            </li>
          </ul>
        </div>

        {/* Actions */}
        <div className="mt-6 space-y-3">
          <Link
            to="/pricing"
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#6366f1] text-white rounded-xl text-sm font-semibold hover:bg-[#4f46e5] transition-all shadow-sm hover:shadow-md w-full justify-center"
          >
            Back to Pricing
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <Link
            to="/assessment"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-[#6366f1] border border-[#d4cfc5] rounded-xl text-sm font-semibold hover:border-[#6366f1] transition-all w-full justify-center"
          >
            <HelpCircle className="w-4 h-4" />
            Try Free Assessment First
          </Link>
        </div>

        <p className="mt-6 text-xs text-[#a8a198]">
          Have questions?{" "}
          <a href="mailto:nnamdiokorafor@gmail.com" className="text-[#6366f1] hover:underline">
            Email us
          </a>
          {" "}or check out{" "}
          <Link to="/assessment" className="text-[#6366f1] hover:underline">
            the free assessment
          </Link>
          .
        </p>
      </div>
    </div>
  );
}
