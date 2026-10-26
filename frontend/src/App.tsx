import React, { useState } from 'react';
import { DashboardPage } from './pages/DashboardPage';
import { CasesPage } from './pages/CasesPage';
import { CaseWorkspacePage } from './pages/CaseWorkspacePage';
import { BenchmarkLab } from './components/BenchmarkLab';
import { RulesPage } from './pages/RulesPage';
import {
  ShieldCheck,
  LayoutDashboard,
  FolderOpen,
  BarChart2,
  Sliders,
  User,
  ExternalLink,
} from 'lucide-react';

export function App() {
  const [currentNav, setCurrentNav] = useState<'dashboard' | 'cases' | 'workspace' | 'benchmarks' | 'rules'>('dashboard');
  const [selectedCaseId, setSelectedCaseId] = useState<number | null>(1);
  const [currentRole, setCurrentRole] = useState<'admin' | 'reviewer'>('reviewer');

  const handleSelectCase = (id: number) => {
    setSelectedCaseId(id);
    setCurrentNav('workspace');
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col text-slate-900 font-sans">
      {/* Top Government-Grade Navy Header */}
      <header className="bg-slate-950 text-white border-b border-slate-800 sticky top-0 z-50 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo / Brand */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg text-white font-black text-lg tracking-wider">
                VT
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-base tracking-tight text-white">
                    VeriTrace
                  </span>
                  <span className="text-[10px] font-mono uppercase bg-blue-900 text-blue-200 px-1.5 py-0.5 rounded border border-blue-700">
                    SIH 2026 · PS 26261
                  </span>
                </div>
                <span className="text-[11px] text-slate-400 block -mt-0.5">
                  AI-Powered Application Validation Decision-Support
                </span>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="hidden md:flex items-center gap-1 text-xs font-semibold">
              <button
                onClick={() => setCurrentNav('dashboard')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg transition ${
                  currentNav === 'dashboard'
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-900'
                }`}
              >
                <LayoutDashboard size={15} />
                Dashboard
              </button>

              <button
                onClick={() => setCurrentNav('cases')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg transition ${
                  currentNav === 'cases' || currentNav === 'workspace'
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-900'
                }`}
              >
                <FolderOpen size={15} />
                Application Cases
              </button>

              <button
                onClick={() => setCurrentNav('benchmarks')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg transition ${
                  currentNav === 'benchmarks'
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-900'
                }`}
              >
                <BarChart2 size={15} />
                Honest Benchmark Lab
              </button>

              <button
                onClick={() => setCurrentNav('rules')}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg transition ${
                  currentNav === 'rules'
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-900'
                }`}
              >
                <Sliders size={15} />
                Rule Registry
              </button>
            </nav>

            {/* User Role Switcher for Live Demo convenience */}
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <span className="text-[10px] text-slate-400 block">Logged In As:</span>
                <span className="text-xs font-bold text-slate-200">
                  {currentRole === 'admin' ? 'Chief Scrutiny Officer' : 'Verification Reviewer'}
                </span>
              </div>

              <select
                value={currentRole}
                onChange={(e) => setCurrentRole(e.target.value as any)}
                className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
                title="Switch demo persona"
              >
                <option value="reviewer">Reviewer Role</option>
                <option value="admin">Admin Role</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {currentNav === 'dashboard' && (
          <DashboardPage
            onSelectCase={handleSelectCase}
            onNavigateToBenchmark={() => setCurrentNav('benchmarks')}
          />
        )}

        {currentNav === 'cases' && (
          <CasesPage onSelectCase={handleSelectCase} />
        )}

        {currentNav === 'workspace' && selectedCaseId && (
          <CaseWorkspacePage
            caseId={selectedCaseId}
            onBack={() => setCurrentNav('cases')}
          />
        )}

        {currentNav === 'benchmarks' && <BenchmarkLab />}

        {currentNav === 'rules' && <RulesPage />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap items-center justify-between gap-2">
          <span>VeriTrace: AI-Assisted Application Validation Platform · SIH 2026</span>
          <span className="font-mono text-[11px] bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
            Truth-State Architecture: Deterministic Rules · Anchored Claims · Immutable Audit Log
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
