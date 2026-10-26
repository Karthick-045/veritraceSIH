import React, { useEffect, useState } from 'react';
import {
  api,
  Case,
  DocumentItem,
  Finding,
  ExtractedField,
  AuditEvent,
} from '../api/client';
import { EvidenceLens } from '../components/EvidenceLens';
import { CaseEvidenceGraph } from '../components/CaseEvidenceGraph';
import { AuditTimeline } from '../components/AuditTimeline';
import { StatusBadge } from '../components/StatusBadge';
import {
  ArrowLeft,
  Play,
  RotateCcw,
  FileText,
  Layers,
  History,
  Upload,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Database,
  Edit2,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

interface CaseWorkspacePageProps {
  caseId: number;
  onBack: () => void;
}

export const CaseWorkspacePage: React.FC<CaseWorkspacePageProps> = ({ caseId, onBack }) => {
  const [caseObj, setCaseObj] = useState<Case | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [fields, setFields] = useState<ExtractedField[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [reproducing, setReproducing] = useState(false);
  const [reproduceResult, setReproduceResult] = useState<any | null>(null);

  // Tabs: lens | fields | graph | audit | upload
  const [activeTab, setActiveTab] = useState<'lens' | 'fields' | 'graph' | 'audit' | 'upload'>('lens');
  const [selectedFindingIndex, setSelectedFindingIndex] = useState(0);

  // Field editing state
  const [editingFieldId, setEditingFieldId] = useState<number | null>(null);
  const [correctedValue, setCorrectedValue] = useState('');
  const [correctionReason, setCorrectionReason] = useState('');

  // Upload file state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadDocType, setUploadDocType] = useState('general');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadAllData();
  }, [caseId]);

  const loadAllData = async () => {
    try {
      setLoading(true);
      const [cData, docsData, findingsData, fieldsData, auditData] = await Promise.all([
        api.getCase(caseId),
        api.getDocuments(caseId),
        api.getFindings(caseId),
        api.getFields(caseId),
        api.getCaseAudit(caseId),
      ]);
      setCaseObj(cData);
      setDocuments(docsData);
      setFindings(findingsData);
      setFields(fieldsData);
      setAuditEvents(auditData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async () => {
    try {
      setAnalyzing(true);
      await api.analyzeCase(caseId);
      await loadAllData();
    } catch (err: any) {
      alert(`Analysis failed: ${err.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleReproduceRun = async () => {
    if (findings.length === 0 || !findings[0].analysis_run_id) {
      alert('Run analysis first to test reproducibility.');
      return;
    }
    try {
      setReproducing(true);
      const res = await api.reproduceRun(findings[0].analysis_run_id);
      setReproduceResult(res);
    } catch (err: any) {
      alert(`Reproduce failed: ${err.message}`);
    } finally {
      setReproducing(false);
    }
  };

  const handleReviewFinding = async (decision: string, comment: string) => {
    if (findings.length === 0) return;
    const currentFinding = findings[selectedFindingIndex];
    try {
      await api.reviewFinding(currentFinding.id, decision, comment);
      await loadAllData();
    } catch (err: any) {
      alert(`Review action failed: ${err.message}`);
    }
  };

  const handleSaveCorrection = async (fieldId: number) => {
    if (!correctedValue.trim()) return;
    try {
      await api.correctField(fieldId, correctedValue.trim(), correctionReason.trim());
      setEditingFieldId(null);
      setCorrectedValue('');
      setCorrectionReason('');
      await loadAllData();
    } catch (err: any) {
      alert(`Correction failed: ${err.message}`);
    }
  };

  const handleUploadDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    try {
      setUploading(true);
      await api.uploadDocument(caseId, uploadFile, uploadDocType);
      setUploadFile(null);
      await loadAllData();
      alert('Document uploaded and extracted successfully.');
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  if (loading || !caseObj) {
    return (
      <div className="p-12 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <p className="text-xs text-slate-500 mt-2">Loading Case Workspace...</p>
      </div>
    );
  }

  const selectedFinding = findings[selectedFindingIndex];

  return (
    <div className="space-y-6">
      {/* Top Header / Nav */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 hover:bg-slate-100 rounded-lg text-slate-600 transition"
          >
            <ArrowLeft size={18} />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-blue-900 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200">
                {caseObj.case_number}
              </span>
              <StatusBadge status={caseObj.status} size="sm" />
            </div>
            <h1 className="text-lg font-black text-slate-900 mt-0.5">
              {caseObj.institution_name}
            </h1>
            <p className="text-xs text-slate-500">{caseObj.title}</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleRunAnalysis}
            disabled={analyzing}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white rounded-lg shadow-sm transition disabled:opacity-50"
          >
            <Play size={14} fill="currentColor" />
            {analyzing ? 'Evaluating Rules...' : 'Re-Run Rule Engine'}
          </button>

          <button
            onClick={handleReproduceRun}
            disabled={reproducing}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-100 rounded-lg shadow-sm transition disabled:opacity-50"
          >
            <RotateCcw size={14} className={reproducing ? 'animate-spin' : ''} />
            Reproduce Run (Proof)
          </button>
        </div>
      </div>

      {/* Reproducibility Proof Modal / Card */}
      {reproduceResult && (
        <div className="bg-emerald-500/10 border-2 border-emerald-500/50 rounded-xl p-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-600 text-white rounded-lg">
              <CheckCircle2 size={20} />
            </div>
            <div>
              <div className="text-xs font-mono font-bold text-emerald-900 flex items-center gap-2">
                REPRODUCIBILITY PROOF: IDENTICAL = {reproduceResult.identical ? 'TRUE' : 'FALSE'}
              </div>
              <p className="text-xs text-emerald-800 mt-0.5">
                Input Hash: <span className="font-mono font-semibold">{reproduceResult.input_hash}</span>
              </p>
              <p className="text-[11px] text-emerald-700 mt-0.5">{reproduceResult.message}</p>
            </div>
          </div>
          <button
            onClick={() => setReproduceResult(null)}
            className="text-xs font-bold text-emerald-800 hover:underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Processing Theatre: Honest Pipeline Tracker */}
      <div className="bg-slate-900 text-slate-100 rounded-xl p-4 shadow-sm border border-slate-800">
        <div className="flex items-center justify-between mb-3 text-xs">
          <span className="font-semibold text-slate-300 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
            <Sparkles size={14} className="text-blue-400" />
            Processing Pipeline Live Tracker
          </span>
          <span className="text-slate-400 font-mono text-[11px]">
            {documents.length} Ingested PDFs · {fields.length} Anchored Claims · {findings.length} Findings
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700 flex items-center gap-2.5">
            <CheckCircle2 size={18} className="text-emerald-400 shrink-0" />
            <div className="text-xs">
              <div className="font-bold text-slate-200">1. Uploaded</div>
              <div className="text-[10px] text-slate-400 font-mono">{documents.length} documents validated</div>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700 flex items-center gap-2.5">
            <CheckCircle2 size={18} className="text-emerald-400 shrink-0" />
            <div className="text-xs">
              <div className="font-bold text-slate-200">2. Text Extracted</div>
              <div className="text-[10px] text-slate-400 font-mono">PyMuPDF / Word BBoxes</div>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700 flex items-center gap-2.5">
            <CheckCircle2 size={18} className="text-emerald-400 shrink-0" />
            <div className="text-xs">
              <div className="font-bold text-slate-200">3. Claims Anchored</div>
              <div className="text-[10px] text-slate-400 font-mono">{fields.length} fields normalized</div>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700 flex items-center gap-2.5">
            <CheckCircle2 size={18} className="text-emerald-400 shrink-0" />
            <div className="text-xs">
              <div className="font-bold text-slate-200">4. Rules Evaluated</div>
              <div className="text-[10px] text-slate-400 font-mono">5 Versioned Rules Executed</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-1">
        <button
          onClick={() => setActiveTab('lens')}
          className={`flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-lg transition ${
            activeTab === 'lens'
              ? 'bg-blue-700 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <AlertTriangle size={15} />
          Evidence Lens ({findings.length})
        </button>

        <button
          onClick={() => setActiveTab('fields')}
          className={`flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-lg transition ${
            activeTab === 'fields'
              ? 'bg-blue-700 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Database size={15} />
          Extracted Claims ({fields.length})
        </button>

        <button
          onClick={() => setActiveTab('graph')}
          className={`flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-lg transition ${
            activeTab === 'graph'
              ? 'bg-blue-700 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Layers size={15} />
          Case Evidence Graph
        </button>

        <button
          onClick={() => setActiveTab('audit')}
          className={`flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-lg transition ${
            activeTab === 'audit'
              ? 'bg-blue-700 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <History size={15} />
          Audit Timeline ({auditEvents.length})
        </button>

        <button
          onClick={() => setActiveTab('upload')}
          className={`flex items-center gap-1.5 px-4 py-2 text-xs font-bold rounded-lg transition ${
            activeTab === 'upload'
              ? 'bg-blue-700 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Upload size={15} />
          Documents & Upload ({documents.length})
        </button>
      </div>

      {/* TAB CONTENT 1: EVIDENCE LENS */}
      {activeTab === 'lens' && (
        <div className="space-y-4">
          {findings.length === 0 ? (
            <div className="bg-white p-12 text-center rounded-xl border border-slate-200">
              <CheckCircle2 size={40} className="mx-auto text-emerald-500 mb-2" />
              <h3 className="text-base font-bold text-slate-800">
                No Inconsistencies Detected within Checked Rules
              </h3>
              <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                All extracted claims satisfy the enabled validation rules. Note: this applies only to verified rules and does not claim official production certification.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Finding Selector Sidebar */}
              <div className="lg:col-span-1 space-y-2">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-2">
                  Flagged Inconsistencies ({findings.length})
                </span>

                {findings.map((f, idx) => (
                  <div
                    key={f.id}
                    onClick={() => setSelectedFindingIndex(idx)}
                    className={`p-3 rounded-xl border text-xs cursor-pointer transition ${
                      selectedFindingIndex === idx
                        ? 'border-blue-600 bg-blue-50/70 shadow-sm ring-2 ring-blue-500/20'
                        : 'border-slate-200 bg-white hover:border-blue-200'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="font-mono text-[10px] text-blue-800 font-bold">
                        {f.rule_code}
                      </span>
                      <StatusBadge status={f.severity} size="sm" />
                    </div>
                    <div className="font-bold text-slate-900 line-clamp-1">{f.title}</div>
                    <div className="text-[11px] text-slate-500 mt-1 flex items-center justify-between">
                      <span>Status: {f.reviewer_status}</span>
                      <span className="text-blue-600 font-semibold">View Lens →</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Signature Screen: Evidence Lens */}
              <div className="lg:col-span-3">
                {selectedFinding && (
                  <EvidenceLens
                    finding={selectedFinding}
                    onReview={handleReviewFinding}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT 2: ANCHORED CLAIMS & PROVENANCE CORRECTIONS */}
      {activeTab === 'fields' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Anchored Claims & Provenance Normalization
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Raw verbatim extraction displayed side-by-side with normalized values. Reviewers can correct values while preserving original raw values.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 uppercase text-[11px]">
                <tr>
                  <th className="py-2.5 px-4">Field Key</th>
                  <th className="py-2.5 px-4">Document / Page</th>
                  <th className="py-2.5 px-4">Raw Extracted Value</th>
                  <th className="py-2.5 px-4">Normalized Value</th>
                  <th className="py-2.5 px-4 text-center">Confidence</th>
                  <th className="py-2.5 px-4 text-center">Status</th>
                  <th className="py-2.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {fields.map((f) => (
                  <tr key={f.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-4 font-mono font-bold text-slate-800">
                      {f.field_key}
                    </td>
                    <td className="py-2.5 px-4 text-slate-600">
                      {f.document_name || `Doc #${f.document_id}`} (P.{f.page_number})
                    </td>
                    <td className="py-2.5 px-4 font-mono text-slate-900 font-medium">
                      "{f.raw_value}"
                    </td>
                    <td className="py-2.5 px-4 font-mono text-blue-700">
                      {f.normalized_value || <span className="italic text-slate-400">None</span>}
                    </td>
                    <td className="py-2.5 px-4 text-center">
                      <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100">
                        {f.confidence.toFixed(2)}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-center">
                      {f.is_ambiguous ? (
                        <span className="px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-bold">
                          Ambiguous Date
                        </span>
                      ) : f.review_status === 'corrected' ? (
                        <span className="px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-bold">
                          Corrected
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-medium">
                          Extracted
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={() => {
                          setEditingFieldId(f.id);
                          setCorrectedValue(f.raw_value);
                        }}
                        className="p-1 hover:bg-slate-200 rounded text-slate-600 transition"
                        title="Correct OCR Value"
                      >
                        <Edit2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Edit Modal */}
          {editingFieldId && (
            <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="bg-white rounded-xl shadow-xl max-w-sm w-full p-5 space-y-3">
                <h4 className="text-sm font-bold text-slate-900">
                  Reviewer Correction with Provenance
                </h4>
                <p className="text-xs text-slate-500">
                  Original raw value is permanently preserved in the audit database.
                </p>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Corrected Value:
                  </label>
                  <input
                    type="text"
                    value={correctedValue}
                    onChange={(e) => setCorrectedValue(e.target.value)}
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-lg font-mono focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Reason for Correction:
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. OCR misread digit '1' as 'I'"
                    value={correctionReason}
                    onChange={(e) => setCorrectionReason(e.target.value)}
                    className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    onClick={() => setEditingFieldId(null)}
                    className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleSaveCorrection(editingFieldId)}
                    className="px-3 py-1.5 text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white rounded"
                  >
                    Save & Re-Normalize
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT 3: EVIDENCE GRAPH */}
      {activeTab === 'graph' && <CaseEvidenceGraph caseId={caseId} />}

      {/* TAB CONTENT 4: AUDIT TIMELINE */}
      {activeTab === 'audit' && <AuditTimeline events={auditEvents} />}

      {/* TAB CONTENT 5: DOCUMENTS & UPLOAD */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">
              Upload Additional PDF to Bundle
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Files are stored in private encrypted storage, checksummed with SHA256, and processed by PyMuPDF / Tesseract.
            </p>

            <form onSubmit={handleUploadDocument} className="flex flex-wrap items-center gap-4">
              <input
                type="file"
                accept=".pdf,image/png,image/jpeg"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                className="text-xs text-slate-600 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />

              <select
                value={uploadDocType}
                onChange={(e) => setUploadDocType(e.target.value)}
                className="text-xs p-2 border border-slate-300 rounded-lg bg-white"
              >
                <option value="aicte_approval">AICTE Approval Letter</option>
                <option value="land_certificate">Land Certificate</option>
                <option value="fire_safety_noc">Fire Safety Clearance NOC</option>
                <option value="building_plan">Building Safety Plan</option>
                <option value="general">General Statutory Document</option>
              </select>

              <button
                type="submit"
                disabled={!uploadFile || uploading}
                className="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold rounded-lg transition disabled:opacity-50"
              >
                {uploading ? 'Processing Extraction...' : 'Upload & Extract'}
              </button>
            </form>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">
              Current Documents in Case Bundle ({documents.length})
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {documents.map((doc) => (
                <div key={doc.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-mono text-blue-700 font-semibold">{doc.doc_type}</span>
                      <span className="text-slate-400 font-mono text-[10px]">
                        {(doc.file_size_bytes / 1024).toFixed(1)} KB
                      </span>
                    </div>
                    <div className="font-bold text-slate-800 text-sm truncate">{doc.original_filename}</div>
                    <div className="text-[10px] text-slate-400 font-mono mt-1 truncate">
                      SHA256: {doc.sha256_hash.substring(0, 16)}...
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-slate-200 flex items-center justify-between">
                    <span className="text-emerald-700 text-xs font-medium flex items-center gap-1">
                      <CheckCircle2 size={14} /> Extracted
                    </span>
                    <a
                      href={`/api/documents/${doc.id}/pages/1/image`}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs font-semibold text-blue-700 hover:underline flex items-center gap-1"
                    >
                      View Rendered Page <ExternalLink size={12} />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
