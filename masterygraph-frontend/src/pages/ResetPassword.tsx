import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import { Brain, Check, Lock, Eye, EyeOff } from 'lucide-react';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      setError('Invalid or missing reset token.');
    }
  }, [token]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    
    setLoading(true);
    setError('');
    try {
      await api.resetPassword({ token, new_password: password });
      setSubmitted(true);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#faf9f7] px-4">
      <div className="max-w-[420px] w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2.5">
            <div className="relative w-10 h-10 flex items-center justify-center">
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[#6366f1] via-[#8b5cf6] to-[#a855f7] opacity-90" />
              <Brain className="relative w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
            <span className="text-xl font-extrabold tracking-tight text-[#1f1c19]">OBIO</span>
          </Link>
          <p className="text-[#7c756d] mt-2 text-sm">Set your new password</p>
        </div>

        <div className="bg-white rounded-2xl border border-[#e8e5df] p-8 shadow-sm">
          {submitted ? (
            <div className="text-center py-4 animate-fade-in">
              <div className="w-16 h-16 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Check className="w-8 h-8 text-emerald-500" />
              </div>
              <h2 className="text-lg font-bold text-[#1f1c19] mb-2">Password reset</h2>
              <p className="text-sm text-[#7c756d] mb-6">Your password has been updated successfully.</p>
              <Link
                to="/login"
                className="inline-flex items-center px-5 py-2.5 bg-[#6366f1] text-white rounded-xl text-sm font-semibold hover:bg-[#4f46e5] transition-colors"
              >
                Sign in
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-[#5c554f] mb-1.5">New password</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#a8a198]" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    className="w-full pl-10 pr-11 py-3 bg-white border border-[#e8e5df] rounded-xl text-sm text-[#1f1c19] placeholder-[#a8a198] focus:outline-none focus:border-[#6366f1] focus:ring-2 focus:ring-[#6366f1]/10 transition-all"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min 6 characters"
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
              <div>
                <label className="block text-sm font-medium text-[#5c554f] mb-1.5">Confirm password</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#a8a198]" />
                  <input
                    type={showConfirm ? 'text' : 'password'}
                    required
                    className="w-full pl-10 pr-11 py-3 bg-white border border-[#e8e5df] rounded-xl text-sm text-[#1f1c19] placeholder-[#a8a198] focus:outline-none focus:border-[#6366f1] focus:ring-2 focus:ring-[#6366f1]/10 transition-all"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm(!showConfirm)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#a8a198] hover:text-[#7c756d] transition-colors"
                  >
                    {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-100 rounded-xl p-3 text-sm text-red-600">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !token}
                className="w-full py-3 px-4 bg-[#6366f1] text-white rounded-xl font-semibold text-sm hover:bg-[#4f46e5] transition-all shadow-sm hover:shadow-md disabled:opacity-60"
              >
                {loading ? 'Resetting...' : 'Reset password'}
              </button>

              <Link
                to="/login"
                className="block text-center text-sm text-[#7c756d] hover:text-[#5c554f] transition-colors"
              >
                Back to login
              </Link>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
