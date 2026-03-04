# mcpygen

mcpygen generates typed Python APIs from MCP server tool schemas. Tool calls made through the generated APIs are executed on a local tool server that manages MCP server connections.

## Features

| Feature | Description |
| --- | --- |
| **API generation** | Generate typed Python tool APIs from MCP server schemas. Each tool becomes a module with a Pydantic `Params` model and a `run()` function. Tools that provide an output schema also get a typed `Result` model. |
| **Tool server** | Local server that manages stdio MCP servers and connects to remote streamable HTTP or SSE servers |
| **Approval workflow** | Gate tool calls with a WebSocket-based approval channel before execution |
