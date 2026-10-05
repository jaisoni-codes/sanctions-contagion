import React, { useState, useEffect, useCallback, useMemo } from 'react';
import ReactFlow, { Background, Controls, Handle, Position, MarkerType, useNodesState, useEdgesState } from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';
import { PlayCircle, Search, Sliders } from 'lucide-react';

const getLayoutedElements = (nodes: any[], edges: any[]) => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: 'TB', ranksep: 100, nodesep: 150 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 200, height: 80 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = Position.Top;
    node.sourcePosition = Position.Bottom;
    node.position = {
      x: nodeWithPosition.x - 200 / 2,
      y: nodeWithPosition.y - 80 / 2,
    };
  });

  return { nodes, edges };
};

const FIXTURES: Record<string, any> = {
  direct: {
    name: 'Direct 60%',
    nodes: [
      { id: 'n1', data: { label: 'Rajeev Malhotra', seed: true, list_id: 'OFAC-99002', regime: 'OFAC', status: 'seed' } },
      { id: 'n2', data: { label: 'Malhotra Traders', status: 'blocked' } }
    ],
    edges: [{ id: 'e1', source: 'n1', target: 'n2', data: { pct: 60, doc_type: 'MoA', doc_ref: 'MOA-101' } }],
    rounds: [{ round: 1, text: "Rajeev Malhotra holds 60%", eq: "60 >= 50", target: "Malhotra Traders" }]
  },
  chain: {
    name: 'Chain 60% -> 55%',
    nodes: [
      { id: 'n1', data: { label: 'John Smith', seed: true, list_id: 'UK-8811', regime: 'UK', status: 'seed' } },
      { id: 'n2', data: { label: 'Smith Holdings', status: 'blocked' } },
      { id: 'n3', data: { label: 'Global Freight', status: 'blocked' } }
    ],
    edges: [
      { id: 'e1', source: 'n1', target: 'n2', data: { pct: 60, doc_type: 'AoA', doc_ref: 'AOA-402' } },
      { id: 'e2', source: 'n2', target: 'n3', data: { pct: 55, doc_type: 'registry_filing', doc_ref: 'REG-555' } }
    ],
    rounds: [
      { round: 1, text: "John Smith holds 60%", eq: "60 > 50", target: "Smith Holdings" },
      { round: 2, text: "Smith Holdings holds 55%", eq: "55 > 50", target: "Global Freight" }
    ]
  },
  split: {
    name: 'Split 30% + 25%',
    nodes: [
      { id: 'n1', data: { label: 'Blocked Owner A', seed: true, list_id: 'UN-101', regime: 'UN', status: 'seed' } },
      { id: 'n2', data: { label: 'Blocked Owner B', seed: true, list_id: 'UN-102', regime: 'UN', status: 'seed' } },
      { id: 'n3', data: { label: 'Aggregated Logistics', status: 'blocked' } }
    ],
    edges: [
      { id: 'e1', source: 'n1', target: 'n3', data: { pct: 30, doc_type: 'declaration', doc_ref: 'DEC-900' } },
      { id: 'e2', source: 'n2', target: 'n3', data: { pct: 25, doc_type: 'stock_exchange_report', doc_ref: 'SEC-314' } }
    ],
    rounds: [{ round: 1, text: "Blocked Owner A: 30%, Blocked Owner B: 25%", eq: "30 + 25 = 55 >= 50", target: "Aggregated Logistics" }]
  },
  near_miss: {
    name: 'Near Miss 49.9%',
    nodes: [
      { id: 'n1', data: { label: 'Wei Chen', seed: true, list_id: 'EU-5544', regime: 'EU', status: 'seed' } },
      { id: 'n2', data: { label: 'Chen Exports', status: 'clear' } }
    ],
    edges: [{ id: 'e1', source: 'n1', target: 'n2', data: { pct: 49.9, doc_type: 'registry_filing', doc_ref: 'REG-111' } }],
    rounds: [{ round: 1, text: "Wei Chen holds 49.9%", eq: "49.9 < 50", target: "Chen Exports: CLEAR" }]
  },
  circular: {
    name: 'Circular Ownership',
    nodes: [
      { id: 'n1', data: { label: 'Amit Patel', seed: true, list_id: 'OFAC-7788', regime: 'OFAC', status: 'seed' } },
      { id: 'n2', data: { label: 'Company A', status: 'blocked' } },
      { id: 'n3', data: { label: 'Company B', status: 'blocked' } }
    ],
    edges: [
      { id: 'e1', source: 'n1', target: 'n2', data: { pct: 60, doc_type: 'MoA', doc_ref: 'MOA-201' } },
      { id: 'e2', source: 'n2', target: 'n3', data: { pct: 100, doc_type: 'MoA', doc_ref: 'MOA-202' } },
      { id: 'e3', source: 'n3', target: 'n2', data: { pct: 10, doc_type: 'AoA', doc_ref: 'AOA-301' } }
    ],
    rounds: [
      { round: 1, text: "Amit Patel holds 60%", eq: "60 >= 50", target: "Company A" },
      { round: 2, text: "Company A holds 100%", eq: "100 >= 50", target: "Company B" },
      { round: 3, text: "Cycle detected Company B -> Company A", eq: "Cycle", target: "Terminated" }
    ]
  }
};

