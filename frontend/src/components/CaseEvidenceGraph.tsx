import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Layers } from 'lucide-react';
import {
  api,
  CaseEvidenceGraph as CaseEvidenceGraphData,
  EvidenceGraphNode,
} from '../api/client';
import { DocumentGraphColumn } from './graph/DocumentGraphColumn';
import { FieldGraphColumn } from './graph/FieldGraphColumn';
import {
  EvidenceGraphConnection,
} from './graph/EvidenceGraphConnections';
import { FindingGraphColumn } from './graph/FindingGraphColumn';
import { EvidenceGraphMap } from './graph/EvidenceGraphMap';

interface CaseEvidenceGraphProps {
  caseId: number;
}

export const CaseEvidenceGraph: React.FC<CaseEvidenceGraphProps> = ({ caseId }) => {
  const [graphData, setGraphData] = useState<CaseEvidenceGraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<EvidenceGraphNode | null>(null);

  useEffect(() => {
    let active = true;

    const loadGraph = async () => {
      try {
        setLoading(true);
        setLoadError(null);
        setGraphData(null);
        setSelectedNode(null);
        const data = await api.getCaseGraph(caseId);
        if (active) setGraphData(data);
      } catch (err) {
        if (active) {
          setLoadError(err instanceof Error ? err.message : 'An unexpected error occurred.');
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    void loadGraph();
    return () => {
      active = false;
    };
  }, [caseId]);

  const nodesById = useMemo(
    () => new Map((graphData?.nodes ?? []).map((node) => [node.id, node])),
    [graphData],
  );

  const connectionsByNode = useMemo(() => {
    const connections = new Map<string, EvidenceGraphConnection[]>();

    for (const edge of graphData?.edges ?? []) {
      const sourceNode = nodesById.get(edge.source);
      const targetNode = nodesById.get(edge.target);
      if (!sourceNode || !targetNode) continue;

      const sourceConnections = connections.get(sourceNode.id) ?? [];
      sourceConnections.push({ edge, node: targetNode });
      connections.set(sourceNode.id, sourceConnections);

      const targetConnections = connections.get(targetNode.id) ?? [];
      targetConnections.push({ edge, node: sourceNode });
      connections.set(targetNode.id, targetConnections);
    }

    return connections;
  }, [graphData, nodesById]);

  const connectedNodeIds = useMemo(() => {
    if (!selectedNode) return new Set<string>();

    const adjacency = new Map<string, Set<string>>();
    for (const edge of graphData?.edges ?? []) {
      adjacency.set(edge.source, (adjacency.get(edge.source) ?? new Set()).add(edge.target));
      adjacency.set(edge.target, (adjacency.get(edge.target) ?? new Set()).add(edge.source));
    }

    const visited = new Set<string>([selectedNode.id]);
    const pending = [selectedNode.id];
    while (pending.length > 0) {
      const current = pending.pop();
      if (!current) continue;
      for (const neighbor of adjacency.get(current) ?? []) {
        if (visited.has(neighbor)) continue;
        visited.add(neighbor);
        pending.push(neighbor);
      }
    }
    return visited;
  }, [graphData, selectedNode]);

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="mt-2 text-xs font-medium text-slate-500">Generating Case Evidence Graph...</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div role="alert" className="rounded-xl border border-rose-200 bg-white p-8 text-center">
        <AlertCircle size={36} className="mx-auto mb-2 text-rose-500" />
        <p className="text-sm font-semibold text-slate-700">Unable to load evidence graph</p>
        <p className="mt-1 text-xs text-rose-600">{loadError}</p>
      </div>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <Layers size={36} className="mx-auto mb-2 text-slate-400" />
        <p className="text-sm font-semibold text-slate-700">No Evidence Nodes Available</p>
        <p className="mt-1 text-xs text-slate-500">
          Upload documents and run analysis to populate the graph.
        </p>
      </div>
    );
  }

  const documents = graphData.nodes.filter((node) => node.type === 'documentNode');
  const fields = graphData.nodes.filter((node) => node.type === 'fieldNode');
  const findings = graphData.nodes.filter((node) => node.type === 'findingNode');

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h3 className="flex items-center gap-2 text-base font-bold text-slate-900">
            <Layers size={18} className="text-blue-600" />
            Case Evidence Graph
          </h3>
          <p className="mt-0.5 text-xs text-slate-500">
            Each claim is linked to its source document and any rule findings that use that field.
            Select a node or connection to highlight its related evidence.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-4 text-xs">
          <span className="flex items-center gap-1.5 font-medium text-blue-700">
            <span className="inline-block h-3 w-3 rounded border border-blue-400 bg-blue-100" />
            Documents ({documents.length})
          </span>
          <span className="flex items-center gap-1.5 font-medium text-emerald-700">
            <span className="inline-block h-3 w-3 rounded border border-emerald-400 bg-emerald-100" />
            Extracted Claims ({fields.length})
          </span>
          <span className="flex items-center gap-1.5 font-medium text-rose-700">
            <span className="inline-block h-3 w-3 rounded border border-rose-400 bg-rose-100" />
            Findings ({findings.length})
          </span>
        </div>
      </div>

      <div className="space-y-5">
        <EvidenceGraphMap
          nodes={graphData.nodes}
          edges={graphData.edges}
          connectedNodeIds={connectedNodeIds}
          selectedNodeId={selectedNode?.id ?? null}
          onSelectNode={setSelectedNode}
        />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <DocumentGraphColumn
            documents={documents}
            connections={connectionsByNode}
            connectedNodeIds={connectedNodeIds}
            selectedNodeId={selectedNode?.id ?? null}
            onSelectNode={setSelectedNode}
          />
          <FieldGraphColumn
            fields={fields}
            connections={connectionsByNode}
            connectedNodeIds={connectedNodeIds}
            selectedNodeId={selectedNode?.id ?? null}
            onSelectNode={setSelectedNode}
          />
          <FindingGraphColumn
            findings={findings}
            connections={connectionsByNode}
            connectedNodeIds={connectedNodeIds}
            selectedNodeId={selectedNode?.id ?? null}
            onSelectNode={setSelectedNode}
          />
        </div>
      </div>

      {selectedNode && (
        <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-xl bg-slate-900 p-4 text-xs text-slate-100">
          <div className="min-w-0">
            <span className="font-mono text-[10px] uppercase text-blue-400">
              {selectedNode.type}
            </span>
            <div className="mt-0.5 font-bold text-white">{selectedNode.label}</div>
            <pre className="mt-1 max-h-24 overflow-auto font-mono text-[11px] text-slate-300">
              {JSON.stringify(selectedNode.data, null, 2)}
            </pre>
          </div>
          <button
            type="button"
            onClick={() => setSelectedNode(null)}
            className="rounded bg-slate-800 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-700"
          >
            Clear Selection
          </button>
        </div>
      )}
    </div>
  );
};
