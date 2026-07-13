import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { getAuth } from "./lib/auth";
import Layout from "./components/Layout";
import OnboardingModal, { useOnboarding } from "./components/Onboarding";
import Dashboard from "./pages/Dashboard";
import Learners from "./pages/Learners";
import LearnerDetail from "./pages/LearnerDetail";
import TopicSearch from "./pages/TopicSearch";
import PathFinder from "./pages/PathFinder";
import GapAnalysis from "./pages/GapAnalysis";
import Analytics from "./pages/Analytics";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import AccountSettings from "./pages/AccountSettings";

import Pricing from "./pages/Pricing";
import Tutor from "./pages/Tutor";
import FreeAssessment from "./pages/Assessment";
import GrowthDashboard from "./pages/GrowthDashboard";
import ProductHuntLaunch from "./pages/ProductHunt";
import PaymentSuccess from "./pages/PaymentSuccess";
import PaymentCancel from "./pages/PaymentCancel";
import AdminDashboard from "./pages/AdminDashboard";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const auth = getAuth();
  if (!auth.isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function AppWithOnboarding() {
  const { showOnboarding } = useOnboarding();
  const auth = getAuth();
  
  return (
    <>
      {showOnboarding && auth.isAuthenticated && (
        <OnboardingModal />
      )}
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/payment/success" element={<PaymentSuccess />} />
        <Route path="/payment/cancel" element={<PaymentCancel />} />
        <Route path="/assessment" element={<FreeAssessment />} />
        <Route path="/assessment/:id" element={<FreeAssessment />} />
        <Route path="/producthunt" element={<ProductHuntLaunch />} />
        
        {/* Protected app routes */}
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="learners" element={<Learners />} />
          <Route path="learners/:id" element={<LearnerDetail />} />
          <Route path="topics" element={<TopicSearch />} />
          <Route path="paths" element={<PathFinder />} />
          <Route path="gaps" element={<GapAnalysis />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="tutor" element={<Tutor />} />
          <Route path="growth" element={<GrowthDashboard />} />
          <Route path="admin" element={<AdminDashboard />} />
          <Route path="account" element={<AccountSettings />} />
        </Route>
      </Routes>
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppWithOnboarding />
    </BrowserRouter>
  );
}

export default App;
