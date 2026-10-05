import re

with open('web/src/main.tsx', 'r') as f:
    content = f.read()

import_line = "import ScenarioGraph from './ScenarioGraph';\n"
if "import ScenarioGraph" not in content:
    content = content.replace("import OwnershipExplorer from './OwnershipExplorer';\n", "import OwnershipExplorer from './OwnershipExplorer';\n" + import_line)

start_idx = content.find("{/* Right: Validation & Graph */}")
end_str = "            </div>\n          )} " # Where activeTab === 'Simulation Console' ends
# Wait, actually it's easier to find the exact block end.
# Look for: {activeTab === 'Metrics & Evaluation' && (
end_idx = content.find("{activeTab === 'Metrics & Evaluation'")
if end_idx != -1:
    # We need to backtrack to the closing tag of Simulation Console.
    # It's usually `</div>\n          )}\n\n          {activeTab === 'Metrics'`.
    block_end = content.rfind("</div>\n          )}", start_idx, end_idx)
    if block_end != -1:
        new_ui = '''{/* Right: Validation & Graph */}
                <ScenarioGraph 
                   graph={currentStepIndex === scenarioSteps.length - 1 ? scenarioGraph : null} 
                   assertions={currentStepIndex === scenarioSteps.length - 1 ? scenarioAssertions : null} 
                />
              '''
        content = content[:start_idx] + new_ui + content[block_end:]
    else:
        print("Could not find block end")


state_injection = '''
  const [scenarioAssertions, setScenarioAssertions] = useState<any[]>([])
  const [scenarioGraph, setScenarioGraph] = useState<any>(null)
'''
if "const [scenarioAssertions" not in content:
    content = content.replace("const [scenarioSteps, setScenarioSteps] = useState<any[]>([])", "const [scenarioSteps, setScenarioSteps] = useState<any[]>([])" + state_injection)

run_update = '''
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
'''
content = re.sub(r'try \{\s*const runRes = await fetch\(`\$\{API_URL\}/api/sim/scenario/\$\{id\}/run`, \{ method: \'POST\' \}\)\s*const runData = await runRes\.json\(\)\s*const stepRes = await fetch\(`\$\{API_URL\}/api/sim/runs/\$\{runData\.run_id\}/steps`\)\s*const stepData = await stepRes\.json\(\)\s*setScenarioSteps\(stepData\.steps\)\s*setCurrentStepIndex\(0\)\s*setIsPlaying\(true\)\s*\} catch \(e\) \{', run_update.strip(), content, flags=re.DOTALL)


with open('web/src/main.tsx', 'w') as f:
    f.write(content)
