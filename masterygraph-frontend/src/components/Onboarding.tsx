import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, Users, Search, GitBranch, ArrowRight, Check, Sparkles, X } from 'lucide-react';

interface OnboardingStep {
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: string;
  route?: string;
}

const steps: OnboardingStep[] = [
  {
    title: "Welcome to OBIO",
    description: "Prerequisite-aware learning paths for children ages 4-11. Let's get you set up in 3 quick steps.",
    icon: <Sparkles className="w-8 h-8 text-yellow-500" />,
  },
  {
    title: "Add Your First Learner",
    description: "Start by creating a profile for your child. We'll track their progress and find the right learning path.",
    icon: <Users className="w-8 h-8 text-blue-500" />,
    action: "Create Learner",
    route: "/learners",
  },
  {
    title: "Explore Topics",
    description: "Search our library of 1,590+ micro-topics. Find what your child wants to learn or where they're stuck.",
    icon: <Search className="w-8 h-8 text-green-500" />,
    action: "Browse Topics",
    route: "/topics",
  },
  {
    title: "Find Learning Paths",
    description: "Our graph engine finds the exact prerequisite chain. See every topic they need, in the right order.",
    icon: <GitBranch className="w-8 h-8 text-purple-500" />,
    action: "Try Path Finder",
    route: "/paths",
  },
  {
    title: "You're All Set",
    description: "You can always come back to the AI Tutor for help, run Gap Analysis to find missing foundations, and track progress in Analytics.",
    icon: <Brain className="w-8 h-8 text-blue-600" />,
    action: "Go to Dashboard",
    route: "/",
  },
];

const ONBOARDING_KEY = 'mg_onboarding_complete';

export function useOnboarding() {
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    const completed = localStorage.getItem(ONBOARDING_KEY);
    if (!completed) {
      setShowOnboarding(true);
    }
  }, []);

  const completeOnboarding = () => {
    localStorage.setItem(ONBOARDING_KEY, 'true');
    setShowOnboarding(false);
  };

  const resetOnboarding = () => {
    localStorage.removeItem(ONBOARDING_KEY);
    setShowOnboarding(true);
  };

  return { showOnboarding, completeOnboarding, resetOnboarding };
}

export default function OnboardingModal() {
  const [step, setStep] = useState(0);
  const navigate = useNavigate();
  const { completeOnboarding } = useOnboarding();

  const currentStep = steps[step];
  const isLast = step === steps.length - 1;

  const handleNext = () => {
    if (isLast) {
      completeOnboarding();
    } else {
      setStep(step + 1);
    }
  };

  const handleAction = () => {
    if (currentStep.route) {
      completeOnboarding();
      navigate(currentStep.route);
    }
  };

  const handleSkip = () => {
    completeOnboarding();
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-8 relative">
        <button
          onClick={handleSkip}
          className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-400" />
        </button>

        {/* Progress */}
        <div className="flex gap-2 mb-8">
          {steps.map((_, i) => (
            <div
              key={i}
              className={`h-2 flex-1 rounded-full transition-colors ${
                i <= step ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>

        {/* Content */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            {currentStep.icon}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{currentStep.title}</h2>
          <p className="text-gray-600">{currentStep.description}</p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          {currentStep.action && currentStep.route && (
            <button
              onClick={handleAction}
              className="flex-1 py-3 px-4 bg-blue-50 text-blue-700 rounded-xl font-semibold hover:bg-blue-100 transition-colors"
            >
              {currentStep.action}
            </button>
          )}
          <button
            onClick={handleNext}
            className="flex-1 py-3 px-4 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
          >
            {isLast ? (
              <>
                <Check className="w-5 h-5" />
                Get Started
              </>
            ) : (
              <>
                Next
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>

        {!isLast && (
          <button
            onClick={handleSkip}
            className="w-full mt-3 text-sm text-gray-400 hover:text-gray-600 transition-colors"
          >
            Skip tutorial
          </button>
        )}
      </div>
    </div>
  );
}
