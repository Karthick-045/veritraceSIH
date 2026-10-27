import React from 'react';
import { FileText } from 'lucide-react';
import { EvidenceGraphNode } from '../../api/client';
import { EvidenceGraphConnection, EvidenceGraphConnections } from './EvidenceGraphConnections';

interface DocumentGraphColumnProps {
  documents: EvidenceGraphNode[];
  connections: Map<string, EvidenceGraphConnection[]>;
  connectedNodeIds: Set<string>;
  selectedNodeId: string | null;
  onSelectNode: (node: EvidenceGraphNode) => void;
}

export const DocumentGraphColumn: React.FC<DocumentGraphColumnProps> = ({
  documents,
  connections,
  connectedNodeIds,
  selectedNodeId,
  onSelectNode,
}) => (
  <section className="min-w-0 space-y-3">
    <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
      <FileText size={14} className="text-blue-600" />
      1. Source Documents
    </h4>
    <div className="max-h-96 space-y-2 overflow-y-auto pr-1">
      {documents.map((document) => {
        const isConnected = connectedNodeIds.has(document.id);
        const isSelected = selectedNodeId === document.id;

        return (
          <div
            key={document.id}
            className={`rounded-lg border p-3 transition ${
              isSelected
                ? 'border-blue-600 bg-blue-50/60 ring-2 ring-blue-500/20'
                : isConnected
                  ? 'border-blue-300 bg-blue-50/30'
                  : 'border-slate-200 bg-slate-50'
            }`}
          >
            <button
              type="button"
              onClick={() => onSelectNode(document)}
              className="w-full text-left text-xs"
            >
              <span className="block truncate font-semibold text-slate-900">{document.label}</span>
              <span className="mt-1 flex justify-between gap-2 text-[11px] text-slate-500">
                <span>Type: {String(document.data.doc_type ?? 'Unknown')}</span>
                <span className="font-medium text-emerald-600">
                  {String(document.data.status ?? 'Unknown')}
                </span>
              </span>
            </button>
            <EvidenceGraphConnections
              connections={connections.get(document.id) ?? []}
              onSelectNode={onSelectNode}
            />
          </div>
        );
      })}
      {documents.length === 0 && (
        <p className="rounded-lg border border-dashed border-slate-200 p-3 text-xs text-slate-400">
          No source documents
        </p>
      )}
    </div>
  </section>
);
