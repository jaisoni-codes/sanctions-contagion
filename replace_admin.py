import re

with open('web/src/main.tsx', 'r') as f:
    content = f.read()

start_idx = content.find("{activeTab === 'Admin' && (")
if start_idx == -1:
    print("Not found")
    exit(1)

end_idx = content.find(")}", start_idx) + 2

dynamic_ui = '''{activeTab === 'Admin' && (
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
)}'''

content = content[:start_idx] + dynamic_ui + content[end_idx:]

with open('web/src/main.tsx', 'w') as f:
    f.write(content)

print('Updated Admin page successfully.')
