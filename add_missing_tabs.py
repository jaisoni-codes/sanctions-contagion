import re

with open('web/src/main.tsx', 'r') as f:
    content = f.read()

new_tabs = """
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
              <div className="bg-white border border-neutral-200 rounded-lg shadow-sm overflow-hidden flex-1">
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
                    <tr className="hover:bg-neutral-50">
                      <td className="p-4 font-mono text-xs">ALT-9921</td>
                      <td className="p-4 font-semibold">Rajeev Malhotra</td>
                      <td className="p-4"><span className="bg-rose-100 text-rose-700 px-2 py-1 rounded text-xs font-bold">DIRECT</span></td>
                      <td className="p-4"><span className="bg-amber-100 text-amber-700 px-2 py-1 rounded text-xs font-bold">OPEN</span></td>
                      <td className="p-4 text-neutral-500">2026-10-05</td>
                      <td className="p-4"><button className="text-emerald-600 font-medium hover:underline">Review</button></td>
                    </tr>
                    <tr className="hover:bg-neutral-50">
                      <td className="p-4 font-mono text-xs">ALT-9922</td>
                      <td className="p-4 font-semibold">Delta Ltd</td>
                      <td className="p-4"><span className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs font-bold">OWNERSHIP</span></td>
                      <td className="p-4"><span className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded text-xs font-bold">CLOSED</span></td>
                      <td className="p-4 text-neutral-500">2026-10-04</td>
                      <td className="p-4"><button className="text-emerald-600 font-medium hover:underline">View</button></td>
                    </tr>
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
"""

content = content.replace("{activeTab === 'Observability' && (", new_tabs + "\n          {activeTab === 'Observability' && (")

with open('web/src/main.tsx', 'w') as f:
    f.write(content)
