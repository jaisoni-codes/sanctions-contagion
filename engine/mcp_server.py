# Mock MCP (Model Context Protocol) Server for external agents

class SanctionsMCPServer:
    """
    Exposes live analytics tables as tools for an IDE assistant or external agent.
    """
    def __init__(self):
        self.tables = {
            "list_open_alerts": [{"alert_id": "A1", "tier": "STRONG"}],
            "get_latency_stats": {"p50": "45ms", "p95": "120ms"}
        }

    def call_tool(self, tool_name: str, params: dict = None):
        if tool_name == "list_open_alerts":
            return self.tables["list_open_alerts"]
        elif tool_name == "get_latency_stats":
            return self.tables["get_latency_stats"]
        else:
            return {"error": "Unknown MCP tool"}

# This would be wrapped in Pathway's MCP server hook
