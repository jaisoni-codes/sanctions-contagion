import React, { useEffect } from 'react';
import ReactFlow, { Background, Handle, Position, MarkerType, useNodesState, useEdgesState } from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import { CheckCircle2, XCircle } from 'lucide-react';

const getLayoutedElements = (nodes: any[], edges: any[]) => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: 'TB', ranksep: 60, nodesep: 100 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 150, height: 60 });
  });
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });
  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = Position.Top;
    node.sourcePosition = Position.Bottom;
    node.position = { x: nodeWithPosition.x - 150 / 2, y: nodeWithPosition.y - 60 / 2 };
  });

  return { nodes, edges };
};

const CustomNode = ({ data, isConnectable }: any) => {
  const isSeed = data.status === 'seed';
  const isBlocked = data.status === 'blocked';
  let bg = 'bg-neutral-50 border-neutral-300';
  if (isSeed) bg = 'bg-rose-50 border-rose-500';
  else if (isBlocked) bg = 'bg-purple-50 border-purple-500';

  return (
    <div className={`px-2 py-1.5 rounded border-2 min-w-[100px] text-center shadow-sm ${bg}`}>
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} className="w-2 h-2 opacity-0" />
      <div className="font-bold text-xs text-neutral-900">{data.label}</div>
      {isSeed && <div className="text-[9px] font-mono text-rose-700">{data.regime}: {data.list_id}</div>}
      {isBlocked && <div className="text-[9px] font-bold text-purple-700">DERIVED BLOCKED</div>}
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} className="w-2 h-2 opacity-0" />
    </div>
  );
};

const CustomEdge = ({ id, sourceX, sourceY, targetX, targetY, data }: any) => {
  const path = `M${sourceX},${sourceY} C${sourceX},${sourceY + 30} ${targetX},${targetY - 30} ${targetX},${targetY}`;
  const midX = (sourceX + targetX) / 2;
  const midY = (sourceY + targetY) / 2;
  return (
    <>
      <path id={id} className="react-flow__edge-path" d={path} markerEnd="url(#arrow)" strokeWidth={1.5} stroke="#64748b" fill="none" />
      <foreignObject width={60} height={30} x={midX - 30} y={midY - 15} className="overflow-visible">
        <div className="bg-white border border-neutral-200 px-1 py-0.5 rounded text-[9px] font-bold text-center text-neutral-600 m-1">
           {data.pct}%
        </div>
      </foreignObject>
    </>
  );
};

const nodeTypes = { custom: CustomNode };
const edgeTypes = { custom: CustomEdge };

export default function ScenarioGraph({ graph, assertions }: { graph: any, assertions: any[] }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (!graph || !graph.nodes || graph.nodes.length === 0) {
        setNodes([]); setEdges([]); return;
    }
    const initialNodes = graph.nodes.map((n:any) => ({ ...n, type: 'custom' }));
    const initialEdges = graph.edges.map((e:any) => ({ ...e, type: 'custom', animated: true }));
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(initialNodes, initialEdges);
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [graph, setNodes, setEdges]);

  return (
    <div className="flex-1 flex flex-col gap-4 min-h-[400px]">
      <div className="bg-white border border-neutral-200 rounded-lg p-5">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold text-neutral-900">Result Validation</h3>
        </div>
        <div className="space-y-3">
           {assertions && assertions.length > 0 ? assertions.map((a, i) => (
              <div key={i} className={`flex items-center justify-between p-2 rounded border ${a.pass ? 'bg-emerald-50 border-emerald-200' : 'bg-rose-50 border-rose-200'}`}>
                 <div className="flex items-center gap-2">
                    {a.pass ? <CheckCircle2 size={16} className="text-emerald-600"/> : <XCircle size={16} className="text-rose-600"/>}
                    <span className="font-bold text-sm text-neutral-800">{a.name}</span>
                 </div>
                 <div className="text-xs flex gap-4">
                    <span className="text-neutral-500">Expected: <span className="font-bold text-neutral-900">{a.expected}</span></span>
                    <span className="text-neutral-500">Actual: <span className="font-bold text-neutral-900">{a.actual}</span></span>
                 </div>
              </div>
           )) : (
              <p className="text-xs text-neutral-500 italic">Waiting for completion...</p>
           )}
        </div>
      </div>
      
      <div className="flex-1 bg-white border border-neutral-200 rounded-lg overflow-hidden relative shadow-sm">
         {nodes.length > 0 ? (
             <ReactFlow 
                nodes={nodes} 
                edges={edges} 
                nodeTypes={nodeTypes} 
                edgeTypes={edgeTypes} 
                fitView 
                fitViewOptions={{ padding: 0.2 }}
                zoomOnScroll={false}
                panOnDrag={false}
                attributionPosition="bottom-right"
              >
                <Background color="#ccc" gap={16} size={1} />
                <svg>
                  <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
                    </marker>
                  </defs>
                </svg>
             </ReactFlow>
         ) : (
             <div className="absolute inset-0 flex items-center justify-center text-sm text-neutral-400">No graph data available</div>
         )}
      </div>
    </div>
  );
}
