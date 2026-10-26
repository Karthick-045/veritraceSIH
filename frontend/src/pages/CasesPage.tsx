import React, { useEffect, useState } from 'react';
import { api, Case } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { Folder, Plus, Search, FileText, AlertTriangle, ArrowRight, X } from 'lucide-react';

interface CasesPageProps {
  onSelectCase: (caseId: number) => void;
}

export const CasesPage: React.FC<CasesPageProps> = ({ onSelectCase }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);

  // New Case Form
  const [newCaseNumber, setNewCaseNumber] = useState('');
  const [newTitle, setNewTitle] = useState('');
  const [newInstitution, setNewInstitution] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      setLoading(true);
      const data = await api.getCases();
      setCases(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCaseNumber.trim() || !newInstitution.trim()) {
      setFormError('Case Number and Institution Name are mandatory.');
      return;
    }
    setSubmitting(true);
    setFormError(null);
    try {
      const created = await api.createCase({
        case_number: newCaseNumber.trim(),
        title: newTitle.trim() || `${newInstitution.trim()} - Scrutiny Application`,
        institution_name: newInstitution.trim(),
      });
      setShowModal(false);
      setNewCaseNumber('');
      setNewTitle('');
      setNewInstitution('');
      await loadCases();
      onSelectCase(created.id);
    } catch (err: any) {
      setFormError(err.message || 'Failed to create case');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredCases = cases.filter(
    (c) =>
      c.case_number.toLowerCase().includes(search.toLowerCase()) ||
      c.institution_name.toLowerCase().includes(search.toLowerCase()) ||
      c.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Folder size={22} className="text-blue-700" />
            Institutional Application Cases
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage application bundles, review document claims, and resolve cross-document inconsistencies.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-1.5 px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-bold shadow-sm transition"
        >
          <Plus size={16} />
          New Application Case
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search size={16} className="absolute left-3.5 top-3 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by Case Number, Institution Name, or Title..."
          className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-lg text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
        />
      </div>

      {/* Cases Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
            <p className="text-xs text-slate-500 mt-2">Loading cases...</p>
          </div>
        ) : filteredCases.length === 0 ? (
          <div className="p-12 text-center">
            <Folder size={36} className="mx-auto text-slate-300 mb-2" />
            <p className="text-sm font-semibold text-slate-700">No Application Cases Found</p>
            <p className="text-xs text-slate-400 mt-1">Create a new application case or load the demo bundle.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="py-3 px-4">Case Number</th>
                  <th className="py-3 px-4">Institution Name</th>
                  <th className="py-3 px-4">Documents</th>
                  <th className="py-3 px-4">Findings</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredCases.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => onSelectCase(c.id)}
                    className="hover:bg-blue-50/40 cursor-pointer transition"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-blue-900">{c.case_number}</td>
                    <td className="py-3 px-4 font-semibold text-slate-900">
                      {c.institution_name}
                      <span className="block text-[11px] text-slate-500 font-normal truncate max-w-sm">
                        {c.title}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1 font-mono text-slate-700">
                        <FileText size={14} className="text-slate-400" />
                        {c.document_count}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {c.finding_count > 0 ? (
                        <span className="inline-flex items-center gap-1 font-mono font-bold text-amber-600">
                          <AlertTriangle size={14} />
                          {c.finding_count} Flagged
                        </span>
                      ) : (
                        <span className="text-emerald-600 font-medium font-mono">0</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={c.status} size="sm" />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectCase(c.id);
                        }}
                        className="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-100 hover:bg-blue-600 hover:text-white text-slate-700 rounded text-xs font-semibold transition"
                      >
                        Open Workspace <ArrowRight size={12} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* New Case Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full border border-slate-200 overflow-hidden">
            <div className="bg-slate-900 text-white p-4 flex items-center justify-between">
              <h3 className="text-sm font-bold">Register New Application Case</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateCase} className="p-6 space-y-4">
              {formError && (
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                  <AlertTriangle size={16} className="shrink-0" />
                  <span>{formError}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Case Number / File Identifier *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. CASE-2026-AICTE-099"
                  value={newCaseNumber}
                  onChange={(e) => setNewCaseNumber(e.target.value)}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg font-mono focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Name of Institution *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. National Institute of Technology"
                  value={newInstitution}
                  onChange={(e) => setNewInstitution(e.target.value)}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Application Title / Description
                </label>
                <input
                  type="text"
                  placeholder="e.g. Extension of Approval 2025-26"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white rounded-lg shadow-sm transition disabled:opacity-50"
                >
                  {submitting ? 'Creating...' : 'Create Case'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
