import React, { useMemo } from 'react';
import { EvidenceGraphEdge, EvidenceGraphNode } from '../../api/client';

interface EvidenceGraphMapProps {
  nodes: EvidenceGraphNode[];
  edges: EvidenceGraphEdge[];
  connectedNodeIds: Set<string>;
  selectedNodeId: string | null;
  onSelectNode: (node: EvidenceGraphNode) => void;
}

const lanePositions = {
  documentNode: { x: 16, width: 220 },
  fieldNode: { x: 340, width: 220 },
  findingNode: { x: 664, width: 220 },
} as const;

const laneColors = {
  documentNode: { fill: '#eff6ff', stroke: '#60a5fa', text: '#1d4ed8' },
  fieldNode: { fill: '#ecfdf5', stroke: '#34d399', text: '#047857' },
  findingNode: { fill: '#fff1f2', stroke: '#fb7185', text: '#be123c' },
} as const;

const truncate = (value: string, limit: number) =>
  value.length > limit ? `${value.slice(0, limit - 1)}…` : value;

const getNodeDetails = (node: EvidenceGraphNode) => {
  if (node.type === 'documentNode') {
    return [String(node.data.doc_type ?? 'Source document'), node.label];
  }
  if (node.type === 'fieldNode') {
    return [
      String(node.data.field_key ?? 'Extracted field'),
      String(node.data.raw_value ?? node.label),
    ];
  }
  return [
    String(node.data.rule_code ?? 'Rule finding'),
    `${String(node.data.severity ?? 'Unspecified')} · ${node.label}`,
  ];
};

