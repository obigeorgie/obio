import { useState } from 'react';
import { getAuth } from '../lib/auth';
import { api } from '../api';
import { Check, X, Loader2, Sparkles, Zap, Crown } from 'lucide-react';

export default function Pricing() {
  const auth = getAuth();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState('');

  const handleCheckout = async (plan: string) => {
    if (!auth.isAuthenticated) {
      window.location.href = '/login?redirect=/pricing';
      return;
    }
    setLoading(plan);
    setError('');
    try {
      const res = await api.createCheckout({ plan });
      if (res?.checkout_url) {
        window.location.href = res.checkout_url;
      } else {
        setError('Unable to create checkout session');
      }
    } catch (err: any) {
      if (err.message?.includes('503') || err.message?.includes('not configured')) {
        setError('Payments are temporarily unavailable. Please try again later.');
      } else {
        setError(err.message || 'Something went wrong');
      }
    } finally {
      setLoading(null);
    }
  };

  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: '/month',
      description: 'Perfect for trying out OBIO',
      icon: Zap,
      iconBg: '#f5f3ef',
      iconColor: '#a8a198',
      features: [
        '1 learner profile',
        'Basic gap analysis',
        'Learning path viewer',
        'Topic search (1,590 topics)',
      ],
      cta: 'Get Started',
      plan: 'free',
      highlighted: false,
    },
    {
      name: 'Family',
      price: '$12',
      period: '/month',
      description: 'For parents with multiple children',
      icon: Crown,
      iconBg: '#fef3c7',
      iconColor: '#f59e0b',
      features: [
        'Unlimited learners',
        'Full analytics dashboard',
        'Advanced gap analysis',
        'Personalized learning plans',
        'Progress reports',
        'Email notifications',
      ],
      cta: 'Start Family Plan',
      plan: 'family',
      highlighted: true,
    },
    {
      name: 'Educator',
      price: '$29',
      period: '/month',
      description: 'For teachers and schools',
      icon: Sparkles,
      iconBg: '#eef2ff',
      iconColor: '#6366f1',
      features: [
        'Everything in Family',
        'Classroom management',
        'Standards alignment',
        'Bulk learner import',
        'Priority support',
        'API access',
      ],
      cta: 'Start Educator Plan',
      plan: 'educator',
      highlighted: false,
    },
  ];

  return (
    <div className="min-h-screen bg-[#faf9f7] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12 animate-fade-in-up">
          <h1 className="text-3xl font-extrabold text-[#1f1c19] tracking-tight mb-3">
            Simple, Transparent Pricing
          </h1>
          <p className="text-[#7c756d] max-w-xl mx-auto">
            Choose the plan that works for your family or classroom. No hidden fees. Cancel anytime.
          </p>
        </div>

        {error && (
          <div className="max-w-md mx-auto mb-8 bg-red-50 border border-red-100 rounded-xl p-4 flex items-center gap-3 animate-fade-in">
            <X className="w-5 h-5 text-red-500 flex-shrink-0" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-6">
          {plans.map((p, i) => (
            <div
              key={p.name}
              className={`rounded-2xl p-8 transition-all duration-300 animate-fade-in-up ${
                p.highlighted
                  ? 'bg-gradient-to-b from-[#6366f1] to-[#7c3aed] text-white shadow-xl ring-2 ring-[#6366f1]/20'
                  : 'bg-white text-[#1f1c19] border border-[#e8e5df] hover:shadow-lg hover:border-[#d4cfc5]'
              }`}
              style={{ animationDelay: `${i * 100}ms`, opacity: 0 }}
            >
              {p.highlighted && (
                <div className="inline-flex items-center gap-1 px-3 py-1 bg-white/20 rounded-full text-xs font-semibold mb-4">
                  <Sparkles className="w-3 h-3" />
                  Most Popular
                </div>
              )}

              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: p.highlighted ? 'rgba(255,255,255,0.15)' : p.iconBg }}
                >
                  <p.icon className="w-5 h-5" style={{ color: p.highlighted ? 'white' : p.iconColor }} />
                </div>
                <div>
                  <h3 className={`text-xl font-bold ${p.highlighted ? 'text-white' : 'text-[#1f1c19]'}`}>
                    {p.name}
                  </h3>
                </div>
              </div>

              <p className={`text-sm mb-4 ${p.highlighted ? 'text-white/70' : 'text-[#7c756d]'}`}>
                {p.description}
              </p>

              <div className="mb-6">
                <span className={`text-4xl font-extrabold ${p.highlighted ? 'text-white' : 'text-[#1f1c19]'}`}>
                  {p.price}
                </span>
                <span className={`text-base ${p.highlighted ? 'text-white/60' : 'text-[#a8a198]'}`}>
                  {p.period}
                </span>
              </div>

              <ul className="space-y-3 mb-8">
                {p.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <Check className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                      p.highlighted ? 'text-white/80' : 'text-emerald-500'
                    }`} />
                    <span className={`text-sm ${p.highlighted ? 'text-white/90' : 'text-[#5c554f]'}`}>
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleCheckout(p.plan)}
                disabled={loading === p.plan || p.plan === 'free'}
                className={`w-full py-3 px-4 rounded-xl font-semibold text-sm transition-all ${
                  p.plan === 'free'
                    ? 'bg-[#f5f3ef] text-[#a8a198] cursor-default'
                    : p.highlighted
                    ? 'bg-white text-[#6366f1] hover:bg-white/90 shadow-md'
                    : 'bg-[#6366f1] text-white hover:bg-[#4f46e5] shadow-sm hover:shadow-md'
                } ${loading === p.plan ? 'opacity-70' : ''}`}
              >
                {loading === p.plan ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Loading...
                  </span>
                ) : p.plan === 'free' ? (
                  'Current Plan'
                ) : (
                  p.cta
                )}
              </button>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center space-y-2">
          <p className="text-sm text-[#7c756d]">
            All paid plans include a 14-day free trial. No credit card required to start.
          </p>
          <p className="text-xs text-[#a8a198]">
            Questions? Contact us at admin@obiomacare.com
          </p>
        </div>
      </div>
    </div>
  );
}
