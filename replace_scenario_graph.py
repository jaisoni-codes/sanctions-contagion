import re

with open('web/src/main.tsx', 'r') as f:
    content = f.read()

import_line = "import ScenarioGraph from './ScenarioGraph';\n"
if "import ScenarioGraph" not in content:
    content = content.replace("import OwnershipExplorer from './OwnershipExplorer';\n", "import OwnershipExplorer from './OwnershipExplorer';\n" + import_line)

# Replace the Right: Validation & Graph block
start_idx = content.find("{/* Right: Validation & Graph */}")
if start_idx != -1:
    end_idx = content.find("{/* Bottom: Metrics */}")
    
    new_ui = '''{/* Right: Validation & Graph */}
                <ScenarioGraph 
                   graph={currentStepIndex === scenarioSteps.length - 1 ? scenarioSteps[scenarioSteps.length - 1].graph : null} 
                   assertions={currentStepIndex === scenarioSteps.length - 1 ? scenarioSteps[scenarioSteps.length - 1].assertions : null} 
                />
                
                '''
    content = content[:start_idx] + new_ui + content[end_idx:]

# Need to update runScenario to read assertions and graph and attach it to the last step! Wait, in my sim.py I return it as part of the run data, not inside step!
# Let's fix that. In sim.py, I return `{"steps": steps, "assertions": assertions, "graph": graph}`.
# I will attach it to the last step in the frontend or just store it in state.
# I'll store it in state.

state_injection = '''
  const [scenarioAssertions, setScenarioAssertions] = useState<any[]>([])
  const [scenarioGraph, setScenarioGraph] = useState<any>(null)
'''
if "const [scenarioAssertions" not in content:
    content = content.replace("const [scenarioSteps, setScenarioSteps] = useState<any[]>([])", "const [scenarioSteps, setScenarioSteps] = useState<any[]>([])" + state_injection)

# Update runScenario
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

# Update ScenarioGraph props
content = content.replace(
    '''<ScenarioGraph 
                   graph={currentStepIndex === scenarioSteps.length - 1 ? scenarioSteps[scenarioSteps.length - 1].graph : null} 
                   assertions={currentStepIndex === scenarioSteps.length - 1 ? scenarioSteps[scenarioSteps.length - 1].assertions : null} 
                />''',
    '''<ScenarioGraph 
                   graph={currentStepIndex === scenarioSteps.length - 1 ? scenarioGraph : null} 
                   assertions={currentStepIndex === scenarioSteps.length - 1 ? scenarioAssertions : null} 
                />'''
)


with open('web/src/main.tsx', 'w') as f:
    f.write(content)
