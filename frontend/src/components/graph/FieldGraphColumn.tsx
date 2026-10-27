import React from 'react';
import { Database } from 'lucide-react';
import { EvidenceGraphNode } from '../../api/client';
import { EvidenceGraphConnection, EvidenceGraphConnections } from './EvidenceGraphConnections';

interface FieldGraphColumnProps {
  fields: EvidenceGraphNode[];
  connections: Map<string, EvidenceGraphConnection[]>;
  connectedNodeIds: Set<string>;
  selectedNodeId: string | null;
  onSelectNode: (node: EvidenceGraphNode) => void;
}

export const FieldGraphColumn: React.FC<FieldGraphColumnProps> = ({
  fields,
  connections,
  connectedNodeIds,
  selectedNodeId,
  onSelectNode,
}) => (
  <section className="min-w-0 space-y-3">
    <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
      <Database size={14} className="text-emerald-600" />
      2. Anchored Claims
    </h4>
    <div className="max-h-96 space-y-2 overflow-y-auto pr-1">
      {fields.map((field) => {
        const isConnected = connectedNodeIds.has(field.id);
        const isSelected = selectedNodeId === field.id;
        const confidence = field.data.confidence;

        return (
          <div
            key={field.id}
            className={`rounded-lg border p-3 transition ${
              isSelected
                ? 'border-emerald-600 bg-emerald-50/60 ring-2 ring-emerald-500/20'
                : isConnected
                  ? 'border-emerald-300 bg-emerald-50/30'
                  : 'border-slate-200 bg-white'
            }`}
          >
            <button
              type="button"
              onClick={() => onSelectNode(field)}
              className="w-full text-left text-xs"
            >
              <span className="flex items-center justify-between gap-2">
                <span className="truncate font-mono text-[10px] uppercase text-slate-500">
                  {String(field.data.field_key ?? 'Unknown field')}
                </span>
                <span className="shrink-0 rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] text-slate-600">
                  conf: {typeof confidence === 'number' ? confidence.toFixed(2) : 'N/A'}
                </span>
              </span>
              <span className="mt-1 block truncate font-semibold text-slate-800">
                "{String(field.data.raw_value ?? field.label)}"
              </span>
              {field.data.is_ambiguous === true && (
                <span className="mt-1 inline-block rounded bg-blue-50 px-1.5 text-[10px] text-blue-700">
                  Ambiguous format
                </span>
              )}
            </button>
            <EvidenceGraphConnections
              connections={connections.get(field.id) ?? []}
              onSelectNode={onSelectNode}
            />
          </div>
        );
      })}
      {fields.length === 0 && (
        <p className="rounded-lg border border-dashed border-slate-200 p-3 text-xs text-slate-400">
          No extracted claims
        </p>
      )}
    </div>
  </section>
);
