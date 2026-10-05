import re

with open('web/src/main.tsx', 'r') as f:
    content = f.read()

# Fix clipped badge: change -left-[9px] to -left-[25px] or add ml-4 to the container
content = content.replace('border-l-2 pl-4 relative', 'border-l-2 pl-6 ml-2 relative')
content = content.replace('-left-[9px]', '-left-[17px]')

# Add S22 and S23 to the UI list and change "PASS EXPECTED"
# Let's replace the whole Catalog section
start_cat = content.find('{/* Left: Catalog */}')
end_cat = content.find('{/* Center: Stepper Player */}')

new_cat = '''{/* Left: Catalog */}
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

              '''

content = content[:start_cat] + new_cat + content[end_cat:]

# Add candidates table for stage 4
table_injection = '''
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
'''
# Find where to inject table
desc_line = '{i <= currentStepIndex && <span className="text-[10px] text-neutral-600 font-mono">{step.elapsed}ms</span>}'
content = content.replace(desc_line, desc_line + table_injection)

with open('web/src/main.tsx', 'w') as f:
    f.write(content)
