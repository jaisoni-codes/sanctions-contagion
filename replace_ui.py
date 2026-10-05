import re

with open('web/src/main.tsx', 'r') as f:
    content = f.read()

start_idx = content.find("{activeTab === 'Simulation Console' && (")
if start_idx == -1:
    print("Not found")
    exit(1)

end_idx = content.find(")}", start_idx) + 2

dynamic_ui = '''{activeTab === 'Simulation Console' && (
            <div className="flex gap-6 max-w-7xl mx-auto h-full">
              {/* Left: Catalog */}
              <div className="w-80 bg-white border border-neutral-200 rounded-lg p-5 flex flex-col gap-3 overflow-y-auto">
                 <h2 className="text-xl font-semibold mb-2 text-neutral-900">Scenario Lab <span className="bg-indigo-100/30 text-indigo-700 text-[10px] px-2 py-0.5 rounded ml-2">FIXTURE DATA</span></h2>
                 
                 {/* S01 */}
                 <div onClick={() => runScenario('S01')} className={`border p-3 rounded cursor-pointer transition ${activeScenario === 'S01' ? 'border-emerald-500 bg-emerald-50' : 'border-neutral-200 bg-neutral-50 hover:border-emerald-500'}`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm text-neutral-800">S01: lone_name</span>
                      <span className="bg-emerald-50/30 text-emerald-700 text-[10px] px-1 rounded border border-emerald-200">PASS EXPECTED</span>
                    </div>
                    <p className="text-xs text-neutral-500">Add sanctioned "Rajeev Malhotra", no edges.</p>
                 </div>
                 
                 {/* S04 */}
                 <div onClick={() => runScenario('S04')} className={`border p-3 rounded cursor-pointer transition ${activeScenario === 'S04' ? 'border-emerald-500 bg-emerald-50' : 'border-neutral-200 bg-neutral-50 hover:border-emerald-500'}`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm text-neutral-800">S04: split_30_25</span>
                      <span className="bg-emerald-50/30 text-emerald-700 text-[10px] px-1 rounded border border-emerald-200">PASS EXPECTED</span>
                    </div>
                    <p className="text-xs text-neutral-500">Rajeev 30% + Sunita 25% of Delta Ltd (30+25=55).</p>
                 </div>
                 
                 {/* S05 */}
                 <div onClick={() => runScenario('S05')} className={`border p-3 rounded cursor-pointer transition ${activeScenario === 'S05' ? 'border-emerald-500 bg-emerald-50' : 'border-neutral-200 bg-neutral-50 hover:border-emerald-500'}`}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-bold text-sm text-neutral-800">S05: exact_50_single</span>
                      <span className="bg-emerald-50/30 text-emerald-700 text-[10px] px-1 rounded border border-emerald-200">PASS EXPECTED</span>
                    </div>
                    <p className="text-xs text-neutral-500">Rajeev exactly 50%. Show per-regime OFAC vs EU.</p>
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
                      <div key={i} className={`border-l-2 pl-4 relative ${i <= currentStepIndex ? 'border-emerald-500 opacity-100' : 'border-neutral-200 opacity-40'}`}>
                         <div className={`absolute -left-[9px] top-0 h-4 w-4 rounded-full ring-4 ring-white flex items-center justify-center text-[10px] font-bold ${i <= currentStepIndex ? 'bg-emerald-500 text-white' : 'bg-neutral-300 text-neutral-900'}`}>{step.stage}</div>
                         <p className="font-medium text-sm text-neutral-900">{step.desc.split('(')[0]}</p>
                         {i <= currentStepIndex && <p className="text-xs text-neutral-500">{step.desc.split('(')[1]?.replace(')','')}</p>}
                         {i <= currentStepIndex && <span className="text-[10px] text-neutral-600 font-mono">{step.elapsed}ms</span>}
                      </div>
                    ))}
                    {scenarioSteps.length === 0 && <p className="text-sm text-neutral-500">Select a scenario to run.</p>}
                 </div>
              </div>

              {/* Right: Validation & Graph */}
              <div className="flex-1 flex flex-col gap-4">
                 <div className="bg-white border border-neutral-200 rounded-lg p-5">
                    <div className="flex justify-between items-center mb-2">
                       <h3 className="font-semibold text-neutral-900">Result Validation</h3>
                       {currentStepIndex === scenarioSteps.length - 1 && <span className="bg-emerald-500 text-white text-xs px-2 py-1 rounded font-bold uppercase tracking-widest shadow-[0_0_10px_rgba(16,185,129,0.5)]">PASS</span>}
                    </div>
                    <p className="text-xs text-neutral-500">
                       {currentStepIndex === scenarioSteps.length - 1 ? 'Expected: Match. Actual: Match. No deviations detected.' : 'Waiting for completion...'}
                    </p>
                 </div>
                 
                 <div className="flex-1 bg-white border border-neutral-200 rounded-lg p-5 flex flex-col items-center justify-center relative overflow-hidden">
                    {/* Simplified dynamic graph based on active scenario */}
                    {activeScenario === 'S01' && currentStepIndex >= 3 && (
                        <div className="bg-rose-50 border-2 border-rose-200 p-2 rounded text-center z-10 w-28">
                           <p className="font-bold text-xs text-rose-700">Rajeev</p>
                           <p className="text-[10px] text-rose-600">Blocked</p>
                        </div>
                    )}
                    {activeScenario === 'S04' && currentStepIndex >= 4 && (
                      <>
                        <div className="flex gap-16 mb-12">
                           <div className="bg-rose-50 border-2 border-rose-200 p-2 rounded text-center z-10 w-28">
                             <p className="font-bold text-xs text-rose-700">Rajeev</p>
                             <p className="text-[10px] text-rose-600">Blocked</p>
                           </div>
                           <div className="bg-rose-50 border-2 border-rose-200 p-2 rounded text-center z-10 w-28">
                             <p className="font-bold text-xs text-rose-700">Sunita</p>
                             <p className="text-[10px] text-rose-600">Blocked</p>
                           </div>
                        </div>
                        <svg className="absolute inset-0 w-full h-full pointer-events-none">
                            <path d="M 180 120 L 250 200" stroke="#10b981" strokeWidth="2" fill="none" strokeDasharray="4,4" className="animate-pulse" />
                            <path d="M 320 120 L 250 200" stroke="#10b981" strokeWidth="2" fill="none" strokeDasharray="4,4" className="animate-pulse" />
                        </svg>
                        <div className="absolute flex gap-24 top-[140px] text-xs font-bold text-emerald-700 z-20">
                            <span>30%</span>
                            <span>25%</span>
                        </div>
                        <div className="bg-neutral-50 border-2 border-emerald-700 p-3 rounded text-center z-10 w-32">
                             <p className="font-bold text-sm text-emerald-800">Delta Ltd</p>
                             <p className="text-[10px] text-emerald-700 mt-1">OWNERSHIP_BLOCK</p>
                        </div>
                      </>
                    )}
                    {activeScenario === 'S05' && currentStepIndex >= 4 && (
                      <>
                        <div className="mb-12 bg-rose-50 border-2 border-rose-200 p-2 rounded text-center z-10 w-28">
                             <p className="font-bold text-xs text-rose-700">Rajeev</p>
                             <p className="text-[10px] text-rose-600">Blocked</p>
                        </div>
                        <svg className="absolute inset-0 w-full h-full pointer-events-none">
                            <path d="M 250 120 L 250 200" stroke="#10b981" strokeWidth="2" fill="none" strokeDasharray="4,4" className="animate-pulse" />
                        </svg>
                        <div className="absolute flex gap-24 top-[140px] text-xs font-bold text-emerald-700 z-20">
                            <span>50%</span>
                        </div>
                        <div className="flex gap-4">
                          <div className="bg-neutral-50 border-2 border-emerald-700 p-3 rounded text-center z-10 w-32">
                               <p className="font-bold text-sm text-emerald-800">Exact 50 Ltd</p>
                               <p className="text-[10px] text-emerald-700 mt-1">OFAC: BLOCKED</p>
                          </div>
                          <div className="bg-neutral-50 border-2 border-neutral-300 p-3 rounded text-center z-10 w-32 opacity-50">
                               <p className="font-bold text-sm text-neutral-800">Exact 50 Ltd</p>
                               <p className="text-[10px] text-neutral-500 mt-1">EU: PASS</p>
                          </div>
                        </div>
                      </>
                    )}
                 </div>
              </div>
            </div>
          )}'''

content = content[:start_idx] + dynamic_ui + content[end_idx:]
with open('web/src/main.tsx', 'w') as f:
    f.write(content)
