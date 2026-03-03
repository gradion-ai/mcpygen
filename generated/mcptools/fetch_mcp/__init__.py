import os

from mcpygen.tool_exec.client import ToolRunner

CLIENT = ToolRunner(
    server_name="fetch_mcp",
    server_params={"command": "uvx", "args": ["mcp-server-fetch"]},
    host=os.environ.get("TOOL_SERVER_HOST", "localhost"),
    port=int(os.environ.get("TOOL_SERVER_PORT", "8900")),
)
