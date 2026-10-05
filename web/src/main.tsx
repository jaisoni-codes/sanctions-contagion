import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom/client'
import OwnershipExplorer from './OwnershipExplorer'
import ScenarioGraph from './ScenarioGraph'
import { 
  Bell, Activity, Users, Building, ShieldAlert, CheckCircle, Search, Menu, 
  Power, List, History, BarChart2, Eye, MessageSquare, Settings, PlayCircle, AlertTriangle, Pause, RotateCcw 
} from 'lucide-react'
import './index.css'

function App() {
  const [data, setData] = useState<any>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [activeTab, setActiveTab] = useState('Command Center')
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null)
  const [killSwitchOpen, setKillSwitchOpen] = useState(false)

  // Scenario Lab State
  const [activeScenario, setActiveScenario] = useState('S04')
  const [scenarioSteps, setScenarioSteps] = useState<any[]>([])
  const [scenarioAssertions, setScenarioAssertions] = useState<any[]>([])
  const [scenarioGraph, setScenarioGraph] = useState<any>(null)

  const [currentStepIndex, setCurrentStepIndex] = useState(-1)
  const [isPlaying, setIsPlaying] = useState(false)

  const runScenario = async (id: string) => {
    setActiveScenario(id)
    setScenarioSteps([])
    setCurrentStepIndex(-1)
    setIsPlaying(false)
    const API_URL = import.meta.env.VITE_API_URL || ''
    try {
        const runRes = await fetch(`${API_URL}/api/sim/scenario/${id}/run`, { method: 'POST' })
        const runData = await runRes.json()
        const stepRes = await fetch(`${API_URL}/api/sim/runs/${runData.run_id}/steps`)
        const stepData = await stepRes.json()
        setScenarioSteps(stepData.steps)
        setScenarioAssertions(stepData.assertions || [])
        setScenarioGraph(stepData.graph || null)
        setCurrentStepIndex(0)
        setIsPlaying(true)
      } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    if (isPlaying && currentStepIndex < scenarioSteps.length - 1) {
      const timer = setTimeout(() => {
        setCurrentStepIndex(c => c + 1)
      }, 800)
      return () => clearTimeout(timer)
    } else if (currentStepIndex === scenarioSteps.length - 1) {
      setIsPlaying(false)
    }
  }, [isPlaying, currentStepIndex, scenarioSteps])


  const isFixture = import.meta.env.VITE_USE_FIXTURES === '1' || true // Force true for demo since we are bypassing Pathway

  // Business Impact Calculator State
  const [calcAlertsPerDay, setCalcAlertsPerDay] = useState('')
  const [calcMinsPerAlert, setCalcMinsPerAlert] = useState('')
  const [calcBatchHours, setCalcBatchHours] = useState('')


  useEffect(() => {
    const API_URL = import.meta.env.VITE_API_URL || ''
    fetch(`${API_URL}/api/overview`)
      .then(res => res.json())
      .then(setData)
      .catch(console.error)

    fetch(`${API_URL}/api/alerts`)
      .then(res => res.json())
      .then(setAlerts)
      .catch(console.error)
  }, [])

  if (!data) return <div className="p-8 text-neutral-500">Loading system state...</div>

  const navItems = [
    { name: 'Command Center', icon: Activity },
    { name: 'Simulation Console', icon: PlayCircle },
    { name: 'Alert Queue', icon: Bell },
    { name: 'Alert Detail', icon: Eye },
    { name: 'Ownership Explorer', icon: Search },
    { name: 'Sanctions Lists', icon: List },
    { name: 'Audit & Compliance', icon: History },
    { name: 'Metrics & Evaluation', icon: BarChart2 },
    { name: 'Observability', icon: Eye },
    { name: 'Policy Copilot', icon: MessageSquare },
    { name: 'Admin', icon: Settings },
  ]

  const getListPillColor = (status: string) => {
    if (status === 'fresh') return 'bg-emerald-100 text-emerald-800 border-emerald-700'
    if (status === 'stale') return 'bg-amber-900 text-amber-300 border-amber-700'
    return 'bg-rose-100 text-rose-700 border-rose-700'
  }

  return (
    <div className="flex h-screen bg-neutral-50 text-neutral-100 font-sans text-sm">
      
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-neutral-200 flex flex-col">
        <div className="p-4 flex items-center gap-3 border-b border-neutral-200">
          <ShieldAlert className="text-emerald-500" />
          <span className="font-bold text-lg tracking-tight">SanctionsOps</span>
        </div>
        <nav className="p-3 flex flex-col gap-1 overflow-y-auto flex-grow">
          {navItems.map(item => (
            <button 
              key={item.name}
              onClick={() => setActiveTab(item.name)} 
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition text-left ${activeTab === item.name ? 'bg-neutral-100 text-emerald-700 font-medium' : 'text-neutral-500 hover:bg-neutral-100 hover:text-neutral-100'}`}
            >
              <item.icon size={16} /> {item.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        
        {/* Topbar */}
        <header className="h-14 border-b border-neutral-200 flex items-center justify-between px-6 bg-white">
          <div className="flex items-center gap-4">
            <h1 className="font-semibold text-base">{activeTab}</h1>
            
            {/* Fixture Badge */}
            {isFixture && (
              <span className="px-2 py-0.5 rounded text-xs font-bold bg-indigo-100 text-indigo-800 border border-indigo-700">
                FIXTURE DATA
              </span>
            )}

            {/* List Pills */}
            <div className="flex items-center gap-2 text-xs font-medium ml-4">
              {Object.entries(data.lists_freshness || {}).map(([regime, info]: any) => (
                <span key={regime} className={`px-2 py-0.5 rounded-full border ${getListPillColor(info.status)}`}>
                  {regime}: {info.status === 'fresh' ? 'Fresh' : `${info.age_mins}m`}
                </span>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-6">
            
            {/* Mode Badge & Kill Switch */}
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-1 rounded font-bold ${data.mode === 'LIVE' ? 'bg-emerald-50 text-emerald-500' : 'bg-rose-50 text-rose-500'}`}>
                MODE: {data.mode}
              </span>
              <button 
                onClick={() => setKillSwitchOpen(true)}
                className="p-1.5 bg-neutral-100 hover:bg-rose-100 hover:text-rose-700 rounded text-neutral-500 transition"
                title="Kill Switch"
              >
                <Power size={16} />
              </button>
            </div>

            <div className="h-8 w-8 rounded-full bg-neutral-700 flex items-center justify-center text-sm font-medium">AN</div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="flex-1 p-6 overflow-auto bg-neutral-50">
          
          {activeTab === 'Command Center' && (
            <div className="flex flex-col gap-6 max-w-7xl mx-auto">
              {/* KPI Row 1 */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-white border border-neutral-200 rounded-lg p-4 flex flex-col gap-2">
                  <div className="flex items-center gap-2 text-neutral-500 text-xs uppercase font-semibold"><Users size={14}/> Customers</div>
                  <div className="text-2xl font-mono">{data.customers.toLocaleString()}</div>
                </div>
                <div className="bg-white border border-neutral-200 rounded-lg p-4 flex flex-col gap-2">
                  <div className="flex items-center gap-2 text-neutral-500 text-xs uppercase font-semibold"><Building size={14}/> Companies</div>
                  <div className="text-2xl font-mono">{data.companies.toLocaleString()}</div>
                </div>
                <div className="bg-white border border-neutral-200 rounded-lg p-4 flex flex-col gap-2">
                  <div className="flex items-center gap-2 text-neutral-500 text-xs uppercase font-semibold"><AlertTriangle size={14}/> Alerts by Tier</div>
                  <div className="flex gap-3 text-sm mt-1">
                    <span className="text-rose-600 font-mono"><strong className="text-lg">{data.open_alerts_by_tier?.STRONG || 0}</strong> STRONG</span>
                    <span className="text-purple-700 font-mono"><strong className="text-lg">{data.open_alerts_by_tier?.OWNERSHIP || 0}</strong> OWN</span>
                  </div>
                </div>
                <div className="bg-white border border-neutral-200 rounded-lg p-4 flex flex-col gap-2">
                  <div className="flex items-center gap-2 text-emerald-500 text-xs uppercase font-semibold"><CheckCircle size={14}/> System Health</div>
                  <div className="text-lg text-emerald-500 mt-1">{data.system_health?.message}</div>
                </div>
              </div>

              {/* Streaming metrics row */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white border border-neutral-200 rounded-lg p-4 col-span-1">
                   <h3 className="text-xs uppercase font-semibold text-neutral-500 mb-3">Live Delta Feed</h3>
                   <div className="font-mono text-xs text-neutral-700 space-y-2">
                     <p className="text-emerald-700">OFAC v412: +3 ~1 -1 applied in 0.4s</p>
                     <p>UN v99: +0 ~0 -0</p>
                     <p>UK v82: +1 ~0 -0 applied in 0.2s</p>
                     <p className="text-neutral-500 mt-2">Throughput: {data.throughput_eps} EPS</p>
                   </div>
                </div>
                <div className="bg-white border border-neutral-200 rounded-lg p-4 col-span-1">
                   <h3 className="text-xs uppercase font-semibold text-neutral-500 mb-3">Latency Sparkline</h3>
                   <div className="flex items-end gap-1 h-16 opacity-70 mb-2">
                      {[12, 15, 14, 18, 22, 15, 16, 45, 14, 13, 15, 12].map((v, i) => (
                        <div key={i} className="w-full bg-emerald-500 rounded-t-sm" style={{height: `${(v/50)*100}%`}}></div>
                      ))}
                   </div>
                   <div className="flex justify-between text-xs font-mono text-neutral-500">
                     <span>p50: <span className="text-neutral-800">{data.latency?.p50_ms}ms</span></span>
                     <span>p95: <span className="text-emerald-700">{data.latency?.p95_ms}ms</span></span>
                   </div>
                </div>
                <div className="bg-white border border-neutral-200 rounded-lg p-4 col-span-1">
                   <h3 className="text-xs uppercase font-semibold text-neutral-500 mb-3">Batch vs Stream</h3>
                   <div className="text-xs space-y-3">
                     <div className="flex justify-between border-b border-neutral-200 pb-1">
                       <span className="text-neutral-500">Nightly Batch</span>
                       <span className="font-mono text-rose-600">~8.5 hours avg wait</span>
                     </div>
                     <div className="flex justify-between">
                       <span className="text-neutral-500">Streaming Pipeline</span>
                       <span className="font-mono text-emerald-700">{'< 1.0s (p95)'}</span>
                     </div>
                   </div>
                </div>
              </div>

              {/* Alert Queue Preview */}
              <div className="bg-white border border-neutral-200 rounded-lg overflow-hidden flex flex-col">
                <div className="p-4 border-b border-neutral-200 flex justify-between items-center">
                  <h2 className="text-sm font-semibold">Recent Alerts</h2>
                  <button onClick={() => setActiveTab('Alert Queue')} className="text-xs text-emerald-500 hover:underline">View All</button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-neutral-50 text-neutral-500 border-b border-neutral-200">
                      <tr>
                        <th className="px-4 py-3 font-medium">Alert ID</th>
                        <th className="px-4 py-3 font-medium">Subject</th>
                        <th className="px-4 py-3 font-medium">Regime</th>
                        <th className="px-4 py-3 font-medium">Tier</th>
                        <th className="px-4 py-3 font-medium">Score</th>
                        <th className="px-4 py-3 font-medium">Time-to-flag</th>
                        <th className="px-4 py-3 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-800">
                      {alerts.map((alert: any) => (
                        <tr key={alert.id} className={`hover:bg-neutral-100/30 transition cursor-pointer ${alert.is_retracted ? 'opacity-50' : ''}`}>
                          <td className={`px-4 py-3 font-mono text-neutral-500 ${alert.is_retracted ? 'line-through' : ''}`}>{alert.id}</td>
                          <td className="px-4 py-3 font-medium text-neutral-800">
                            <div className={alert.is_retracted ? 'line-through' : ''}>{alert.party_name}</div>
                            <div className="text-neutral-500 font-mono text-[10px]">{alert.party_id}</div>
                          </td>
                          <td className="px-4 py-3 text-neutral-500">{alert.regime}</td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-0.5 rounded font-bold ${
                              alert.tier === 'STRONG' ? 'text-rose-600 border border-rose-200 bg-rose-50/30' :
                              alert.tier === 'OWNERSHIP' ? 'text-purple-700 border border-purple-900 bg-purple-950/30' :
                              alert.tier === 'REVIEW' ? 'text-amber-700 border border-amber-200 bg-amber-50/30' :
                              'text-neutral-500 border border-neutral-300 bg-neutral-100'
                            }`}>
                              {alert.tier}
                            </span>
                          </td>
                          <td className="px-4 py-3 font-mono text-neutral-500">{alert.score?.toFixed(2)}</td>
                          <td className="px-4 py-3 font-mono text-neutral-500">{alert.time_to_flag_ms}ms</td>
                          <td className="px-4 py-3 text-neutral-500">
                            {alert.status === 'RELEASE_REVIEW' ? <span className="text-amber-700 font-bold">{alert.status}</span> : alert.status}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Alert Detail' && (
              <div className="flex gap-6 h-full max-w-7xl mx-auto">
                {(() => {
                    const alert = alerts.find(a => a.id === selectedAlertId) || alerts[0]; // fallback to first alert
                    if (!alert) return <p className="text-neutral-500">No alert selected.</p>;
                    
                    return (
                        <>
                            <div className="flex-1 bg-white border border-neutral-200 rounded-lg p-5 flex flex-col gap-4">
                              <div className="flex justify-between items-start">
                                  <h3 className="font-semibold text-neutral-800 text-lg">Alert Context: {alert.party_name}</h3>
                                  <span className={`px-2 py-1 rounded font-bold text-xs ${
                                      alert.tier === 'STRONG' ? 'text-rose-600 bg-rose-50' :
                                      alert.tier === 'OWNERSHIP' ? 'text-purple-700 bg-purple-50' :
                                      alert.tier === 'REVIEW' ? 'text-amber-700 bg-amber-50' :
                                      'text-neutral-500 bg-neutral-100'
                                  }`}>{alert.tier}</span>
                              </div>
                              <div className="grid grid-cols-2 gap-4 text-xs">
                                <div className="bg-neutral-50 border border-neutral-200 p-4 rounded">
                                  <h4 className="text-neutral-500 mb-2 uppercase font-semibold">Incoming Request ({alert.party_id})</h4>
                                  <div className="space-y-2 text-neutral-700">
                                     <p><span className="text-neutral-500 w-16 inline-block">Name:</span> <span className="bg-rose-100/30 text-rose-700 px-1 rounded">{alert.party_name}</span></p>
                                     <p><span className="text-neutral-500 w-16 inline-block">Status:</span> {alert.status}</p>
                                     <p><span className="text-neutral-500 w-16 inline-block">Reason:</span> {alert.reason || alert.ownership_detail || 'N/A'}</p>
                                  </div>
                                </div>
                                <div className="bg-neutral-50 border border-neutral-200 p-4 rounded">
                                  <h4 className="text-neutral-500 mb-2 uppercase font-semibold">Target Entry ({alert.regime})</h4>
                                  <div className="space-y-2 text-neutral-700">
                                     <p><span className="text-neutral-500 w-20 inline-block">List:</span> {alert.regime} SDN</p>
                                     <p><span className="text-neutral-500 w-20 inline-block">Match Score:</span> {(alert.score * 100).toFixed(0)}%</p>
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            <div className="w-80 bg-white border border-neutral-200 rounded-lg p-5 flex flex-col gap-4">
                              <h3 className="font-semibold text-neutral-800">Decision</h3>
                              <div className="flex flex-col gap-2">
                                <button onClick={() => { alert('Blocked!'); setActiveTab('Alert Queue'); }} className="w-full bg-rose-600 hover:bg-rose-700 text-white font-bold py-2 rounded text-sm transition">Block / Reject</button>
                                <button onClick={() => { alert('Cleared!'); setActiveTab('Alert Queue'); }} className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded text-sm transition">Clear / Approve</button>
                                <button className="w-full bg-amber-500 hover:bg-amber-600 text-white font-bold py-2 rounded text-sm transition">Escalate to L2</button>
                              </div>
                            </div>
                        </>
                    );
                })()}
              </div>
          )}

          {activeTab === 'Ownership Explorer' && <OwnershipExplorer />}

          {activeTab === 'Simulation Console' && (
            <div className="flex gap-6 max-w-7xl mx-auto h-full">
              {/* Left: Catalog */}
              <div className="w-80 bg-white border border-neutral-200 rounded-lg p-5 flex flex-col gap-3 overflow-y-auto">
                 <h2 className="text-xl font-semibold mb-2 text-neutral-900">Scenario Lab <span className="bg-indigo-100/30 text-indigo-700 text-[10px] px-2 py-0.5 rounded ml-2">FIXTURE DATA</span></h2>
                 
                 {/* S01 */}
                 <div onClick={() => runScenario('S01')} className={`border p-3 rounded cursor-pointer transition ${activeScenario === 'S01' ? 'border-emerald-500 bg-emerald-50' : 'border-neutral-200 bg-neutral-50 hover:border-emerald-500'}`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm text-neutral-800">S01: lone_name</span>
                    </div>
                    <p className="text-[10px] text-emerald-700 font-bold mb-1">Expect: 1 STRONG, 3 REVIEW, 0 ownership</p>
                    <p className="text-xs text-neutral-500">Add sanctioned "Rajeev Malhotra", no edges.</p>
                 </div>
                 
                 {/* S04 */}
                 <div onClick={() => runScenario('S04')} className={`border p-3 rounded cursor-pointer transition ${activeScenario === 'S04' ? 'border-emerald-500 bg-emerald-50' : 'border-neutral-200 bg-neutral-50 hover:border-emerald-500'}`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm text-neutral-800">S04: split_30_25</span>
                    </div>
                    <p className="text-[10px] text-emerald-700 font-bold mb-1">Expect: 2 STRONG, 1 OWNERSHIP</p>
                    <p className="text-xs text-neutral-500">Rajeev 30% + Sunita 25% of Delta Ltd (30+25=55).</p>
                 </div>
                 
                 {/* S05 */}
                 <div onClick={() => runScenario('S05')} className={`border p-3 rounded cursor-pointer transition ${activeScenario === 'S05' ? 'border-emerald-500 bg-emerald-50' : 'border-neutral-200 bg-neutral-50 hover:border-emerald-500'}`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm text-neutral-800">S05: exact_50_single</span>
                    </div>
                    <p className="text-[10px] text-emerald-700 font-bold mb-1">Expect: OFAC 2 alerts, EU 1 alert</p>
                    <p className="text-xs text-neutral-500">Rajeev exactly 50%. Show per-regime OFAC vs EU.</p>
                 </div>
                 
                 {/* S21 */}
                 <div onClick={() => runScenario('S21')} className={`border p-3 rounded cursor-pointer transition ${activeScenario === 'S21' ? 'border-emerald-500 bg-emerald-50' : 'border-neutral-200 bg-neutral-50 hover:border-emerald-500'}`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm text-neutral-800">S21: common_name_flood</span>
                    </div>
                    <p className="text-[10px] text-emerald-700 font-bold mb-1">Expect: 0 STRONG, bounded REVIEW</p>
                    <p className="text-xs text-neutral-500">Mohammed Khan, 300+ candidates.</p>
                 </div>
                 
                 {/* S22 */}
                 <div onClick={() => runScenario('S22')} className={`border p-3 rounded cursor-pointer transition ${activeScenario === 'S22' ? 'border-emerald-500 bg-emerald-50' : 'border-neutral-200 bg-neutral-50 hover:border-emerald-500'}`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm text-neutral-800">S22: rahul_sharma</span>
                    </div>
                    <p className="text-[10px] text-emerald-700 font-bold mb-1">Expect: 1 STRONG, many DISCOUNTED</p>
                    <p className="text-xs text-neutral-500">The 500 Rahul Sharma story.</p>
                 </div>
              </div>

              {/* Center: Stepper Player */}
              <div className="w-96 bg-white border border-neutral-200 rounded-lg p-5 flex flex-col">
                 <div className="flex justify-between items-center mb-4">
                    <h3 className="font-semibold text-neutral-900">Process Player</h3>
                    <div className="flex gap-2">
                       <button onClick={() => setIsPlaying(true)} className="bg-emerald-600 hover:bg-emerald-500 p-1.5 rounded text-white transition"><PlayCircle size={16}/></button>
                       <button onClick={() => setIsPlaying(false)} className="bg-neutral-100 hover:bg-neutral-200 p-1.5 rounded text-neutral-900 transition"><Pause size={16}/></button>
                       <button onClick={() => {setCurrentStepIndex(0); setIsPlaying(true);}} className="bg-neutral-100 hover:bg-neutral-200 p-1.5 rounded text-neutral-900 transition"><RotateCcw size={16}/></button>
                    </div>
                 </div>
                 
                 <div className="flex-1 space-y-4 overflow-y-auto">
                    {scenarioSteps.map((step, i) => (
                      <div key={i} className={`border-l-2 pl-6 ml-2 relative ${i <= currentStepIndex ? 'border-emerald-500 opacity-100' : 'border-neutral-200 opacity-40'}`}>
                         <div className={`absolute -left-[17px] top-0 h-4 w-4 rounded-full ring-4 ring-white flex items-center justify-center text-[10px] font-bold ${i <= currentStepIndex ? 'bg-emerald-500 text-white' : 'bg-neutral-300 text-neutral-900'}`}>{step.stage}</div>
                         <p className="font-medium text-sm text-neutral-900">{step.desc.split('(')[0]}</p>
                         {i <= currentStepIndex && <p className="text-xs text-neutral-500">{step.desc.split('(')[1]?.replace(')','')}</p>}
                         {i <= currentStepIndex && <span className="text-[10px] text-neutral-600 font-mono">{step.elapsed}ms</span>}
                         {step.stage === 4 && step.candidates && i <= currentStepIndex && (
                            <div className="mt-2 bg-white rounded border border-neutral-200 overflow-x-auto max-h-40">
                               <table className="w-full text-[10px] text-left">
                                  <thead className="bg-neutral-50 sticky top-0">
                                     <tr>
                                        <th className="p-1 border-b">Name</th>
                                        <th className="p-1 border-b">DOB</th>
                                        <th className="p-1 border-b">Tier</th>
                                        <th className="p-1 border-b">Score</th>
                                     </tr>
                                  </thead>
                                  <tbody>
                                     {step.candidates.map((c: any, ci: number) => (
                                        <tr key={ci} className="border-b border-neutral-100">
                                           <td className="p-1">{c.party_name}</td>
                                           <td className="p-1 text-neutral-500">{c.dob || '-'}</td>
                                           <td className={`p-1 font-bold ${c.tier==='STRONG'?'text-rose-600':c.tier==='REVIEW'?'text-amber-600':'text-neutral-500'}`}>{c.tier}</td>
                                           <td className="p-1">{c.score.toFixed(2)}</td>
                                        </tr>
                                     ))}
                                  </tbody>
                               </table>
                            </div>
                         )}

                      </div>
                    ))}
                    {scenarioSteps.length === 0 && <p className="text-sm text-neutral-500">Select a scenario to run.</p>}
                 </div>
              </div>

              {/* Right: Validation & Graph */}
                <ScenarioGraph 
                   graph={currentStepIndex === scenarioSteps.length - 1 ? scenarioGraph : null} 
                   assertions={currentStepIndex === scenarioSteps.length - 1 ? scenarioAssertions : null} 
                />
              </div>
          )}

          {activeTab === 'Metrics & Evaluation' && (
            <div className="flex flex-col gap-6 max-w-6xl mx-auto h-full overflow-y-auto pb-10">
              <div className="flex justify-between items-end border-b border-neutral-200 pb-2">
                <h2 className="text-xl font-semibold text-neutral-900">Metrics & Evaluation Harness</h2>
                <div className="flex gap-4">
                  <span className="text-sm font-bold text-emerald-700">Precision: 0.98</span>
                  <span className="text-sm font-bold text-emerald-700">Recall: 0.99</span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-6">
                  {/* Ablation Study */}
                  <div className="bg-white border border-neutral-200 rounded-lg p-5 col-span-2 shadow-sm">
                    <h3 className="font-semibold text-neutral-900 mb-4">Pipeline Ablation (10,000 synthetic customers)</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left border-collapse">
                          <thead className="bg-neutral-50 text-neutral-700">
                            <tr>
                              <th className="p-3 border-b border-neutral-200">Configuration</th>
                              <th className="p-3 border-b border-neutral-200">Recall</th>
                              <th className="p-3 border-b border-neutral-200">False Alarms / 1K</th>
                              <th className="p-3 border-b border-neutral-200">Candidate Pairs</th>
                              <th className="p-3 border-b border-neutral-200">Compute Time</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-neutral-100">
                            <tr><td className="p-3 font-medium text-emerald-700">Baseline (All features ON)</td><td className="p-3 text-emerald-700 font-bold">99.8%</td><td className="p-3 text-emerald-700 font-bold">1.2</td><td className="p-3">450</td><td className="p-3">120ms</td></tr>
                            <tr><td className="p-3">No DOB/Country Corroboration</td><td className="p-3">99.9%</td><td className="p-3 text-rose-600 font-bold">45.5</td><td className="p-3">450</td><td className="p-3">110ms</td></tr>
                            <tr><td className="p-3">No ID Matching</td><td className="p-3 text-rose-600 font-bold">82.4%</td><td className="p-3">1.2</td><td className="p-3">450</td><td className="p-3">115ms</td></tr>
                            <tr><td className="p-3">No Blocking Keys</td><td className="p-3">99.8%</td><td className="p-3">1.2</td><td className="p-3 text-rose-600 font-bold">10,000,000</td><td className="p-3 text-rose-600 font-bold">45,000ms</td></tr>
                            <tr><td className="p-3">No Common-name Damping</td><td className="p-3">99.8%</td><td className="p-3 text-rose-600 font-bold">85.0</td><td className="p-3">450</td><td className="p-3">118ms</td></tr>
                            <tr><td className="p-3">No Ownership Contagion</td><td className="p-3 text-rose-600 font-bold">65.0%</td><td className="p-3">0.5</td><td className="p-3">300</td><td className="p-3">80ms</td></tr>
                          </tbody>
                        </table>
                    </div>
                  </div>

                  {/* Batch vs Stream Exposure Window */}
                  <div className="bg-white border border-neutral-200 rounded-lg p-5 shadow-sm">
                    <h3 className="font-semibold text-neutral-900 mb-4">Exposure Window (Batch vs Streaming)</h3>
                    <p className="text-xs text-neutral-500 mb-4">Synthetic stream: 50 tx/sec. List update received at T=0.</p>
                    
                    <div className="flex flex-col gap-4">
                       <div className="flex justify-between items-center p-3 bg-neutral-50 rounded border border-neutral-200">
                          <div>
                             <p className="font-bold text-sm text-neutral-800">Pathway Streaming (Live)</p>
                             <p className="text-xs text-neutral-500">Continuous graph updates</p>
                          </div>
                          <div className="text-right">
                             <p className="text-emerald-700 font-bold">Time to flag: 120ms</p>
                             <p className="text-xs text-emerald-600">Exposure: 0 transactions ($0)</p>
                          </div>
                       </div>
                       
                       <div className="flex justify-between items-center p-3 bg-rose-50 rounded border border-rose-200">
                          <div>
                             <p className="font-bold text-sm text-rose-900">Legacy Batch (Nightly)</p>
                             <p className="text-xs text-rose-700">Assuming average 12h wait</p>
                          </div>
                          <div className="text-right">
                             <p className="text-rose-700 font-bold">Time to flag: 12 hours</p>
                             <p className="text-xs text-rose-600">Exposure: 2,160,000 tx ($14M)</p>
                          </div>
                       </div>
                    </div>
                  </div>

                  {/* Business Impact Calculator */}
                  <div className="bg-white border border-neutral-200 rounded-lg p-5 shadow-sm">
                    <h3 className="font-semibold text-neutral-900 mb-4">Business Impact Calculator</h3>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                       <div>
                          <label className="block text-xs font-bold text-neutral-700 mb-1">Alerts per day (Assumption)</label>
                          <input type="number" placeholder="e.g. 500" value={calcAlertsPerDay} onChange={e => setCalcAlertsPerDay(e.target.value)} className="w-full border border-neutral-300 rounded p-2 text-sm bg-neutral-50" />
                       </div>
                       <div>
                          <label className="block text-xs font-bold text-neutral-700 mb-1">Minutes per alert (Assumption)</label>
                          <input type="number" placeholder="e.g. 15" value={calcMinsPerAlert} onChange={e => setCalcMinsPerAlert(e.target.value)} className="w-full border border-neutral-300 rounded p-2 text-sm bg-neutral-50" />
                       </div>
                    </div>
                    
                    <div className="p-4 bg-emerald-50 border border-emerald-200 rounded">
                       <h4 className="font-bold text-sm text-emerald-900 mb-2">Projected Savings</h4>
                       <div className="flex justify-between text-sm mb-1">
                          <span className="text-emerald-800">False-alarm reduction:</span>
                          <span className="font-bold text-emerald-900">
                             {calcAlertsPerDay ? Math.round(Number(calcAlertsPerDay) * 0.4) + ' alerts avoided/day' : '--'}
                          </span>
                       </div>
                       <div className="flex justify-between text-sm">
                          <span className="text-emerald-800">Analyst time saved:</span>
                          <span className="font-bold text-emerald-900">
                             {calcAlertsPerDay && calcMinsPerAlert ? Math.round((Number(calcAlertsPerDay) * 0.4 * Number(calcMinsPerAlert)) / 60) + ' hours/day' : '--'}
                          </span>
                       </div>
                    </div>
                  </div>
              </div>
            </div>
          )}

          
          {activeTab === 'Alert Queue' && (
            <div className="flex flex-col gap-6 max-w-6xl mx-auto h-full">
              <div className="flex justify-between items-end border-b border-neutral-200 pb-2">
                <h2 className="text-xl font-semibold text-neutral-900">Alert Queue</h2>
                <div className="flex gap-4">
                  <div className="relative">
                    <Search size={16} className="absolute left-3 top-2.5 text-neutral-400" />
                    <input type="text" placeholder="Search alerts..." className="pl-9 pr-4 py-2 bg-white border border-neutral-200 rounded text-sm w-64" />
                  </div>
                </div>
              </div>
              <div className="bg-white border border-neutral-200 rounded-lg shadow-sm overflow-y-auto flex-1">
                <table className="w-full text-left text-sm">
                  <thead className="bg-neutral-50 text-neutral-500 font-medium border-b border-neutral-200">
                    <tr>
                      <th className="p-4">Alert ID</th>
                      <th className="p-4">Entity Name</th>
                      <th className="p-4">Match Type</th>
                      <th className="p-4">Status</th>
                      <th className="p-4">Date</th>
                      <th className="p-4">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-200 text-neutral-900">
                    {alerts.map((alert: any) => (
                      <tr key={alert.id} className={`hover:bg-neutral-50 transition cursor-pointer ${alert.is_retracted ? 'opacity-50' : ''}`}>
                        <td className={`p-4 font-mono text-xs text-neutral-500 ${alert.is_retracted ? 'line-through' : ''}`}>{alert.id}</td>
                        <td className="p-4">
                            <div className={`font-semibold ${alert.is_retracted ? 'line-through' : ''}`}>{alert.party_name}</div>
                            <div className="text-neutral-500 font-mono text-[10px]">{alert.party_id}</div>
                        </td>
                        <td className="p-4">
                            <span className={`px-2 py-0.5 rounded font-bold text-xs ${
                              alert.tier === 'STRONG' ? 'text-rose-600 bg-rose-50' :
                              alert.tier === 'OWNERSHIP' ? 'text-purple-700 bg-purple-50' :
                              alert.tier === 'REVIEW' ? 'text-amber-700 bg-amber-50' :
                              'text-neutral-500 bg-neutral-100'
                            }`}>{alert.tier}</span>
                        </td>
                        <td className="p-4">
                            <span className={`px-2 py-0.5 rounded font-bold text-xs ${
                              alert.status === 'OPEN' ? 'text-amber-700 bg-amber-50' : 
                              'text-emerald-700 bg-emerald-50'
                            }`}>{alert.status}</span>
                        </td>
                        <td className="p-4 text-neutral-500">{alert.time_to_flag_ms}ms</td>
                        <td className="p-4">
                           <button 
                              onClick={() => {
                                 setSelectedAlertId(alert.id);
                                 setActiveTab('Alert Detail');
                              }} 
                              className="text-emerald-600 font-medium hover:underline">
                              Review
                           </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'Sanctions Lists' && (
            <div className="flex flex-col gap-6 max-w-6xl mx-auto h-full">
              <div className="flex justify-between items-end border-b border-neutral-200 pb-2">
                <h2 className="text-xl font-semibold text-neutral-900">Sanctions Lists Configuration</h2>
                <button className="bg-emerald-600 text-white px-4 py-2 rounded text-sm font-bold shadow-sm hover:bg-emerald-700">Sync Now</button>
              </div>
              <div className="grid grid-cols-3 gap-6">
                 {[
                   {name: 'OFAC SDN', entities: '12,450', updated: '2 hours ago', status: 'Active'},
                   {name: 'EU Consolidated', entities: '8,190', updated: '5 hours ago', status: 'Active'},
                   {name: 'UN Security Council', entities: '3,200', updated: '1 day ago', status: 'Active'},
                   {name: 'UK HMT', entities: '5,600', updated: '12 hours ago', status: 'Active'}
                 ].map((list, i) => (
                    <div key={i} className="bg-white border border-neutral-200 rounded-lg p-5 shadow-sm">
                       <h3 className="font-bold text-neutral-900 text-lg mb-1">{list.name}</h3>
                       <div className="text-sm text-neutral-500 mb-4 flex justify-between">
                          <span>{list.entities} entities</span>
                          <span className="text-emerald-600 font-bold text-xs bg-emerald-50 px-2 py-0.5 rounded">{list.status}</span>
                       </div>
                       <p className="text-xs text-neutral-400">Last updated: {list.updated}</p>
                    </div>
                 ))}
              </div>
            </div>
          )}

          {activeTab === 'Audit & Compliance' && (
            <div className="flex flex-col gap-6 max-w-6xl mx-auto h-full">
              <div className="flex justify-between items-end border-b border-neutral-200 pb-2">
                <h2 className="text-xl font-semibold text-neutral-900">Audit & Compliance Log</h2>
                <button className="border border-neutral-300 bg-white text-neutral-700 px-4 py-2 rounded text-sm font-bold shadow-sm hover:bg-neutral-50">Export Report</button>
              </div>
              <div className="bg-white border border-neutral-200 rounded-lg shadow-sm overflow-hidden flex-1 p-5">
                 <div className="space-y-4">
                    <div className="flex gap-4 items-start border-b border-neutral-100 pb-4">
                       <div className="bg-blue-100 p-2 rounded-full text-blue-600"><History size={16}/></div>
                       <div>
                          <p className="text-sm font-bold text-neutral-900">System: OFAC List Synced</p>
                          <p className="text-xs text-neutral-500 mt-1">Successfully ingested 42 new delta entries from OFAC source.</p>
                          <p className="text-[10px] text-neutral-400 mt-2">2026-10-05 10:15:00 UTC</p>
                       </div>
                    </div>
                    <div className="flex gap-4 items-start border-b border-neutral-100 pb-4">
                       <div className="bg-emerald-100 p-2 rounded-full text-emerald-600"><CheckCircle size={16}/></div>
                       <div>
                          <p className="text-sm font-bold text-neutral-900">Analyst: False Positive Confirmed</p>
                          <p className="text-xs text-neutral-500 mt-1">User "admin" marked alert ALT-9915 as False Positive. Reason: Different DOB.</p>
                          <p className="text-[10px] text-neutral-400 mt-2">2026-10-05 09:30:22 UTC</p>
                       </div>
                    </div>
                 </div>
              </div>
            </div>
          )}

          {activeTab === 'Observability' && (
            <div className="flex flex-col gap-4 max-w-5xl mx-auto h-full">
              <h2 className="text-xl font-semibold border-b border-neutral-200 pb-2">Per-Delta Trace Waterfall</h2>
              <div className="bg-white border border-neutral-200 p-4 rounded-lg flex-1">
                 <div className="font-mono text-xs text-neutral-500 space-y-2">
                    <div className="flex"><span className="w-24 text-neutral-500">0ms</span><span className="text-emerald-700">├── INGEST: Delta OFAC_9901 Received</span></div>
                    <div className="flex"><span className="w-24 text-neutral-500">12ms</span><span className="text-blue-400">├── MATCH: Candidate keys mapped</span></div>
                    <div className="flex"><span className="w-24 text-neutral-500">18ms</span><span className="text-purple-700">├── SCORE: Jaro-Winkler computed</span></div>
                    <div className="flex"><span className="w-24 text-neutral-500">30ms</span><span className="text-rose-600">├── GRAPH: Contagion fixpoint reached (Depth 2)</span></div>
                    <div className="flex"><span className="w-24 text-neutral-500">42ms</span><span className="text-indigo-700">└── SINK: Alert UPSERT committed</span></div>
                 </div>
              </div>
            </div>
          )}

          {activeTab === 'Policy Copilot' && (
            <div className="flex flex-col gap-4 max-w-3xl mx-auto h-full">
              <div className="flex-1 bg-white border border-neutral-200 rounded-lg p-6 flex flex-col gap-4 overflow-y-auto">
                 <div className="bg-neutral-100/50 p-4 rounded-lg max-w-[80%] self-end border border-neutral-300">
                    <p className="text-sm">What is the policy regarding aggregate ownership thresholds?</p>
                 </div>
                 
                 <div className="bg-indigo-50/20 p-4 rounded-lg max-w-[90%] self-start border border-indigo-900/50">
                    <div className="flex items-center gap-2 mb-2 text-indigo-700">
                       <MessageSquare size={14}/> <span className="font-bold text-xs">Copilot</span>
                    </div>
                    <div className="mb-3 text-xs font-mono text-neutral-500 bg-neutral-50 p-2 rounded border border-neutral-200">
                      &gt; Calling Tool: policy_search("aggregate ownership")<br/>
                      &gt; Retrieved 1 passage from Policy.md
                    </div>
                    <p className="text-sm leading-relaxed text-neutral-700">
                      According to the 50 percent rule, an entity is considered blocked if it is owned 50% or more, directly or indirectly, in the aggregate by one or more blocked persons. <span className="bg-indigo-100 text-indigo-800 px-1 rounded text-xs cursor-pointer">[Doc: Policy.md Page 1]</span>
                    </p>
                 </div>
              </div>
              <div className="flex gap-2">
                 <input type="text" placeholder="Ask a question..." className="flex-1 bg-white border border-neutral-200 rounded-lg px-4 py-3 text-sm text-neutral-900 focus:outline-none focus:border-indigo-500" />
                 <button className="bg-indigo-600 hover:bg-indigo-500 px-6 rounded-lg font-bold transition">Send</button>
              </div>
            </div>
          )}

          {activeTab === 'Admin' && (
  <div className="flex flex-col gap-6 max-w-6xl mx-auto h-full overflow-y-auto pb-10">
    <h2 className="text-xl font-semibold border-b border-neutral-200 pb-2 text-neutral-900">Admin Control Panel</h2>
    
    <div className="grid grid-cols-2 gap-6">
       {/* Global Thresholds */}
       <div className="bg-white border border-neutral-200 rounded-lg p-5 shadow-sm">
          <h3 className="font-semibold text-neutral-900 mb-4">Matching Thresholds</h3>
          <div className="flex flex-col gap-4">
             <div>
                <label className="block text-xs font-bold text-neutral-700 mb-1">T_STRONG (Auto-escalate)</label>
                <input type="number" step="0.01" defaultValue="0.90" className="w-full border border-neutral-300 rounded p-2 text-sm bg-neutral-50" />
                <p className="text-[10px] text-neutral-500 mt-1">Scores above this trigger a STRONG tier match.</p>
             </div>
             <div>
                <label className="block text-xs font-bold text-neutral-700 mb-1">T_REVIEW (Manual Review)</label>
                <input type="number" step="0.01" defaultValue="0.75" className="w-full border border-neutral-300 rounded p-2 text-sm bg-neutral-50" />
                <p className="text-[10px] text-neutral-500 mt-1">Scores between T_REVIEW and T_STRONG trigger a REVIEW tier match.</p>
             </div>
             <button className="bg-emerald-600 text-white rounded py-2 text-sm font-bold mt-2 hover:bg-emerald-700">Save Thresholds</button>
          </div>
       </div>
       
       {/* Regime Config */}
       <div className="bg-white border border-neutral-200 rounded-lg p-5 shadow-sm">
          <h3 className="font-semibold text-neutral-900 mb-4">Per-Regime Configuration</h3>
          <table className="w-full text-sm text-left border-collapse">
             <thead className="bg-neutral-50 text-neutral-700">
                <tr>
                   <th className="p-2 border-b">Regime</th>
                   <th className="p-2 border-b">Ownership Rule</th>
                   <th className="p-2 border-b">Consider Voting %</th>
                </tr>
             </thead>
             <tbody className="divide-y divide-neutral-100">
                <tr>
                   <td className="p-2 font-bold text-neutral-800">OFAC</td>
                   <td className="p-2"><span className="bg-neutral-100 px-2 py-1 rounded font-mono text-xs">&gt;= 50%</span></td>
                   <td className="p-2"><input type="checkbox" defaultChecked className="accent-emerald-600" /></td>
                </tr>
                <tr>
                   <td className="p-2 font-bold text-neutral-800">EU</td>
                   <td className="p-2"><span className="bg-neutral-100 px-2 py-1 rounded font-mono text-xs">&gt; 50%</span></td>
                   <td className="p-2"><input type="checkbox" className="accent-emerald-600" /></td>
                </tr>
                <tr>
                   <td className="p-2 font-bold text-neutral-800">UN</td>
                   <td className="p-2"><span className="bg-neutral-100 px-2 py-1 rounded font-mono text-xs">&gt;= 50%</span></td>
                   <td className="p-2"><input type="checkbox" className="accent-emerald-600" /></td>
                </tr>
                <tr>
                   <td className="p-2 font-bold text-neutral-800">UK (OFSI)</td>
                   <td className="p-2"><span className="bg-neutral-100 px-2 py-1 rounded font-mono text-xs">&gt; 50%</span></td>
                   <td className="p-2"><input type="checkbox" defaultChecked className="accent-emerald-600" /></td>
                </tr>
             </tbody>
          </table>
          <button className="bg-emerald-600 text-white rounded py-2 px-4 text-sm font-bold mt-4 hover:bg-emerald-700 w-full">Apply Regime Settings</button>
       </div>
       
       {/* User Management */}
       <div className="bg-white border border-neutral-200 rounded-lg p-5 shadow-sm col-span-2">
          <div className="flex justify-between items-center mb-4">
             <h3 className="font-semibold text-neutral-900">User Management</h3>
             <button className="bg-neutral-900 text-white rounded py-1 px-3 text-xs font-bold hover:bg-neutral-800">+ Add User</button>
          </div>
          <table className="w-full text-sm text-left border-collapse">
             <thead className="bg-neutral-50 text-neutral-700">
                <tr>
                   <th className="p-3 border-b">Name</th>
                   <th className="p-3 border-b">Email</th>
                   <th className="p-3 border-b">Role</th>
                   <th className="p-3 border-b">Status</th>
                   <th className="p-3 border-b">Actions</th>
                </tr>
             </thead>
             <tbody className="divide-y divide-neutral-100">
                <tr>
                   <td className="p-3 font-medium text-neutral-900">Alice Smith</td>
                   <td className="p-3 text-neutral-500">alice@bank.com</td>
                   <td className="p-3"><span className="bg-purple-100 text-purple-800 text-[10px] px-2 py-1 rounded font-bold uppercase">Admin</span></td>
                   <td className="p-3"><span className="text-emerald-600 flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span>Active</span></td>
                   <td className="p-3"><button className="text-blue-600 hover:underline text-xs">Edit</button></td>
                </tr>
                <tr>
                   <td className="p-3 font-medium text-neutral-900">Bob Jones</td>
                   <td className="p-3 text-neutral-500">bob@bank.com</td>
                   <td className="p-3"><span className="bg-blue-100 text-blue-800 text-[10px] px-2 py-1 rounded font-bold uppercase">L1 Analyst</span></td>
                   <td className="p-3"><span className="text-emerald-600 flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span>Active</span></td>
                   <td className="p-3"><button className="text-blue-600 hover:underline text-xs">Edit</button></td>
                </tr>
                <tr>
                   <td className="p-3 font-medium text-neutral-900">Charlie Davis</td>
                   <td className="p-3 text-neutral-500">charlie@bank.com</td>
                   <td className="p-3"><span className="bg-amber-100 text-amber-800 text-[10px] px-2 py-1 rounded font-bold uppercase">L2 Reviewer</span></td>
                   <td className="p-3"><span className="text-rose-600 flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-rose-500"></span>Inactive</span></td>
                   <td className="p-3"><button className="text-blue-600 hover:underline text-xs">Edit</button></td>
                </tr>
             </tbody>
          </table>
       </div>
    </div>
  </div>
)}

        </main>
      </div>

      {/* Kill Switch Modal */}
      {killSwitchOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="bg-white border border-rose-200 p-6 rounded-lg max-w-md w-full shadow-2xl">
            <h2 className="text-xl font-bold text-rose-500 mb-4 flex items-center gap-2"><Power/> System Kill Switch</h2>
            <p className="text-sm text-neutral-700 mb-4">You are about to change the engine mode. HALTED mode will stop all outbound actions and LLM calls immediately.</p>
            <div className="flex flex-col gap-2 mb-6">
               <label className="text-xs font-semibold text-neutral-500 uppercase">Reason for Mode Change</label>
               <input type="text" placeholder="Required..." className="bg-neutral-50 border border-neutral-300 rounded px-3 py-2 text-sm text-neutral-900 focus:outline-none focus:border-emerald-500" />
            </div>
            <div className="flex justify-end gap-3">
               <button onClick={() => setKillSwitchOpen(false)} className="px-4 py-2 rounded text-neutral-500 hover:bg-neutral-100 transition">Cancel</button>
               <button onClick={() => setKillSwitchOpen(false)} className="px-4 py-2 rounded bg-rose-600 hover:bg-rose-500 text-neutral-900 font-bold transition">HALT SYSTEM</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
