import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertCircle,
  CalendarClock,
  Check,
  FileText,
  GitCompareArrows,
  Play,
  RotateCcw,
  SlidersHorizontal,
} from 'lucide-react';
import {
  api,
  Case,
  DocumentItem,
  ExtractedField,
  ScenarioSimulation,
  SimulationFinding,
  ValidationRule,
} from '../api/client';
import { StatusBadge } from '../components/StatusBadge';

const isDateField = (field: ExtractedField) =>
  /date|valid_until|expiry/i.test(field.field_key);

const severityOrder = ['Critical', 'High', 'Medium', 'Low', 'Info'];

const FindingList: React.FC<{
  title: string;
  findings: SimulationFinding[];
  emptyText: string;
  tone: 'rose' | 'emerald';
}> = ({ title, findings, emptyText, tone }) => (
  <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <h3 className="mb-3 flex items-center justify-between gap-3 text-sm font-bold text-slate-900">
      {title}
      <span className={`rounded-full px-2 py-0.5 text-xs ${
        tone === 'rose' ? 'bg-rose-50 text-rose-700' : 'bg-emerald-50 text-emerald-700'
      }`}>
        {findings.length}
      </span>
    </h3>
    {findings.length === 0 ? (
      <p className="rounded-lg bg-slate-50 p-4 text-xs text-slate-500">{emptyText}</p>
    ) : (
      <div className="max-h-80 space-y-2 overflow-y-auto">
        {findings.map((finding, index) => (
          <article
            key={`${finding.rule_code}-${finding.title}-${index}`}
            className={`rounded-lg border p-3 ${
              tone === 'rose' ? 'border-rose-100 bg-rose-50/40' : 'border-emerald-100 bg-emerald-50/40'
            }`}
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-mono text-[10px] font-bold text-slate-700">
                {finding.rule_code}
              </span>
              <StatusBadge status={finding.severity} size="sm" />
            </div>
            <h4 className="mt-1 text-xs font-bold text-slate-900">{finding.title}</h4>
            <p className="mt-1 text-[11px] leading-relaxed text-slate-600">{finding.explanation}</p>
          </article>
        ))}
      </div>
    )}
  </section>
);

