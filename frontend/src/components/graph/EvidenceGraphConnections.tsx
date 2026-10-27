import React from 'react';
import { ArrowRight } from 'lucide-react';
import { EvidenceGraphEdge, EvidenceGraphNode } from '../../api/client';

export interface EvidenceGraphConnection {
  edge: EvidenceGraphEdge;
  node: EvidenceGraphNode;
}

interface EvidenceGraphConnectionsProps {
  connections: EvidenceGraphConnection[];
  onSelectNode: (node: EvidenceGraphNode) => void;
}

export const EvidenceGraphConnections: React.FC<EvidenceGraphConnectionsProps> = ({
  connections,
  onSelectNode,
}) => (
  <div className="mt-2 space-y-1">
    {connections.map(({ edge, node }) => (
      <button
        key={edge.id}
        type="button"
        onClick={() => onSelectNode(node)}
        className="flex w-full min-w-0 items-center gap-1.5 rounded px-1.5 py-1 text-left text-[10px] text-slate-600 hover:bg-slate-100 hover:text-slate-900"
        title={`${edge.label || 'connected to'} ${node.label}`}
      >
        <ArrowRight size={11} className="shrink-0 text-slate-400" />
        <span className="shrink-0 font-medium text-slate-400">{edge.label || 'related'}</span>
        <span className="truncate">{node.label}</span>
      </button>
    ))}
  </div>
);
