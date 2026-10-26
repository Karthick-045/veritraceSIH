import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { FileText, Database, AlertTriangle, Layers } from 'lucide-react';

interface CaseEvidenceGraphProps {
  caseId: number;
}

export const CaseEvidenceGraph: React.FC<CaseEvidenceGraphProps> = ({ caseId }) => {
  const [graphData, setGraphData] = useState<{ nodes: any[]; edges: any[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);

  useEffect(() => {
    loadGraph();
  }, [caseId]);

  const loadGraph = async () => {
    try {
      setLoading(true);
      const data = await api.getCaseGraph(caseId);
      setGraphData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-slate-200">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <p className="text-xs text-slate-500 mt-2 font-medium">Generating Case Evidence Graph...</p>
      </div>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-slate-200">
        <Layers size={36} className="mx-auto text-slate-400 mb-2" />
        <p className="text-sm font-semibold text-slate-700">No Evidence Nodes Available</p>
        <p className="text-xs text-slate-500 mt-1">Upload documents and run analysis to populate the graph.</p>
      </div>
    );
  }

  const docNodes = graphData.nodes.filter(n => n.type === 'documentNode');
  const fieldNodes = graphData.nodes.filter(n => n.type === 'fieldNode');
  const findingNodes = graphData.nodes.filter(n => n.type === 'findingNode');

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-100">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Layers size={18} className="text-blue-600" />
            Case Evidence Graph
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Auto-generated provenance mapping: Documents → Anchored Claims → Rule Findings (conflicts highlighted in red)
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <span className="flex items-center gap-1.5 font-medium text-blue-700">
            <span className="w-3 h-3 rounded bg-blue-100 border border-blue-400 inline-block"></span>
            Documents ({docNodes.length})
          </span>
          <span className="flex items-center gap-1.5 font-medium text-emerald-700">
            <span className="w-3 h-3 rounded bg-emerald-100 border border-emerald-400 inline-block"></span>
            Extracted Claims ({fieldNodes.length})
          </span>
          <span className="flex items-center gap-1.5 font-medium text-rose-700">
            <span className="w-3 h-3 rounded bg-rose-100 border border-rose-400 inline-block"></span>
            Findings ({findingNodes.length})
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Column 1: Documents */}
        <div className="space-y-3">
          <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <FileText size={14} className="text-blue-600" />
            1. Source Documents
          </h4>
          <div className="space-y-2">
            {docNodes.map(doc => (
              <div
                key={doc.id}
                onClick={() => setSelectedNode(doc)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition ${
                  selectedNode?.id === doc.id
                    ? 'border-blue-600 bg-blue-50/60 ring-2 ring-blue-500/20'
                    : 'border-slate-200 bg-slate-50 hover:border-blue-300'
                }`}
              >
                <div className="font-semibold text-slate-900 truncate">{doc.label}</div>
                <div className="text-[11px] text-slate-500 mt-1 flex justify-between">
                  <span>Type: {doc.data.doc_type}</span>
                  <span className="text-emerald-600 font-medium">{doc.data.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Column 2: Claims / Fields */}
        <div className="space-y-3">
          <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <Database size={14} className="text-emerald-600" />
            2. Anchored Claims
          </h4>
          <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
            {fieldNodes.map(f => (
              <div
                key={f.id}
                onClick={() => setSelectedNode(f)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition ${
                  selectedNode?.id === f.id
                    ? 'border-emerald-600 bg-emerald-50/60 ring-2 ring-emerald-500/20'
                    : 'border-slate-200 bg-white hover:border-emerald-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] text-slate-500 uppercase">{f.data.field_key}</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                    conf: {f.data.confidence}
                  </span>
                </div>
                <div className="font-semibold text-slate-800 mt-1 truncate">
                  "{f.data.raw_value}"
                </div>
                {f.data.is_ambiguous && (
                  <span className="inline-block mt-1 text-[10px] bg-blue-50 text-blue-700 px-1.5 rounded">
                    Ambiguous format
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Column 3: Findings */}
        <div className="space-y-3">
          <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle size={14} className="text-rose-600" />
            3. Rule Engine Findings
          </h4>
          <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
            {findingNodes.map(find => (
              <div
                key={find.id}
                onClick={() => setSelectedNode(find)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition ${
                  selectedNode?.id === find.id
                    ? 'border-rose-600 bg-rose-50/60 ring-2 ring-rose-500/20'
                    : 'border-rose-200 bg-rose-50/30 hover:border-rose-400'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] text-rose-700 font-bold">{find.data.rule_code}</span>
                  <span className="text-[10px] font-semibold text-rose-600">{find.data.severity}</span>
                </div>
                <div className="font-bold text-slate-900 mt-1">
                  {find.label}
                </div>
                <div className="text-[11px] text-slate-600 mt-1 line-clamp-2">
                  {find.data.explanation}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Selected Node Inspector Drawer */}
      {selectedNode && (
        <div className="mt-6 p-4 rounded-xl bg-slate-900 text-slate-100 text-xs flex flex-wrap items-center justify-between gap-4">
          <div>
            <span className="font-mono text-blue-400 uppercase text-[10px]">{selectedNode.type}</span>
            <div className="font-bold text-sm text-white mt-0.5">{selectedNode.label}</div>
            <pre className="text-[11px] font-mono text-slate-300 mt-1 max-h-24 overflow-auto">
              {JSON.stringify(selectedNode.data, null, 2)}
            </pre>
          </div>
          <button
            onClick={() => setSelectedNode(null)}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs"
          >
            Close Inspector
          </button>
        </div>
      )}
    </div>
  );
};