const CustomNode = ({ data, isConnectable }: any) => {
  const isSeed = data.status === 'seed';
  const isBlocked = data.status === 'blocked';
  const isClear = data.status === 'clear';
  
  let bg = 'bg-neutral-100 border-neutral-300';
  if (isSeed) bg = 'bg-rose-50 border-rose-600 shadow-[0_0_15px_rgba(225,29,72,0.3)]';
  else if (isBlocked) bg = 'bg-purple-50 border-purple-600 shadow-[0_0_15px_rgba(147,51,234,0.3)]';
  
  return (
    <div className={`px-4 py-3 rounded-lg border-2 min-w-[150px] text-center ${bg}`}>
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} className="w-3 h-3 bg-neutral-400" />
      <div className="font-bold text-sm text-neutral-900">{data.label}</div>
      {isSeed && <div className="text-[10px] font-mono text-rose-700 mt-1">{data.regime}: {data.list_id}</div>}
      {isBlocked && <div className="text-[10px] font-bold text-purple-700 mt-1">DERIVED BLOCKED</div>}
      {isClear && <div className="text-[10px] font-bold text-neutral-500 mt-1">CLEAR</div>}
      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} className="w-3 h-3 bg-neutral-400" />
    </div>
  );
};

const CustomEdge = ({ id, sourceX, sourceY, targetX, targetY, data }: any) => {
  const [isHovered, setIsHovered] = useState(false);
  const path = `M${sourceX},${sourceY} C${sourceX},${sourceY + 50} ${targetX},${targetY - 50} ${targetX},${targetY}`;
  const midX = (sourceX + targetX) / 2;
  const midY = (sourceY + targetY) / 2;

  return (
    <>
      <path id={id} className="react-flow__edge-path" d={path} markerEnd="url(#arrow)" strokeWidth={2} stroke={isHovered ? '#10b981' : '#94a3b8'} fill="none" onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)} />
      <foreignObject width={140} height={60} x={midX - 70} y={midY - 30} className="overflow-visible pointer-events-auto" onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)}>
        <div className="bg-white border text-neutral-900 border-neutral-200 px-2 py-1 rounded text-[10px] font-bold text-center shadow-sm cursor-pointer relative group flex items-center justify-center m-2">
           {data.pct}%
           <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-1 hidden group-hover:block bg-neutral-900 text-white p-2 rounded w-48 text-left z-50">
             <p className="font-bold border-b border-neutral-700 pb-1 mb-1">Source Evidence</p>
             <p className="text-neutral-300">Type: <span className="text-white">{data.doc_type}</span></p>
             <p className="text-neutral-300">Ref: <span className="text-white">{data.doc_ref}</span></p>
           </div>
        </div>
      </foreignObject>
    </>
  );
};

const nodeTypes = { custom: CustomNode };
const edgeTypes = { custom: CustomEdge };

