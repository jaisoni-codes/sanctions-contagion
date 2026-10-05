import re

with open('web/src/main.tsx', 'r') as f:
    content = f.read()

# Add states
states_str = """
  // Alert Integration State
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null)
  const [externalNotifications, setExternalNotifications] = useState<any[]>([])
  const [alertDetails, setAlertDetails] = useState<any>(null)

  useEffect(() => {
      const interval = setInterval(async () => {
          try {
             const API_URL = import.meta.env.VITE_API_URL || ''
             const res = await fetch(`${API_URL}/api/alerts/latest-external`)
             const newNotifs = await res.json()
             if (newNotifs && newNotifs.length > 0) {
                 setExternalNotifications(prev => [...prev, ...newNotifs])
             }
          } catch(e) {}
      }, 3000)
      return () => clearInterval(interval)
  }, [])

  useEffect(() => {
     if (activeTab === 'Alert Detail' && selectedAlertId) {
         const API_URL = import.meta.env.VITE_API_URL || ''
         fetch(`${API_URL}/api/alerts/${selectedAlertId}`)
           .then(res => res.json())
           .then(data => setAlertDetails(data))
     }
  }, [activeTab, selectedAlertId])
  
  const handleDecision = async (decision: string) => {
      if (!selectedAlertId) return;
      const API_URL = import.meta.env.VITE_API_URL || ''
      await fetch(`${API_URL}/api/alerts/${selectedAlertId}/decision`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({decision, reason: "Manual Action"})
      })
      alert(`Alert ${decision.toLowerCase()} successfully!`);
      setActiveTab('Alert Queue');
  }
"""
if "selectedAlertId" not in content:
    content = content.replace("const [killSwitchOpen, setKillSwitchOpen] = useState(false)", "const [killSwitchOpen, setKillSwitchOpen] = useState(false)\n" + states_str)

# Replace Alert Detail UI
alert_detail_ui = """
          {activeTab === 'Alert Detail' && (
              <div className="flex gap-6 h-full max-w-7xl mx-auto">
                <div className="flex-1 bg-white border border-neutral-200 rounded-lg p-5 flex flex-col gap-4">
                  <h3 className="font-semibold text-neutral-800">Alert Context</h3>
                  {alertDetails ? (
                      <div className="grid grid-cols-2 gap-4 text-xs">
                        <div className="bg-neutral-50 border border-neutral-200 p-4 rounded">
                          <h4 className="text-neutral-500 mb-2 uppercase font-semibold">Incoming Request ({alertDetails.party_id})</h4>
                          <div className="space-y-2 text-neutral-700">
                             <p><span className="text-neutral-500 w-16 inline-block">Name:</span> <span className="bg-rose-100/30 text-rose-700 px-1 rounded">{alertDetails.party_name}</span></p>
                             <p><span className="text-neutral-500 w-16 inline-block">Tier:</span> {alertDetails.tier}</p>
                             <p><span className="text-neutral-500 w-16 inline-block">Status:</span> {alertDetails.status}</p>
                             <p><span className="text-neutral-500 w-16 inline-block">Reason:</span> {alertDetails.reason}</p>
                          </div>
                        </div>
                        <div className="bg-neutral-50 border border-neutral-200 p-4 rounded">
                          <h4 className="text-neutral-500 mb-2 uppercase font-semibold">Target Entry ({alertDetails.regime})</h4>
                          <div className="space-y-2 text-neutral-700">
                             <p><span className="text-neutral-500 w-20 inline-block">List:</span> {alertDetails.regime} SDN</p>
                             <p><span className="text-neutral-500 w-20 inline-block">Match Score:</span> {(alertDetails.score * 100).toFixed(0)}%</p>
                          </div>
                        </div>
                      </div>
                  ) : (
                      <p className="text-sm text-neutral-500">No alert selected or loading...</p>
                  )}
                </div>
                
                <div className="w-80 bg-white border border-neutral-200 rounded-lg p-5 flex flex-col gap-4">
                  <h3 className="font-semibold text-neutral-800">Decision</h3>
                  <div className="flex flex-col gap-2">
                    <button onClick={() => handleDecision('CONFIRM')} className="w-full bg-rose-600 hover:bg-rose-700 text-white font-bold py-2 rounded text-sm transition">Block / Reject</button>
                    <button onClick={() => handleDecision('REJECT')} className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded text-sm transition">Clear / Approve</button>
                    <button onClick={() => handleDecision('ESCALATE')} className="w-full bg-amber-500 hover:bg-amber-600 text-white font-bold py-2 rounded text-sm transition">Escalate to L2</button>
                  </div>
                </div>
              </div>
          )}
"""

# Need to replace the old Alert Detail block
start_idx = content.find("{activeTab === 'Alert Detail' && (")
if start_idx != -1:
    end_idx = content.find("{activeTab === 'Ownership Explorer' && <OwnershipExplorer />}")
    if end_idx != -1:
        content = content[:start_idx] + alert_detail_ui + content[end_idx:]


# Add Notifications overlay at the very bottom
overlay = """
      </div>

      {/* Global Notifications */}
      <div className="fixed bottom-6 right-6 flex flex-col gap-3 z-50">
         {externalNotifications.map((notif, idx) => (
             <div key={idx} className="bg-white border-l-4 border-rose-500 rounded shadow-lg p-4 w-80 flex flex-col gap-2">
                <div className="flex justify-between items-start">
                   <div className="flex items-center gap-2 text-rose-600 font-bold">
                      <AlertTriangle size={16} /> New External Alert
                   </div>
                   <button onClick={() => setExternalNotifications(prev => prev.filter((_, i) => i !== idx))} className="text-neutral-400 hover:text-neutral-600">×</button>
                </div>
                <p className="text-sm font-semibold text-neutral-800">{notif.name}</p>
                <p className="text-xs text-neutral-500">Triggered: {notif.scenario_id}</p>
                <button onClick={() => {
                    setSelectedAlertId(notif.alert_id);
                    setActiveTab('Alert Detail');
                    setExternalNotifications(prev => prev.filter((_, i) => i !== idx));
                }} className="mt-2 w-full bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold py-1.5 rounded text-xs transition">
                   Review Alert
                </button>
             </div>
         ))}
      </div>
    </div>
"""
# Replace final </div></div>
content = re.sub(r'      </div>\s*</div>\s*$', overlay, content)

with open('web/src/main.tsx', 'w') as f:
    f.write(content)
