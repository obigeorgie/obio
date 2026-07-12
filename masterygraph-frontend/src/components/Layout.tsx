import { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from "react-router-dom";
import {
  Brain, Users, Search, GitBranch, AlertTriangle, BarChart3, LogOut,
  TrendingUp, Crown, Menu, X, Home, Settings,
  Sparkles, Zap
} from "lucide-react";
import { getAuth, clearAuth } from "../lib/auth";

const Logo = () => (
  <div className="flex items-center gap-2.5">
    <div className="relative w-9 h-9 flex items-center justify-center">
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[#6366f1] via-[#8b5cf6] to-[#a855f7] opacity-90" />
      <Brain className="relative w-5 h-5 text-white" strokeWidth={2.5} />
    </div>
    <span className="text-[19px] font-extrabold tracking-tight text-[#1f1c19]">OBIO</span>
  </div>
);

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const auth = getAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    clearAuth();
    navigate("/login");
  };

  const isFree = auth.user?.subscription?.plan === 'free' || !auth.user?.subscription;

  const navItems = [
    { to: "/", label: "Dashboard", icon: Home, color: "#6366f1" },
    { to: "/learners", label: "Learners", icon: Users, color: "#f59e0b" },
    { to: "/topics", label: "Topics", icon: Search, color: "#10b981" },
    { to: "/paths", label: "Paths", icon: GitBranch, color: "#8b5cf6" },
    { to: "/gaps", label: "Gaps", icon: AlertTriangle, color: "#ef4444" },
    { to: "/analytics", label: "Analytics", icon: BarChart3, color: "#06b6d4" },
    { to: "/growth", label: "Growth", icon: TrendingUp, color: "#10b981" },
    { to: "/tutor", label: "AI Tutor", icon: Sparkles, color: "#f59e0b" },
  ];

  if (isFree) {
    navItems.push({ to: "/pricing", label: "Upgrade", icon: Crown, color: "#f59e0b" });
  }

  const sidebarWidth = collapsed ? "w-[72px]" : "w-[240px]";

  return (
    <div className="min-h-screen flex bg-[#faf9f7]">
      {/* Desktop Sidebar */}
      <aside
        className={`hidden md:flex ${sidebarWidth} flex-col bg-white border-r border-[#e8e5df] transition-all duration-300 ease-in-out fixed h-screen z-30`}
      >
        {/* Logo */}
        <div className={`flex items-center h-[68px] px-4 ${collapsed ? 'justify-center' : ''}`}>
          {collapsed ? (
            <div className="relative w-9 h-9 flex items-center justify-center">
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[#6366f1] via-[#8b5cf6] to-[#a855f7] opacity-90" />
              <Brain className="relative w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
          ) : (
            <Logo />
          )}
        </div>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden md:flex absolute -right-3 top-[80px] w-6 h-6 bg-white border border-[#e8e5df] rounded-full items-center justify-center shadow-sm hover:shadow-md transition-shadow cursor-pointer z-40"
        >
          {collapsed ? <Zap className="w-3 h-3 text-[#6366f1]" /> : <Zap className="w-3 h-3 text-[#6366f1] rotate-180" />}
        </button>

        {/* Navigation */}
        <nav className="flex-1 px-3 pt-2 space-y-0.5 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = location.pathname === item.to ||
              (item.to !== "/" && location.pathname.startsWith(item.to));
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? "bg-[#6366f1]/10 text-[#4f46e5] font-semibold"
                    : "text-[#7c756d] hover:bg-[#f5f3ef] hover:text-[#5c554f]"
                }`}
                end={item.to === "/"}
                title={collapsed ? item.label : undefined}
              >
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200 ${
                    isActive
                      ? "bg-[#6366f1] text-white shadow-sm"
                      : "bg-[#f5f3ef] text-[#a8a198] group-hover:bg-white group-hover:text-[#7c756d]"
                  }`}
                >
                  <item.icon className="w-[18px] h-[18px]" strokeWidth={isActive ? 2.5 : 2} />
                </div>
                {!collapsed && (
                  <span className="text-sm tracking-[-0.01em]">{item.label}</span>
                )}
                {isActive && !collapsed && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[#6366f1]" />
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom section */}
        <div className="px-3 pb-4 space-y-1">
          <div className="border-t border-[#e8e5df] mx-1 mb-3" />

          <NavLink
            to="/account"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 ${
                isActive
                  ? "bg-[#6366f1]/10 text-[#4f46e5] font-semibold"
                  : "text-[#7c756d] hover:bg-[#f5f3ef] hover:text-[#5c554f]"
              }`
            }
            title={collapsed ? "Account" : undefined}
          >
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-[#f5f3ef] text-[#a8a198]">
              <Settings className="w-[18px] h-[18px]" />
            </div>
            {!collapsed && <span className="text-sm">Account</span>}
          </NavLink>

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 w-full rounded-xl text-[#7c756d] hover:bg-red-50 hover:text-red-600 transition-all duration-200 cursor-pointer"
            title={collapsed ? "Sign out" : undefined}
          >
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-[#f5f3ef] text-[#a8a198]">
              <LogOut className="w-[18px] h-[18px]" />
            </div>
            {!collapsed && <span className="text-sm">Sign out</span>}
          </button>

          {!collapsed && auth.user && (
            <div className="mt-3 px-3 py-3 bg-[#f5f3ef] rounded-xl">
              <p className="text-sm font-semibold text-[#3d3834] truncate">
                {auth.user.name || auth.user.email}
              </p>
              <div className="flex items-center gap-1.5 mt-1">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <p className="text-xs text-[#a8a198] capitalize">
                  {auth.user.role}
                  {auth.user.subscription?.plan && auth.user.subscription.plan !== 'free' && (
                    <span className="ml-1 text-[#6366f1] font-semibold">
                      • {auth.user.subscription.plan}
                    </span>
                  )}
                </p>
              </div>
            </div>
          )}

          {!collapsed && (
            <p className="text-[11px] text-[#a8a198] px-3 pt-2">
              OBIO Core v1.0
            </p>
          )}
        </div>
      </aside>

      {/* Desktop content margin */}
      <div className={`hidden md:block ${collapsed ? "w-[72px]" : "w-[240px]"} flex-shrink-0 transition-all duration-300`} />

      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-md border-b border-[#e8e5df] z-50 px-4 h-[60px] flex items-center justify-between">
        <Logo />
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 rounded-xl hover:bg-[#f5f3ef] transition-colors"
        >
          {mobileMenuOpen ? <X className="w-5 h-5 text-[#5c554f]" /> : <Menu className="w-5 h-5 text-[#5c554f]" />}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 bg-black/30 z-40 animate-fade-in">
          <div className="absolute top-[60px] left-0 right-0 bg-white border-b border-[#e8e5df] shadow-xl p-4 animate-fade-in-up">
            <nav className="space-y-1">
              {navItems.map((item) => {
                const isActive = location.pathname === item.to ||
                  (item.to !== "/" && location.pathname.startsWith(item.to));
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                      isActive
                        ? "bg-[#6366f1]/10 text-[#4f46e5] font-semibold"
                        : "text-[#7c756d] hover:bg-[#f5f3ef]"
                    }`}
                    end={item.to === "/"}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <div className={`flex items-center justify-center w-8 h-8 rounded-lg ${
                      isActive ? "bg-[#6366f1] text-white" : "bg-[#f5f3ef] text-[#a8a198]"
                    }`}>
                      <item.icon className="w-[18px] h-[18px]" />
                    </div>
                    <span className="text-sm">{item.label}</span>
                  </NavLink>
                );
              })}
              <NavLink
                to="/account"
                className="flex items-center gap-3 px-4 py-3 rounded-xl text-[#7c756d] hover:bg-[#f5f3ef]"
                onClick={() => setMobileMenuOpen(false)}
              >
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-[#f5f3ef] text-[#a8a198]">
                  <Settings className="w-[18px] h-[18px]" />
                </div>
                <span className="text-sm">Account</span>
              </NavLink>
            </nav>
            <div className="mt-4 pt-4 border-t border-[#e8e5df]">
              {auth.user && (
                <div className="px-2 mb-3">
                  <p className="text-sm font-medium text-[#3d3834]">{auth.user.name || auth.user.email}</p>
                  <p className="text-xs text-[#a8a198] capitalize">{auth.user.role}</p>
                </div>
              )}
              <button
                onClick={() => { setMobileMenuOpen(false); handleLogout(); }}
                className="flex items-center gap-3 px-4 py-3 w-full text-sm text-red-600 hover:bg-red-50 rounded-xl transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Sign out
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 min-h-screen overflow-auto pt-[60px] md:pt-0">
        <div className="p-4 md:p-8 pb-24 md:pb-8 max-w-[1400px] mx-auto">
          <Outlet />
        </div>
      </main>

      {/* Mobile Bottom Nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-[#e8e5df] z-50 flex justify-around items-center py-1.5 px-1">
        {[
          { to: "/", icon: Home, label: "Home" },
          { to: "/learners", icon: Users, label: "Learners" },
          { to: "/topics", icon: Search, label: "Topics" },
          { to: "/tutor", icon: Sparkles, label: "Tutor" },
          { to: "/analytics", icon: BarChart3, label: "Stats" },
        ].map((item) => {
          const isActive = location.pathname === item.to ||
            (item.to !== "/" && location.pathname.startsWith(item.to));
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={`flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl transition-all ${
                isActive ? 'text-[#6366f1]' : 'text-[#a8a198]'
              }`}
            >
              <item.icon className="w-[22px] h-[22px]" strokeWidth={isActive ? 2.5 : 1.5} />
              <span className="text-[10px] font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </div>
  );
}
