# Tool server

ToolServer is a local server that manages stdio MCP servers and connects to remote streamable HTTP or SSE servers. MCP servers are started on demand and cached for subsequent calls. The generated [tool APIs](https://gradion-ai.github.io/mcpygen/apigen/index.md) delegate tool calls to the tool server for execution.

```
from mcpygen import ToolServer

async with ToolServer(port=8900) as server:
    await server.join()
```

## ToolRunner

The generated tool APIs use ToolRunner internally to communicate with the tool server. `ToolRunner` sends HTTP requests to the tool server, which executes the MCP tool and returns the result.

```
from mcpygen import ToolRunner

runner = ToolRunner(
    server_name="brave_search",
    server_params={
        "command": "npx",
        "args": ["-y", "@brave/brave-search-mcp-server"],
        "env": {"BRAVE_API_KEY": "${BRAVE_API_KEY}"},
    },
)

result = runner.run_sync(
    tool_name="brave_web_search",
    tool_args={"query": "MCP"},
)
```
