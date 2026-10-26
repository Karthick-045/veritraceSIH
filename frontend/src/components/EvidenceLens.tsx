import React, { useState } from 'react';
import { Finding, EvidenceItem } from '../api/client';
import { StatusBadge } from './StatusBadge';
import { FileText, ArrowRightLeft, ShieldCheck, CheckCircle2, XCircle, AlertCircle, Sparkles } from 'lucide-react';

interface EvidenceLensProps {
  finding: Finding;
  onReview: (decision: string, comment: string) => Promise<void>;
}

export const EvidenceLens: React.FC<EvidenceLensProps> = ({ finding, onReview }) => {
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [clarificationDraft, setClarificationDraft] = useState<string | null>(null);

  const evA = finding.evidence_items[0];
  const evB = finding.evidence_items[1] || finding.evidence_items[0];

  const handleAction = async (decision: string) => {
    if (!comment.trim()) {
      alert('A review comment is mandatory to maintain the immutable audit trail.');
      return;
    }
    setSubmitting(true);
    try {
      await onReview(decision, comment);
      setComment('');
    } finally {
      setSubmitting(false);
    }
  };

  const generateClarificationDraft = () => {
    const text = `To,\nThe Authorized Representative,\nReference: Application Inconsistency Scrutiny - Rule [${finding.rule_code} v${finding.rule_version}]\n\nDuring routine automated validation of your application documents, the following discrepancy was noted:\n\n• Discrepancy: ${finding.title}\n• Details: ${finding.explanation}\n• Source Evidence 1: ${evA.document_name} (Page ${evA.page_number}) indicates "${evA.raw_value}".\n${evB !== evA ? `• Source Evidence 2: ${evB.document_name} (Page ${evB.page_number}) indicates "${evB.raw_value}".\n` : ''}\nPlease provide necessary documentary clarification or amended certificates within 7 working days to resume institutional processing.\n\nOffice of Verification Scrutiny\nGovernment Application Scrutiny Directorate`;
    setClarificationDraft(text);
  };

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
      {/* Header Bar */}
      <div className="bg-slate-900 text-white p-4 flex flex-wrap items-center justify-between gap-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs px-2.5 py-1 bg-blue-950 text-blue-300 rounded border border-blue-800">
              {finding.rule_code} v{finding.rule_version}
            </span>
            <StatusBadge status={finding.severity} size="sm" />
            <StatusBadge status="Potential inconsistency" size="sm" />
          </div>
          <h2 className="text-lg font-bold mt-1 text-slate-50">{finding.title}</h2>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={generateClarificationDraft}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <Sparkles size={14} className="text-amber-400" />
            Generate Clarification Draft
          </button>
        </div>
      </div>

      {/* Signature Split View: Evidence Lens */}
      <div className="p-4 bg-slate-100 border-b border-slate-200">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <ArrowRightLeft size={14} className="text-blue-600" />
            Evidence Lens: Anchored Bounding Box Comparison
          </span>
          <span className="text-xs text-slate-500">
            Current Review Status: <span className="font-semibold text-slate-700 uppercase">{finding.reviewer_status}</span>
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative">
          {/* Connecting bridge badge */}
          <div className="hidden md:flex absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 bg-rose-600 text-white rounded-full p-2.5 shadow-lg border-2 border-white items-center justify-center">
            <ArrowRightLeft size={18} />
          </div>

          {/* Left Side: Source A */}
          <div className="bg-white rounded-lg border border-slate-200 p-3 shadow-sm flex flex-col">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 text-xs">
              <span className="font-semibold text-slate-700 flex items-center gap-1.5">
                <FileText size={14} className="text-blue-600" />
                {evA.document_name}
              </span>
              <span className="text-slate-500 font-mono">Page {evA.page_number}</span>
            </div>

            <div className="relative bg-slate-50 rounded border border-slate-200 h-80 overflow-hidden flex items-center justify-center group">
              <img
                src={`/api/documents/${evA.document_id}/pages/${evA.page_number}/image`}
                alt="Document Source A"
                className="max-h-full max-w-full object-contain"
                onError={(e) => {
                  (e.target as HTMLElement).style.display = 'none';
                }}
              />

              {/* Bounding Box Highlight Overlay */}
              {evA.bbox && (
                <div
                  className="absolute border-2 border-rose-500 bg-rose-500/15 pulsing-highlight pointer-events-none rounded transition"
                  style={{
                    left: `${evA.bbox.x0 * 100}%`,
                    top: `${evA.bbox.y0 * 100}%`,
                    width: `${(evA.bbox.x1 - evA.bbox.x0) * 100}%`,
                    height: `${(evA.bbox.y1 - evA.bbox.y0) * 100}%`,
                  }}
                >
                  <span className="absolute -top-5 left-0 text-[10px] bg-rose-600 text-white px-1.5 py-0.2 rounded font-mono shadow">
                    CLAIM A
                  </span>
                </div>
              )}
            </div>

            <div className="mt-2 text-xs bg-slate-50 p-2 rounded border border-slate-200">
              <span className="text-slate-500 font-medium">Extracted Claim:</span>
              <div className="font-bold text-slate-900 text-sm mt-0.5 font-mono">
                "{evA.raw_value}"
              </div>
              {evA.normalized_value && evA.normalized_value !== evA.raw_value && (
                <div className="text-[11px] text-slate-500 mt-0.5">
                  Normalized: <span className="font-mono text-slate-700">{evA.normalized_value}</span>
                </div>
              )}
            </div>
          </div>

          {/* Right Side: Source B */}
          <div className="bg-white rounded-lg border border-slate-200 p-3 shadow-sm flex flex-col">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 text-xs">
              <span className="font-semibold text-slate-700 flex items-center gap-1.5">
                <FileText size={14} className="text-amber-600" />
                {evB.document_name}
              </span>
              <span className="text-slate-500 font-mono">Page {evB.page_number}</span>
            </div>

            <div className="relative bg-slate-50 rounded border border-slate-200 h-80 overflow-hidden flex items-center justify-center group">
              <img
                src={`/api/documents/${evB.document_id}/pages/${evB.page_number}/image`}
                alt="Document Source B"
                className="max-h-full max-w-full object-contain"
                onError={(e) => {
                  (e.target as HTMLElement).style.display = 'none';
                }}
              />

              {/* Bounding Box Highlight Overlay */}
              {evB.bbox && (
                <div
                  className="absolute border-2 border-amber-500 bg-amber-500/15 pulsing-highlight pointer-events-none rounded transition"
                  style={{
                    left: `${evB.bbox.x0 * 100}%`,
                    top: `${evB.bbox.y0 * 100}%`,
                    width: `${(evB.bbox.x1 - evB.bbox.x0) * 100}%`,
                    height: `${(evB.bbox.y1 - evB.bbox.y0) * 100}%`,
                  }}
                >
                  <span className="absolute -top-5 left-0 text-[10px] bg-amber-600 text-white px-1.5 py-0.2 rounded font-mono shadow">
                    CLAIM B
                  </span>
                </div>
              )}
            </div>

            <div className="mt-2 text-xs bg-slate-50 p-2 rounded border border-slate-200">
              <span className="text-slate-500 font-medium">Extracted Claim:</span>
              <div className="font-bold text-slate-900 text-sm mt-0.5 font-mono">
                "{evB.raw_value}"
              </div>
              {evB.normalized_value && evB.normalized_value !== evB.raw_value && (
                <div className="text-[11px] text-slate-500 mt-0.5">
                  Normalized: <span className="font-mono text-slate-700">{evB.normalized_value}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Docked Rule Explanation & Officer Review Decision */}
      <div className="p-4 bg-white grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Explanation & Uncertainty Note */}
        <div className="lg:col-span-2 space-y-3">
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Rule Execution Analysis
            </h3>
            <p className="text-sm text-slate-800 font-medium mt-1 leading-relaxed">
              {finding.explanation}
            </p>
          </div>

          <div className="bg-amber-50/70 border border-amber-200 rounded-lg p-3 text-xs text-amber-900 flex items-start gap-2.5">
            <AlertCircle size={16} className="text-amber-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">Uncertainty Note: </span>
              {finding.uncertainty_note || 'Potential inconsistency; reviewer confirmation is required. Automated system never accuses.'}
            </div>
          </div>

          {clarificationDraft && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between text-xs font-bold text-blue-900 mb-1">
                <span>Neutral Clarification Letter Draft</span>
                <button
                  onClick={() => navigator.clipboard.writeText(clarificationDraft)}
                  className="text-blue-600 hover:underline"
                >
                  Copy to Clipboard
                </button>
              </div>
              <textarea
                value={clarificationDraft}
                onChange={(e) => setClarificationDraft(e.target.value)}
                rows={6}
                className="w-full text-xs font-mono p-2 border border-blue-300 rounded bg-white text-slate-800"
              />
            </div>
          )}
        </div>

        {/* Right Col: Human Decision Panel */}
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck size={14} className="text-blue-700" />
              Human Reviewer Decision
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Officer review is required to confirm or dismiss. Decisions are permanently audited.
            </p>

            <div className="mt-3">
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Mandatory Review Reason / Comment:
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="e.g. Confirmed discrepancy between AICTE Approval and Fire NOC..."
                rows={3}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 mt-4">
            <button
              onClick={() => handleAction('confirmed')}
              disabled={submitting}
              className="flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-rose-600 hover:bg-rose-700 text-white shadow-sm transition disabled:opacity-50"
            >
              <CheckCircle2 size={14} />
              Confirm Discrepancy
            </button>
            <button
              onClick={() => handleAction('dismissed')}
              disabled={submitting}
              className="flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-800 transition disabled:opacity-50"
            >
              <XCircle size={14} />
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