export default function OwnershipExplorer() {
  const [activeFixture, setActiveFixture] = useState('split');
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [rounds, setRounds] = useState<any[]>([]);
  
  useEffect(() => {
    const fixture = FIXTURES[activeFixture];
    const initialNodes = fixture.nodes.map((n:any) => ({ ...n, type: 'custom' }));
    const initialEdges = fixture.edges.map((e:any) => ({ ...e, type: 'custom', animated: true }));
    
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(initialNodes, initialEdges);
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
    setRounds(fixture.rounds);
  }, [activeFixture, setNodes, setEdges]);

  return (
    <div className="flex flex-col gap-4 h-full pb-10">
      <div className="flex justify-between items-center bg-white p-4 border border-neutral-200 rounded-lg shadow-sm">
         <div className="flex gap-4 items-center">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-2.5 text-neutral-400" />
              <input type="text" placeholder="Search party or ID..." className="pl-9 pr-4 py-2 bg-neutral-50 border border-neutral-200 rounded text-sm w-64" />
            </div>
            <select value={activeFixture} onChange={e => setActiveFixture(e.target.value)} className="bg-white border border-neutral-200 rounded p-2 text-sm font-medium">
              {Object.entries(FIXTURES).map(([k, v]) => <option key={k} value={k}>{v.name}</option>)}
            </select>
            <span className="bg-indigo-100/30 text-indigo-700 text-xs px-2 py-1 rounded font-bold">FIXTURE DATA</span>
         </div>
         <div className="flex gap-4 items-center">
            <div className="text-sm font-medium flex items-center gap-2">
              Regime:
              <select className="bg-white border border-neutral-200 rounded p-1 text-sm">
                <option>OFAC (&gt;= 50%)</option>
                <option>EU (&gt; 50%)</option>
                <option>UN (&gt;= 50%)</option>
              </select>
            </div>
            <div className="text-sm font-medium flex items-center gap-2">
              Depth:
              <input type="number" min="1" max="5" defaultValue="3" className="w-12 border border-neutral-200 rounded p-1 text-center" />
            </div>
         </div>
      </div>
      
      <div className="flex-1 flex gap-4 min-h-[500px]">
        <div className="flex-1 bg-white border border-neutral-200 rounded-lg overflow-hidden shadow-sm relative">
          <ReactFlow 
            nodes={nodes} 
            edges={edges} 
            onNodesChange={onNodesChange} 
            onEdgesChange={onEdgesChange} 
            nodeTypes={nodeTypes} 
            edgeTypes={edgeTypes} 
            fitView 
            attributionPosition="bottom-right"
          >
            <Background color="#ccc" gap={16} />
            <Controls />
            <svg>
              <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
                </marker>
              </defs>
            </svg>
          </ReactFlow>
        </div>
        
        <div className="w-80 bg-white border border-neutral-200 rounded-lg p-5 flex flex-col shadow-sm">
           <h3 className="font-semibold text-neutral-900 mb-4 border-b border-neutral-200 pb-2">Why Blocked?</h3>
           
           <div className="flex-1 overflow-y-auto">
              <div className="space-y-4">
                 {rounds.map((r, i) => (
                    <div key={i} className="bg-neutral-50 p-3 rounded border border-neutral-200">
                      <p className="font-bold text-sm text-neutral-900 mb-1">Round {r.round}</p>
                      <p className="text-xs text-neutral-600 mb-2">{r.text}</p>
                      <div className="mt-2 pt-2 border-t border-neutral-200">
                        <p className="font-mono text-[10px] text-purple-700 font-bold bg-purple-100 px-1 rounded inline-block">{r.eq}</p>
                        <p className="text-xs font-bold text-purple-900 mt-1">{r.target}</p>
                      </div>
                    </div>
                 ))}
              </div>
           </div>
           
           <div className="mt-4 pt-4 border-t border-neutral-200 flex flex-col gap-3">
              <div>
                <label className="text-xs font-bold text-neutral-700 flex items-center gap-1 mb-1"><Sliders size={12}/> What-If Simulation</label>
                <div className="flex items-center gap-2">
                  <input type="range" min="0" max="100" defaultValue="55" className="flex-1 accent-indigo-600" />
                  <span className="text-xs font-mono w-8">55%</span>
                </div>
              </div>
              <button className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded flex items-center justify-center gap-2 text-sm transition">
                <PlayCircle size={16} /> Replay Contagion
              </button>
           </div>
        </div>
      </div>
    </div>
  );
}
