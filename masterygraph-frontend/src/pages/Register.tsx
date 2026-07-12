import { useState, useCallback } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../api";
import { setAuth } from "../lib/auth";
import { Brain, Eye, EyeOff, ArrowRight, Mail, Lock, User, Check, X, AlertCircle } from "lucide-react";

const Logo = () => (
  <div className="flex items-center justify-center gap-2.5">
    <div className="relative w-10 h-10 flex items-center justify-center">
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[#6366f1] via-[#8b5cf6] to-[#a855f7] opacity-90" />
      <Brain className="relative w-5 h-5 text-white" strokeWidth={2.5} />
    </div>
    <span className="text-xl font-extrabold tracking-tight text-white">OBIO</span>
  </div>
);

interface FieldErrors {
  name?: string;
  email?: string;
  password?: string;
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function getPasswordStrength(password: string): { score: number; label: string; color: string } {
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;

  const levels = [
    { label: "Too weak", color: "#ef4444" },
    { label: "Weak", color: "#f97316" },
    { label: "Fair", color: "#eab308" },
    { label: "Good", color: "#22c55e" },
    { label: "Strong", color: "#16a34a" },
  ];
  return { score, ...levels[Math.min(score, 4)] };
}

export default function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [success, setSuccess] = useState(false);

  const validateField = useCallback((field: string, value: string): string | undefined => {
    switch (field) {
      case "name":
        if (!value.trim()) return "Name is required";
        if (value.trim().length < 2) return "Name must be at least 2 characters";
        return undefined;
      case "email":
        if (!value.trim()) return "Email is required";
        if (!validateEmail(value)) return "Please enter a valid email address";
        return undefined;
      case "password":
        if (!value) return "Password is required";
        if (value.length < 8) return "Password must be at least 8 characters";
        return undefined;
      default:
        return undefined;
    }
  }, []);

  const handleBlur = (field: string) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    const value = field === "name" ? name : field === "email" ? email : password;
    const error = validateField(field, value);
    setFieldErrors((prev) => ({ ...prev, [field]: error }));
  };

  const handleChange = (field: string, value: string) => {
    if (field === "name") setName(value);
    if (field === "email") setEmail(value);
    if (field === "password") setPassword(value);

    if (touched[field]) {
      const error = validateField(field, value);
      setFieldErrors((prev) => ({ ...prev, [field]: error }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate all fields
    const errors: FieldErrors = {
      name: validateField("name", name),
      email: validateField("email", email),
      password: validateField("password", password),
    };
    setFieldErrors(errors);
    setTouched({ name: true, email: true, password: true });

    if (errors.name || errors.email || errors.password) {
      return;
    }

    setLoading(true);
    try {
      const res = await api.register({ email, password, name });
      if (res.success) {
        const loginRes = await api.login({ email, password });
        setAuth(loginRes.token, loginRes.user);
        setSuccess(true);
        setTimeout(() => navigate("/"), 1500);
      }
    } catch (err: any) {
      const msg = err.message || "Registration failed";
      if (msg.includes("already registered") || msg.includes("already exists")) {
        setFieldErrors((prev) => ({ ...prev, email: "This email is already registered" }));
      } else if (msg.includes("password") || msg.includes("Password")) {
        setFieldErrors((prev) => ({ ...prev, password: msg }));
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const passwordStrength = getPasswordStrength(password);

  const inputClass = (field: string) => {
    const hasError = fieldErrors[field as keyof FieldErrors] && touched[field];
    return `w-full pl-10 pr-4 py-3 bg-white border rounded-xl text-sm text-[#1f1c19] placeholder-[#a8a198] focus:outline-none focus:ring-2 transition-all ${
      hasError
        ? "border-red-300 focus:border-red-400 focus:ring-red-100"
        : "border-[#e8e5df] focus:border-[#6366f1] focus:ring-[#6366f1]/10"
    }`;
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#faf9f7] p-6">
        <div className="text-center space-y-6 max-w-md">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto">
            <Check className="w-8 h-8 text-emerald-600" />
          </div>
          <h1 className="text-2xl font-bold text-[#1f1c19]">Account created!</h1>
          <p className="text-[#7c756d]">Welcome to OBIO. Redirecting to your dashboard...</p>
        </div>
      </div>
    );
  }

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
              Start your child's mastery journey today.
            </h2>
            <p className="text-white/70 text-lg">
              Join parents using graph intelligence to find the exact learning path for their children.
            </p>
            <div className="flex gap-3 pt-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <svg key={i} className="w-5 h-5 text-amber-300" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
              <span className="text-white/80 text-sm ml-1">Trusted by parents worldwide</span>
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
            <h1 className="text-2xl font-bold text-[#1f1c19] tracking-tight">Create your account</h1>
            <p className="text-sm text-[#7c756d] mt-1">
              Free forever. No credit card required.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5" noValidate>
            {error && (
              <div className="bg-red-50 border border-red-100 rounded-xl p-4 flex items-start gap-3 animate-fade-in">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#5c554f] mb-1.5">
                  Full name <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#a8a198]" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => handleChange("name", e.target.value)}
                    onBlur={() => handleBlur("name")}
                    className={inputClass("name")}
                    placeholder="Your name"
                  />
                </div>
                {fieldErrors.name && touched.name && (
                  <p className="text-xs text-red-500 mt-1.5 flex items-center gap-1">
                    <X className="w-3 h-3" /> {fieldErrors.name}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-[#5c554f] mb-1.5">
                  Email <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#a8a198]" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => handleChange("email", e.target.value)}
                    onBlur={() => handleBlur("email")}
                    className={inputClass("email")}
                    placeholder="you@example.com"
                  />
                </div>
                {fieldErrors.email && touched.email && (
                  <p className="text-xs text-red-500 mt-1.5 flex items-center gap-1">
                    <X className="w-3 h-3" /> {fieldErrors.email}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-[#5c554f] mb-1.5">
                  Password <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#a8a198]" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => handleChange("password", e.target.value)}
                    onBlur={() => handleBlur("password")}
                    className={inputClass("password") + " pr-11"}
                    placeholder="Min. 8 characters"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#a8a198] hover:text-[#7c756d] transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {fieldErrors.password && touched.password && (
                  <p className="text-xs text-red-500 mt-1.5 flex items-center gap-1">
                    <X className="w-3 h-3" /> {fieldErrors.password}
                  </p>
                )}

                {/* Password strength meter */}
                {password.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <div className="flex gap-1.5">
                      {[1, 2, 3, 4].map((i) => (
                        <div
                          key={i}
                          className="h-1.5 flex-1 rounded-full transition-all"
                          style={{
                            backgroundColor: i <= passwordStrength.score ? passwordStrength.color : "#e8e5df",
                          }}
                        />
                      ))}
                    </div>
                    <p className="text-xs" style={{ color: passwordStrength.color }}>
                      {passwordStrength.label}
                    </p>
                    <div className="flex flex-wrap gap-x-4 gap-y-1">
                      {[
                        { label: "8+ chars", met: password.length >= 8 },
                        { label: "Uppercase", met: /[A-Z]/.test(password) },
                        { label: "Number", met: /[0-9]/.test(password) },
                        { label: "Special char", met: /[^A-Za-z0-9]/.test(password) },
                      ].map((req) => (
                        <span
                          key={req.label}
                          className={`text-xs flex items-center gap-1 ${req.met ? "text-emerald-600" : "text-[#a8a198]"}`}
                        >
                          {req.met ? <Check className="w-3 h-3" /> : <span className="w-3 h-3 rounded-full border border-current" />}
                          {req.label}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
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
                  Creating account...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Create account
                  <ArrowRight className="w-4 h-4" />
                </span>
              )}
            </button>

            <p className="text-xs text-center text-[#a8a198]">
              By creating an account, you agree to our Terms of Service and Privacy Policy.
            </p>
          </form>

          <div className="text-center">
            <p className="text-sm text-[#7c756d]">
              Already have an account?{" "}
              <Link to="/login" className="font-semibold text-[#6366f1] hover:text-[#4f46e5] transition-colors">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
