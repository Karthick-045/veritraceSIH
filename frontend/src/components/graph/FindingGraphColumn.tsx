import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { EvidenceGraphNode } from '../../api/client';
import { EvidenceGraphConnection, EvidenceGraphConnections } from './EvidenceGraphConnections';

interface FindingGraphColumnProps {
  findings: EvidenceGraphNode[];
  connections: Map<string, EvidenceGraphConnection[]>;
  connectedNodeIds: Set<string>;
  selectedNodeId: string | null;
  onSelectNode: (node: EvidenceGraphNode) => void;
}

export const FindingGraphColumn: React.FC<FindingGraphColumnProps> = ({
  findings,
  connections,
  connectedNodeIds,
  selectedNodeId,
  onSelectNode,
}) => (
  <section className="min-w-0 space-y-3">
    <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
      <AlertTriangle size={14} className="text-rose-600" />
      3. Rule Engine Findings
    </h4>
    <div className="max-h-96 space-y-2 overflow-y-auto pr-1">
      {findings.map((finding) => {
        const isConnected = connectedNodeIds.has(finding.id);
        const isSelected = selectedNodeId === finding.id;

        return (
          <div
            key={finding.id}
            className={`rounded-lg border p-3 transition ${
              isSelected
                ? 'border-rose-600 bg-rose-50/60 ring-2 ring-rose-500/20'
                : isConnected
                  ? 'border-rose-300 bg-rose-50/50'
                  : 'border-rose-200 bg-rose-50/30'
            }`}
          >
            <button
              type="button"
              onClick={() => onSelectNode(finding)}
              className="w-full text-left text-xs"
            >
              <span className="flex items-center justify-between gap-2">
                <span className="truncate font-mono text-[10px] font-bold text-rose-700">
                  {String(finding.data.rule_code ?? 'Rule finding')}
                </span>
                <span className="shrink-0 text-[10px] font-semibold text-rose-600">
                  {String(finding.data.severity ?? 'Unspecified')}
                </span>
              </span>
              <span className="mt-1 block font-bold text-slate-900">{finding.label}</span>
              <span className="mt-1 line-clamp-2 block text-[11px] text-slate-600">
                {String(finding.data.explanation ?? '')}
              </span>
            </button>
            <EvidenceGraphConnections
              connections={connections.get(finding.id) ?? []}
              onSelectNode={onSelectNode}
            />
          </div>
        );
      })}
      {findings.length === 0 && (
        <p className="rounded-lg border border-dashed border-slate-200 p-3 text-xs text-slate-400">
          No rule findings
        </p>
      )}
    </div>
  </section>
);
