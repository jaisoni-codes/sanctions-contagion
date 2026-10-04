class PolicyCopilot:
    def __init__(self):
        self.allowed_tools = ["policy_search", "get_alert", "get_party", "get_ownership_chain", "audit_lookup"]
        
    def execute_tool(self, tool_name: str, **kwargs):
        if tool_name not in self.allowed_tools:
            return {"error": f"Tool {tool_name} not permitted."}
            
        # Mock tool executions
        if tool_name == "policy_search":
            return {"result": "According to the 50 percent rule, aggregate stakes >= 50% are blocked. [Doc: Policy.md Page 1]"}
        elif tool_name == "get_alert":
            return {"result": f"Alert {kwargs.get('alert_id')} is currently OPEN."}
            
        return {"error": "Tool not implemented in mock"}

    def ask(self, question: str, user_role: str = "analyst"):
        trace = []
        
        # Simple rule-based router for demo
        if "policy" in question.lower() or "50 percent" in question.lower():
            tool_call = {"tool_name": "policy_search", "params": {"query": question}}
            trace.append(tool_call)
            res = self.execute_tool(**tool_call)
            trace.append({"tool_result": res})
            answer = f"Based on the policy search, {res['result']}"
            
        elif "approve" in question.lower() or "clear" in question.lower():
            answer = "I am a copilot and I decline to make or change decisions. I can only provide information."
            
        else:
            answer = "I can only answer questions related to policy or current alerts."
            
        return {
            "answer": answer,
            "trace": trace,
            "citations": ["[Doc: Policy.md Page 1]"] if "policy" in question.lower() else []
        }