export const WhatIfSimulatorPage: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [rules, setRules] = useState<ValidationRule[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<number | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [fields, setFields] = useState<ExtractedField[]>([]);
  const [includedDocumentIds, setIncludedDocumentIds] = useState<Set<number>>(new Set());
  const [enabledRuleCodes, setEnabledRuleCodes] = useState<Set<string>>(new Set());
  const [reviewDate, setReviewDate] = useState('');
  const [fieldValues, setFieldValues] = useState<Record<number, string>>({});
  const [simulation, setSimulation] = useState<ScenarioSimulation | null>(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [caseLoading, setCaseLoading] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([api.getCases(), api.getRules()])
      .then(([caseData, ruleData]) => {
        if (!active) return;
        setCases(caseData);
        setRules(ruleData);
        const demoCase = caseData.find((caseItem) => caseItem.id === 1);
        setSelectedCaseId(demoCase?.id ?? caseData[0]?.id ?? null);
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : 'Unable to load simulator data.');
      })
      .finally(() => {
        if (active) setInitialLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (selectedCaseId === null) return;
    let active = true;
    setCaseLoading(true);
    setError(null);
    setSimulation(null);
    Promise.all([
      api.getCase(selectedCaseId),
      api.getDocuments(selectedCaseId),
      api.getFields(selectedCaseId),
    ])
      .then(([caseItem, documentData, fieldData]) => {
        if (!active) return;
        setDocuments(documentData);
        setFields(fieldData);
        setIncludedDocumentIds(new Set(documentData.map((document) => document.id)));
        setEnabledRuleCodes(new Set(rules.filter((rule) => rule.is_active).map((rule) => rule.rule_code)));
        setReviewDate(caseItem.review_date?.slice(0, 10) ?? '');
        setFieldValues(
          Object.fromEntries(
            fieldData
              .filter(isDateField)
              .map((field) => [field.id, field.normalized_value ?? '']),
          ),
        );
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : 'Unable to load this case.');
      })
      .finally(() => {
        if (active) setCaseLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedCaseId, rules]);

  const dateFields = useMemo(() => fields.filter(isDateField), [fields]);
  const selectedCase = cases.find((caseItem) => caseItem.id === selectedCaseId);

  const toggleRule = (ruleCode: string) => {
    setEnabledRuleCodes((current) => {
      const next = new Set(current);
      if (next.has(ruleCode)) next.delete(ruleCode);
      else next.add(ruleCode);
      return next;
    });
  };

  const toggleDocument = (documentId: number) => {
    setIncludedDocumentIds((current) => {
      const next = new Set(current);
      if (next.has(documentId)) next.delete(documentId);
      else next.add(documentId);
      return next;
    });
  };

  const runSimulation = async () => {
    if (selectedCaseId === null) return;
    try {
      setSimulating(true);
      setError(null);
      const result = await api.simulateCase(selectedCaseId, {
        enabled_rule_codes: [...enabledRuleCodes],
        excluded_document_ids: documents
          .filter((document) => !includedDocumentIds.has(document.id))
          .map((document) => document.id),
        ...(reviewDate ? { review_date: reviewDate } : {}),
        field_overrides: dateFields.flatMap((field) => {
          const value = fieldValues[field.id]?.trim();
          return includedDocumentIds.has(field.document_id) &&
            value &&
            value !== field.normalized_value
            ? [{ field_id: field.id, raw_value: value }]
            : [];
        }),
      });
      setSimulation(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed.');
      setSimulation(null);
    } finally {
      setSimulating(false);
    }
  };

  const resetScenario = () => {
    if (!selectedCase) return;
    setIncludedDocumentIds(new Set(documents.map((document) => document.id)));
    setEnabledRuleCodes(new Set(rules.filter((rule) => rule.is_active).map((rule) => rule.rule_code)));
    setReviewDate(selectedCase.review_date?.slice(0, 10) ?? '');
    setFieldValues(
      Object.fromEntries(
        dateFields.map((field) => [field.id, field.normalized_value ?? '']),
      ),
    );
    setSimulation(null);
    setError(null);
  };

  const renderSeverityBreakdown = (counts: Record<string, number>) => (
    <div className="mt-3 flex flex-wrap gap-2">
      {severityOrder.filter((severity) => counts[severity]).map((severity) => (
        <span key={severity} className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-600">
          {severity}: {counts[severity]}
        </span>
      ))}
      {Object.keys(counts).length === 0 && (
        <span className="text-[11px] text-slate-400">No findings</span>
      )}
    </div>
  );

  if (initialLoading) {
    return <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-sm text-slate-500">Loading simulator...</div>;
  }

  if (cases.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
        <FileText size={32} className="mx-auto mb-2 text-slate-400" />
        <p className="font-semibold text-slate-800">Create a case and add documents to simulate scenarios.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-bold text-slate-900">
            <GitCompareArrows size={22} className="text-blue-700" />
            What-if Scenario Simulator
          </h1>
          <p className="mt-1 max-w-3xl text-xs leading-relaxed text-slate-600">
            Try alternate rule settings, review dates, extracted dates, and document bundles. Results are
            compared with the current case using the deterministic rule engine.
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-[11px] font-semibold text-blue-800">
          <Check size={13} /> Preview only · nothing is saved
        </span>
      </header>

      {error && (
        <div role="alert" className="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      <section className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <div className="space-y-5 xl:col-span-2">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <label htmlFor="simulation-case" className="mb-2 block text-xs font-bold uppercase tracking-wide text-slate-500">
              Application case
            </label>
            <select
              id="simulation-case"
              value={selectedCaseId ?? ''}
              onChange={(event) => setSelectedCaseId(Number(event.target.value))}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {cases.map((caseItem) => (
                <option key={caseItem.id} value={caseItem.id}>
                  {caseItem.case_number} · {caseItem.institution_name}
                </option>
              ))}
            </select>

            <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="rounded-lg border border-slate-200 p-4">
                <h2 className="mb-3 flex items-center gap-2 text-xs font-bold text-slate-800">
                  <CalendarClock size={15} className="text-blue-600" />
                  Scenario review date
                </h2>
                <input
                  type="date"
                  aria-label="Scenario review date"
                  value={reviewDate}
                  onChange={(event) => setReviewDate(event.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-xs text-slate-700"
                />
                <p className="mt-2 text-[10px] text-slate-500">
                  {reviewDate ? `Compare expiry checks as of ${reviewDate}.` : 'No date override; use the case review date.'}
                </p>
              </div>

              <div className="rounded-lg border border-slate-200 p-4">
                <h2 className="mb-3 flex items-center gap-2 text-xs font-bold text-slate-800">
                  <FileText size={15} className="text-blue-600" />
                  Documents in scenario
                </h2>
                <div className="max-h-32 space-y-2 overflow-y-auto">
                  {documents.map((document) => (
                    <label key={document.id} className="flex cursor-pointer items-start gap-2 text-[11px] text-slate-700">
                      <input
                        type="checkbox"
                        checked={includedDocumentIds.has(document.id)}
                        onChange={() => toggleDocument(document.id)}
                        className="mt-0.5 accent-blue-700"
                      />
                      <span className="min-w-0">
                        <span className="block truncate font-medium">{document.original_filename}</span>
                        <span className="text-[10px] text-slate-400">{document.doc_type}</span>
                      </span>
                    </label>
                  ))}
                  {documents.length === 0 && <p className="text-[11px] text-slate-400">No documents uploaded.</p>}
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="mb-1 flex items-center gap-2 text-sm font-bold text-slate-900">
              <CalendarClock size={16} className="text-violet-600" />
              Hypothetical extracted date values
            </h2>
            <p className="mb-4 text-[11px] text-slate-500">
              Change a date claim for this run only. The original extracted values remain untouched.
            </p>
            {dateFields.length === 0 ? (
              <p className="rounded-lg bg-slate-50 p-3 text-xs text-slate-500">This case has no date fields to override.</p>
            ) : (
              <div className="space-y-2">
                {dateFields.map((field) => {
                  const document = documents.find((item) => item.id === field.document_id);
                  return (
                    <label key={field.id} className="grid grid-cols-1 items-center gap-2 rounded-lg border border-slate-100 p-3 sm:grid-cols-[1fr_180px]">
                      <span className="min-w-0">
                        <span className="block text-xs font-semibold text-slate-800">
                          {field.field_key.replaceAll('_', ' ')}
                        </span>
                        <span className="block truncate text-[10px] text-slate-500">
                          {document?.original_filename ?? `Document #${field.document_id}`} · current: {field.raw_value}
                        </span>
                      </span>
                      <input
                        type="date"
                        aria-label={`Scenario value for ${field.field_key} from ${document?.original_filename ?? 'document'}`}
                        value={fieldValues[field.id] ?? ''}
                        onChange={(event) => setFieldValues((current) => ({
                          ...current,
                          [field.id]: event.target.value,
                        }))}
                        className="rounded-lg border border-slate-300 px-2.5 py-2 text-xs"
                      />
                    </label>
                  );
                })}
              </div>
            )}
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="mb-1 flex items-center gap-2 text-sm font-bold text-slate-900">
              <SlidersHorizontal size={16} className="text-blue-600" />
              Rule switches
            </h2>
            <p className="mb-4 text-[11px] text-slate-500">
              Enable or disable rules for the hypothetical run without changing the rule registry.
            </p>
            {rules.length === 0 ? (
              <p className="text-xs text-slate-500">No rules are registered.</p>
            ) : (
              <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                {rules.map((rule) => (
                  <label key={rule.rule_code} className="flex cursor-pointer items-start gap-2 rounded-lg border border-slate-100 p-3 hover:bg-slate-50">
                    <input
                      type="checkbox"
                      checked={enabledRuleCodes.has(rule.rule_code)}
                      onChange={() => toggleRule(rule.rule_code)}
                      className="mt-0.5 accent-blue-700"
                    />
                    <span className="min-w-0">
                      <span className="block font-mono text-[10px] font-bold text-blue-800">
                        {rule.rule_code}
                      </span>
                      <span className="block text-[11px] text-slate-600">{rule.name}</span>
                    </span>
                  </label>
                ))}
              </div>
            )}
          </div>
        </div>

        <aside className="h-fit rounded-xl border border-blue-100 bg-blue-50/60 p-5">
          <h2 className="text-sm font-bold text-slate-900">Run scenario</h2>
          <p className="mt-1 text-[11px] leading-relaxed text-slate-600">
            Compare the current case’s active rules and full document bundle with the settings on the left.
          </p>
          <div className="mt-4 space-y-2 text-[11px] text-slate-600">
            <p><strong className="text-slate-800">{includedDocumentIds.size}</strong> of {documents.length} documents included</p>
            <p><strong className="text-slate-800">{enabledRuleCodes.size}</strong> rules enabled</p>
            <p><strong className="text-slate-800">{dateFields.filter((field) => includedDocumentIds.has(field.document_id) && fieldValues[field.id] && fieldValues[field.id] !== field.normalized_value).length}</strong> date values changed</p>
          </div>
          <button
            type="button"
            onClick={() => void runSimulation()}
            disabled={simulating || caseLoading || selectedCaseId === null}
            className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-700 px-4 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Play size={14} fill="currentColor" />
            {simulating ? 'Simulating…' : 'Run What-if Simulation'}
          </button>
          <button
            type="button"
            onClick={resetScenario}
            disabled={caseLoading}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            <RotateCcw size={13} />
            Reset to current case
          </button>
          {caseLoading && <p className="mt-3 text-center text-[10px] text-slate-500">Loading case data…</p>}
        </aside>
      </section>

      {simulation && (
        <section aria-live="polite" className="space-y-5">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {[
              { title: 'Current case baseline', result: simulation.baseline },
              { title: 'What-if scenario', result: simulation.scenario },
            ].map(({ title, result }) => (
              <article key={title} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <h2 className="text-xs font-bold uppercase tracking-wide text-slate-500">{title}</h2>
                <div className="mt-2 flex items-end gap-2">
                  <span className="text-3xl font-black text-slate-900">{result.finding_count}</span>
                  <span className="pb-1 text-xs text-slate-500">findings</span>
                </div>
                <p className="mt-1 text-[11px] text-slate-500">
                  {result.included_document_count} documents · {result.enabled_rule_codes.length} rules
                  {result.review_date ? ` · review date ${result.review_date}` : ''}
                </p>
                {renderSeverityBreakdown(result.findings_by_severity)}
              </article>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            <FindingList
              title="New in scenario"
              findings={simulation.added_findings}
              emptyText="No new findings compared with the current case."
              tone="rose"
            />
            <FindingList
              title="No longer flagged in scenario"
              findings={simulation.resolved_findings}
              emptyText="No baseline findings were removed by this scenario."
              tone="emerald"
            />
          </div>
          <p className="text-center text-[10px] text-slate-400">
            Simulation results are temporary decision-support previews; they do not update case documents,
            findings, audit history, or global rule settings.
          </p>
        </section>
      )}
    </div>
  );
};
