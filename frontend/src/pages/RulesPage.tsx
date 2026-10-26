import React, { useEffect, useState } from 'react';
import { api, ValidationRule } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { ShieldCheck, ToggleLeft, ToggleRight, Info } from 'lucide-react';

export const RulesPage: React.FC = () => {
  const [rules, setRules] = useState<ValidationRule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      setLoading(true);
      const data = await api.getRules();
      setRules(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleRuleActive = async (rule: ValidationRule) => {
    try {
      const updated = await api.updateRule(rule.id, { is_active: !rule.is_active });
      setRules(rules.map((r) => (r.id === updated.id ? updated : r)));
    } catch (err: any) {
      alert(`Update failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck size={22} className="text-blue-700" />
            Deterministic Validation Rule Registry
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Rules are versioned as code. Every finding references the exact Rule ID and Version executed.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-500">Loading rules...</div>
        ) : (
          <div className="divide-y divide-slate-100">
            {rules.map((r) => (
              <div key={r.id} className="p-5 flex flex-wrap items-center justify-between gap-4 hover:bg-slate-50">
                <div className="space-y-1 max-w-2xl">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-blue-900 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                      {r.rule_code}
                    </span>
                    <span className="font-mono text-xs text-slate-500">v{r.version}</span>
                    <StatusBadge status={r.severity} size="sm" />
                  </div>
                  <h3 className="text-sm font-bold text-slate-900">{r.name}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{r.description}</p>
                </div>

                <div className="flex items-center gap-4">
                  <span className={`text-xs font-bold ${r.is_active ? 'text-emerald-700' : 'text-slate-400'}`}>
                    {r.is_active ? 'ACTIVE' : 'DISABLED'}
                  </span>
                  <button
                    onClick={() => toggleRuleActive(r)}
                    className="text-slate-400 hover:text-blue-600 transition"
                    title={r.is_active ? 'Disable rule' : 'Enable rule'}
                  >
                    {r.is_active ? (
                      <ToggleRight size={32} className="text-blue-600" />
                    ) : (
                      <ToggleLeft size={32} className="text-slate-300" />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="p-4 bg-slate-100 rounded-xl border border-slate-200 text-xs text-slate-600 flex items-start gap-2.5">
        <Info size={16} className="text-slate-500 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-800">Rule Immutability Guarantee: </span>
          When rules are modified or re-versioned, past scrutiny findings retain their original Rule ID and Version for historical audit compliance.
        </div>
      </div>
    </div>
  );
};
