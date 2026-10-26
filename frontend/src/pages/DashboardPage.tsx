import React, { useEffect, useState } from 'react';
import { api, DashboardSummary } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { ShieldCheck, FileText, AlertTriangle, Layers, Clock, ArrowRight, Play } from 'lucide-react';

interface DashboardPageProps {
  onSelectCase: (caseId: number) => void;
  onNavigateToBenchmark: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onSelectCase, onNavigateToBenchmark }) => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboardSummary();
      setSummary(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <p className="text-xs text-slate-500 mt-2 font-medium">Loading Scrutiny Dashboard...</p>
      </div>
    );
  }

  const truth = summary?.system_truth_states || {
    Consistent: 0,
    'Potential Inconsistency': 0,
    'Needs Human Review': 0,
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Synthetic Data & Decision Support Notice */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-xl p-6 shadow-md flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-800/80 border border-blue-700 text-[11px] font-semibold tracking-wider text-blue-200 uppercase mb-2">
            Decision-Support Scrutiny Platform · SIH 2026
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white">
            VeriTrace: AI-Powered Application Validation
          </h1>
          <p className="text-xs text-blue-200 mt-1 max-w-2xl leading-relaxed">
            Deterministic rule-based evidence anchoring for institutional application bundles.
            Surfaces cross-document contradictions with synchronized page-level bounding box highlights.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onSelectCase(1)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-400 text-white rounded-lg text-xs font-bold shadow transition"
          >
            Launch Demo Case (CASE-DEMO-01)
            <ArrowRight size={14} />
          </button>
        </div>
      </div>

      {/* Three-State Truth Model Bar */}
      <div>
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
          Three-State Truth Model Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-5 rounded-xl border border-emerald-200 shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-emerald-800">Consistent Checks</span>
              <div className="text-3xl font-black text-emerald-600 mt-1">{truth['Consistent']}</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Anchored claims agreeing across documents</p>
            </div>
            <StatusBadge status="consistent" size="sm" />
          </div>

          <div className="bg-white p-5 rounded-xl border border-amber-200 shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-amber-800">Potential Inconsistencies</span>
              <div className="text-3xl font-black text-amber-600 mt-1">{truth['Potential Inconsistency']}</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Discrepancies flagged for reviewer scrutiny</p>
            </div>
            <StatusBadge status="potential inconsistency" size="sm" />
          </div>

          <div className="bg-white p-5 rounded-xl border border-blue-200 shadow-sm flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-blue-800">Needs Human Review</span>
              <div className="text-3xl font-black text-blue-600 mt-1">{truth['Needs Human Review']}</div>
              <p className="text-[11px] text-slate-500 mt-0.5">Low-confidence or ambiguous date formats</p>
            </div>
            <StatusBadge status="needs human review" size="sm" />
          </div>
        </div>
      </div>

      {/* High-Level Numbers & Benchmark Quick Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-2">
            <FileText size={16} className="text-blue-600" />
            Applications & Documents Under Scrutiny
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-xs text-slate-500">Active Cases</span>
              <div className="text-2xl font-bold text-slate-900 mt-0.5">{summary?.total_cases || 0}</div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-xs text-slate-500">Total Ingested PDFs</span>
              <div className="text-2xl font-bold text-slate-900 mt-0.5">{summary?.total_documents || 0}</div>
            </div>
          </div>

          <div className="border-t border-slate-100 pt-3">
            <span className="text-xs font-semibold text-slate-700 block mb-2">Findings by Severity</span>
            <div className="flex items-center gap-2 flex-wrap">
              {Object.entries(summary?.findings_by_severity || {}).map(([sev, cnt]) => (
                <div key={sev} className="flex items-center gap-1.5 text-xs bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
                  <span className="font-semibold text-slate-700">{sev}:</span>
                  <span className="font-mono font-bold text-blue-700">{cnt}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Latest Benchmark Quick Card */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-2">
                <ShieldCheck size={16} className="text-emerald-600" />
                Latest Benchmark Evaluation Snapshot
              </h3>
              <span className="text-[11px] font-mono bg-amber-50 text-amber-800 px-2 py-0.5 rounded border border-amber-200">
                Synthetic Benchmark Lab
              </span>
            </div>

            {summary?.latest_benchmark ? (
              <div className="grid grid-cols-3 gap-4 my-2">
                <div className="bg-blue-50/60 border border-blue-200 p-3.5 rounded-lg text-center">
                  <span className="text-xs font-bold text-blue-800 uppercase">Precision</span>
                  <div className="text-2xl font-black text-blue-700 mt-1">
                    {(summary.latest_benchmark.precision * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-emerald-50/60 border border-emerald-200 p-3.5 rounded-lg text-center">
                  <span className="text-xs font-bold text-emerald-800 uppercase">Recall</span>
                  <div className="text-2xl font-black text-emerald-700 mt-1">
                    {(summary.latest_benchmark.recall * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="bg-indigo-50/60 border border-indigo-200 p-3.5 rounded-lg text-center">
                  <span className="text-xs font-bold text-indigo-800 uppercase">F1 Score</span>
                  <div className="text-2xl font-black text-indigo-700 mt-1">
                    {(summary.latest_benchmark.f1_score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500">No benchmark run completed yet.</p>
            )}
          </div>

          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Live evaluation on 12 test cases with negative examples and ambiguity checks.
            </span>
            <button
              onClick={onNavigateToBenchmark}
              className="text-xs font-bold text-blue-700 hover:text-blue-800 flex items-center gap-1"
            >
              Open Benchmark Lab <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Recent Scrutiny Activity */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-2 mb-3">
          <Clock size={16} className="text-blue-600" />
          Recent Scrutiny & Audit Activity
        </h3>

        <div className="divide-y divide-slate-100">
          {(summary?.recent_activity || []).slice(0, 5).map((act: any) => (
            <div key={act.id} className="py-2.5 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                <span className="font-mono font-bold text-slate-800 px-2 py-0.5 bg-slate-100 rounded text-[10px]">
                  {act.event_type}
                </span>
                <span className="text-slate-600">Case ID #{act.case_id}</span>
                <span className="text-slate-400 font-mono text-[11px] truncate max-w-md">
                  {JSON.stringify(act.payload)}
                </span>
              </div>
              <span className="text-slate-400 font-mono text-[11px]">
                {new Date(act.created_at).toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
