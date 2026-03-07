# Quickstart

## How it works

mcpygen has three parts:

1. **Generate**: connect to an MCP server, discover its tools, and produce a typed Python package with `Params` models and `run()` functions.
1. **Serve**: a local tool server manages stdio MCP server processes and proxies remote HTTP/SSE MCP servers.
1. **Call**: generated `run()` functions send requests to the tool server, which delegates to the actual MCP server and returns results.

The tool server creates and connects to MCP servers on demand and keeps them running for subsequent calls.

## Generate a typed tool API

```
from pathlib import Path

from mcpygen import generate_mcp_sources

server_params = {
    "command": "uvx",
    "args": ["mcp-server-fetch"],
}

await generate_mcp_sources("fetch_mcp", server_params, Path("mcptools"))
```

This generates a Python package under `mcptools/fetch_mcp/` with one module per tool, each containing a `Params` class and a `run()` function. Pass `async_api=True` to generate async functions instead (see [Async API generation](https://gradion-ai.github.io/mcpygen/apigen/#async-api-generation)).

## Start a tool server

A running [tool server](https://gradion-ai.github.io/mcpygen/toolserver/index.md) is required before calling the generated tool APIs.

```
from mcpygen import ToolServer

async with ToolServer() as server:
    await server.join()
```

Or from the command line:

```
mcpygen toolserver
```

## Use the generated API

With a tool server running, call the generated `run()` function:

```
from mcptools.fetch_mcp.fetch import Params, run

result = run(Params(url="https://example.com"))
```

For async usage, pass `async_api=True` when generating and `await` the result:

```
result = await run(Params(url="https://example.com"))
```

See [Async API generation](https://gradion-ai.github.io/mcpygen/apigen/#async-api-generation) for details.

## Custom tool server port

By default, the tool server listens on port 8900. To use a different port:

```
mcpygen toolserver --port 9000
```

Set the `TOOL_SERVER_PORT` environment variable so the generated APIs connect to the same port:

```
export TOOL_SERVER_PORT=9000
```
