import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../api";
import { setAuth } from "../lib/auth";
import { Brain, Eye, EyeOff, ArrowRight, Mail, Lock } from "lucide-react";

const Logo = () => (
  <div className="flex items-center justify-center gap-2.5">
    <div className="relative w-10 h-10 flex items-center justify-center">
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[#6366f1] via-[#8b5cf6] to-[#a855f7] opacity-90" />
      <Brain className="relative w-5 h-5 text-white" strokeWidth={2.5} />
    </div>
    <span className="text-xl font-extrabold tracking-tight text-white">OBIO</span>
  </div>
);

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.login({ email, password });
      setAuth(res.token, res.user);
      navigate("/");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side — visual */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#6366f1] via-[#7c3aed] to-[#a855f7] relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
        <div className="relative z-10 flex flex-col justify-between p-12 text-white">
          <div>
            <Logo />
          </div>
          <div className="space-y-6">
            <h2 className="text-3xl font-bold leading-tight">
              Every child learns in a network, not a line.
            </h2>
            <p className="text-white/70 text-lg">
              Find the exact learning path through 1,590+ micro-topics for your child.
            </p>
            <div className="flex gap-8 pt-4">
              <div>
                <div className="text-2xl font-bold">1,590</div>
                <div className="text-white/60 text-sm">Topics</div>
              </div>
              <div>
                <div className="text-2xl font-bold">3,221</div>
                <div className="text-white/60 text-sm">Dependencies</div>
              </div>
              <div>
                <div className="text-2xl font-bold">7</div>
                <div className="text-white/60 text-sm">Curricula</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side — form */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12 bg-[#faf9f7]">
        <div className="w-full max-w-[420px] space-y-8">
          {/* Mobile logo */}
          <div className="lg:hidden flex justify-center">
            <Logo />
          </div>

          <div className="text-center lg:text-left">
            <h1 className="text-2xl font-bold text-[#1f1c19] tracking-tight">Welcome back</h1>
            <p className="text-sm text-[#7c756d] mt-1">
              Sign in to your OBIO account
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-50 border border-red-100 rounded-xl p-4 flex items-start gap-3 animate-fade-in">
                <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-red-500 text-xs font-bold">!</span>
                </div>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#5c554f] mb-1.5">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#a8a198]" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-white border border-[#e8e5df] rounded-xl text-sm text-[#1f1c19] placeholder-[#a8a198] focus:outline-none focus:border-[#6366f1] focus:ring-2 focus:ring-[#6366f1]/10 transition-all"
                    placeholder="you@example.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#5c554f] mb-1.5">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#a8a198]" />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-11 py-3 bg-white border border-[#e8e5df] rounded-xl text-sm text-[#1f1c19] placeholder-[#a8a198] focus:outline-none focus:border-[#6366f1] focus:ring-2 focus:ring-[#6366f1]/10 transition-all"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#a8a198] hover:text-[#7c756d] transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-[#d4cfc5] text-[#6366f1] focus:ring-[#6366f1]/20" />
                <span className="text-sm text-[#7c756d]">Remember me</span>
              </label>
              <Link to="/forgot-password" className="text-sm font-medium text-[#6366f1] hover:text-[#4f46e5] transition-colors">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-[#6366f1] text-white rounded-xl font-semibold text-sm hover:bg-[#4f46e5] transition-all shadow-sm hover:shadow-md disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Signing in...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Sign in
                  <ArrowRight className="w-4 h-4" />
                </span>
              )}
            </button>
          </form>

          <div className="text-center">
            <p className="text-sm text-[#7c756d]">
              Don't have an account?{" "}
              <Link to="/register" className="font-semibold text-[#6366f1] hover:text-[#4f46e5] transition-colors">
                Create one free
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