export const EvidenceGraphMap: React.FC<EvidenceGraphMapProps> = ({
  nodes,
  edges,
  connectedNodeIds,
  selectedNodeId,
  onSelectNode,
}) => {
  const layout = useMemo(() => {
    const nodePositions = new Map<string, { x: number; y: number }>();
    const lanes = {
      documentNode: nodes.filter((node) => node.type === 'documentNode'),
      fieldNode: nodes.filter((node) => node.type === 'fieldNode'),
      findingNode: nodes.filter((node) => node.type === 'findingNode'),
    };

    for (const [type, laneNodes] of Object.entries(lanes) as [
      keyof typeof lanePositions,
      EvidenceGraphNode[],
    ][]) {
      const { x } = lanePositions[type];
      laneNodes.forEach((node, index) => {
        nodePositions.set(node.id, { x, y: 28 + index * 72 });
      });
    }

    const visibleEdges = edges.flatMap((edge) => {
      const source = nodePositions.get(edge.source);
      const target = nodePositions.get(edge.target);
      if (!source || !target) return [];
      return [{ edge, source, target }];
    });

    const maxNodes = Math.max(
      lanes.documentNode.length,
      lanes.fieldNode.length,
      lanes.findingNode.length,
      1,
    );

    return {
      lanes,
      nodePositions,
      visibleEdges,
      height: 48 + maxNodes * 72,
    };
  }, [edges, nodes]);

  const nodeById = useMemo(
    () => new Map(nodes.map((node) => [node.id, node])),
    [nodes],
  );

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-slate-50/70 p-3">
      <svg
        role="img"
        aria-label="Evidence relationship graph connecting source documents, extracted fields, and rule findings"
        viewBox={`0 0 900 ${layout.height}`}
        className="mx-auto block min-w-[780px]"
        style={{ width: '100%', height: 'auto' }}
      >
        <title>Evidence relationship graph</title>
        <desc>
          Lines connect each extracted field to its source document and any associated rule findings.
        </desc>

        <text x="16" y="17" className="fill-blue-800 text-[11px] font-bold">
          SOURCE DOCUMENTS
        </text>
        <text x="340" y="17" className="fill-emerald-800 text-[11px] font-bold">
          EXTRACTED FIELDS
        </text>
        <text x="664" y="17" className="fill-rose-800 text-[11px] font-bold">
          RULE FINDINGS
        </text>

        {layout.visibleEdges.map(({ edge, source, target }) => {
          const sourceNode = nodeById.get(edge.source);
          const targetNode = nodeById.get(edge.target);
          if (!sourceNode || !targetNode) return null;

          const startX = source.x + lanePositions[sourceNode.type].width;
          const endX = target.x;
          const centerX = (startX + endX) / 2;
          const startY = source.y + 25;
          const endY = target.y + 25;
          const path = `M ${startX} ${startY} C ${centerX} ${startY}, ${centerX} ${endY}, ${endX} ${endY}`;
          const isHighlighted =
            selectedNodeId !== null &&
            connectedNodeIds.has(edge.source) &&
            connectedNodeIds.has(edge.target);
          const isSelectedEdge =
            selectedNodeId !== null &&
            (edge.source === selectedNodeId || edge.target === selectedNodeId);
          const stroke =
            edge.label === 'contradicts'
              ? '#e11d48'
              : edge.label === 'flags'
                ? '#d97706'
                : '#2563eb';
          const opacity =
            selectedNodeId === null ? 0.58 : isHighlighted ? 0.88 : 0.12;

          return (
            <g key={edge.id}>
              <path
                d={path}
                fill="none"
                stroke={stroke}
                strokeWidth={isSelectedEdge ? 3 : 1.8}
                strokeOpacity={opacity}
                markerEnd={
                  edge.label === 'contradicts'
                    ? 'url(#arrow-rose)'
                    : edge.label === 'flags'
                      ? 'url(#arrow-amber)'
                      : 'url(#arrow-blue)'
                }
              />
              <text
                x={centerX}
                y={(startY + endY) / 2 - 3}
                textAnchor="middle"
                className="fill-slate-500 text-[9px]"
                opacity={opacity}
              >
                {edge.label}
              </text>
            </g>
          );
        })}

        <defs>
          <marker id="arrow-blue" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
            <path d="M 0 0 L 7 3.5 L 0 7 z" fill="#2563eb" />
          </marker>
          <marker id="arrow-rose" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
            <path d="M 0 0 L 7 3.5 L 0 7 z" fill="#e11d48" />
          </marker>
          <marker id="arrow-amber" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
            <path d="M 0 0 L 7 3.5 L 0 7 z" fill="#d97706" />
          </marker>
        </defs>

        {nodes.map((node) => {
          const position = layout.nodePositions.get(node.id);
          if (!position) return null;

          const lane = lanePositions[node.type];
          const colors = laneColors[node.type];
          const [detail, label] = getNodeDetails(node);
          const isSelected = selectedNodeId === node.id;
          const isConnected = connectedNodeIds.has(node.id);
          const faded = selectedNodeId !== null && !isConnected;

          return (
            <g
              key={node.id}
              role="button"
              tabIndex={0}
              aria-label={`${detail}: ${label}`}
              aria-pressed={isSelected}
              onClick={() => onSelectNode(node)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  onSelectNode(node);
                }
              }}
              className="cursor-pointer outline-none"
              opacity={faded ? 0.35 : 1}
            >
              <title>{`${detail}: ${label}`}</title>
              <rect
                x={position.x}
                y={position.y}
                width={lane.width}
                height="50"
                rx="8"
                fill={colors.fill}
                stroke={isSelected ? '#0f172a' : isConnected ? colors.text : colors.stroke}
                strokeWidth={isSelected ? 2.5 : isConnected ? 2 : 1.2}
              />
              <text
                x={position.x + 10}
                y={position.y + 19}
                className="fill-slate-500 text-[9px] font-semibold"
              >
                {truncate(detail, 34)}
              </text>
              <text
                x={position.x + 10}
                y={position.y + 37}
                className="fill-slate-900 text-[11px] font-bold"
              >
                {truncate(label, 31)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};
