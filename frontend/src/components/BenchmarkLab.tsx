import React, { useState, useEffect } from 'react';
import { api, BenchmarkRun } from '../api/client';
import { Play, CheckCircle2, AlertTriangle, ShieldAlert, Clock, RefreshCw, BarChart2 } from 'lucide-react';

export const BenchmarkLab: React.FC = () => {
  const [runs, setRuns] = useState<BenchmarkRun[]>([]);
  const [activeRun, setActiveRun] = useState<BenchmarkRun | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      const data = await api.getBenchmarks();
      setRuns(data);
      if (data.length > 0) {
        // Fetch detailed results for first run
        const detailed = await api.getBenchmarks();
        setActiveRun(detailed[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleTriggerRun = async () => {
    try {
      setRunning(true);
      const newRun = await api.runBenchmark();
      setRuns(prev => [newRun, ...prev]);
      setActiveRun(newRun);
    } catch (err) {
      alert(`Benchmark failed: ${err}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Permanent Honesty / Synthetic Data Banner */}
      <div className="bg-amber-500/10 border-2 border-amber-500/40 rounded-xl p-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-500/20 text-amber-700 rounded-lg">
            <AlertTriangle size={24} />
          </div>
          <div>
            <h4 className="text-sm font-bold text-amber-900 tracking-wide uppercase">
              Honest Benchmark Lab · Synthetic Data Caveat
            </h4>
            <p className="text-xs text-amber-800 mt-0.5">
              Metrics are evaluated on curated, labelled synthetic test cases (including negative examples and formatting stress tests).
              This demonstrates algorithmic false-alarm discipline and reproducibility, not production AICTE deployment claims.
            </p>
          </div>
        </div>

        <button
          onClick={handleTriggerRun}
          disabled={running}
          className="shrink-0 flex items-center gap-2 px-4 py-2.5 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-bold shadow-md transition disabled:opacity-50"
        >
          {running ? (
            <>
              <RefreshCw size={14} className="animate-spin" />
              Running Live Suite...
            </>
          ) : (
            <>
              <Play size={14} fill="currentColor" />
              Run Benchmark Now
            </>
          )}
        </button>
      </div>

      {activeRun && (
        <>
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Precision
              </span>
              <div className="text-3xl font-extrabold text-blue-700 mt-2">
                {(activeRun.precision * 100).toFixed(1)}%
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Discipline against false alarms
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Recall
              </span>
              <div className="text-3xl font-extrabold text-emerald-600 mt-2">
                {(activeRun.recall * 100).toFixed(1)}%
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Detection of planted defects
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                F1 Score
              </span>
              <div className="text-3xl font-extrabold text-indigo-700 mt-2">
                {(activeRun.f1_score * 100).toFixed(1)}%
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Harmonic balance of precision & recall
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Clock size={14} className="text-slate-400" />
                Execution Runtime
              </span>
              <div className="text-3xl font-extrabold text-slate-900 mt-2">
                {activeRun.duration_ms} <span className="text-sm font-normal text-slate-500">ms</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                {activeRun.total_cases} test cases evaluated live
              </p>
            </div>
          </div>

          {/* Confusion Counts Matrix */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2 mb-4">
              <BarChart2 size={16} className="text-blue-600" />
              Confusion Matrix & Error Analysis
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-200">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-emerald-800">True Positives (TP)</span>
                  <CheckCircle2 size={18} className="text-emerald-600" />
                </div>
                <div className="text-2xl font-black text-emerald-700 mt-2">{activeRun.tp_count}</div>
                <p className="text-[11px] text-emerald-700 mt-1">Planted defects correctly identified</p>
              </div>

              <div className="p-4 rounded-lg bg-amber-50 border border-amber-200">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-amber-800">False Positives (FP)</span>
                  <AlertTriangle size={18} className="text-amber-600" />
                </div>
                <div className="text-2xl font-black text-amber-700 mt-2">{activeRun.fp_count}</div>
                <p className="text-[11px] text-amber-700 mt-1">False alarms (kept intentionally low)</p>
              </div>

              <div className="p-4 rounded-lg bg-slate-100 border border-slate-200">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700">False Negatives (FN)</span>
                  <ShieldAlert size={18} className="text-slate-500" />
                </div>
                <div className="text-2xl font-black text-slate-700 mt-2">{activeRun.fn_count}</div>
                <p className="text-[11px] text-slate-600 mt-1">Undetected planted contradictions</p>
              </div>
            </div>
          </div>

          {/* Case by Case Breakdown */}
          {activeRun.case_results && activeRun.case_results.length > 0 && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 bg-slate-50 border-b border-slate-200">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Individual Benchmark Cases Breakdown
                </h4>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-100 text-slate-600 font-semibold border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-4">Case Key</th>
                      <th className="py-2.5 px-4">Expected Rules</th>
                      <th className="py-2.5 px-4">Detected Rules</th>
                      <th className="py-2.5 px-4 text-center">TP</th>
                      <th className="py-2.5 px-4 text-center">FP</th>
                      <th className="py-2.5 px-4 text-center">FN</th>
                      <th className="py-2.5 px-4 text-right">Runtime</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {activeRun.case_results.map((c, i) => (
                      <tr key={i} className="hover:bg-slate-50">
                        <td className="py-2.5 px-4 font-mono font-medium text-slate-800">{c.case_key}</td>
                        <td className="py-2.5 px-4">
                          {c.expected_rules.length > 0 ? (
                            c.expected_rules.map((r, idx) => (
                              <span key={idx} className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 mr-1">
                                {r}
                              </span>
                            ))
                          ) : (
                            <span className="text-slate-400 italic">None (Negative Example)</span>
                          )}
                        </td>
                        <td className="py-2.5 px-4">
                          {c.detected_rules.length > 0 ? (
                            c.detected_rules.map((r, idx) => (
                              <span key={idx} className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 mr-1">
                                {r}
                              </span>
                            ))
                          ) : (
                            <span className="text-slate-400 italic">None (Did not fire)</span>
                          )}
                        </td>
                        <td className="py-2.5 px-4 text-center font-bold text-emerald-600">{c.tp}</td>
                        <td className="py-2.5 px-4 text-center font-bold text-amber-600">{c.fp}</td>
                        <td className="py-2.5 px-4 text-center font-bold text-slate-500">{c.fn}</td>
                        <td className="py-2.5 px-4 text-right font-mono text-slate-500">{c.duration_ms} ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
