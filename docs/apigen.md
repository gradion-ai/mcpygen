# Python tool API generation

[`generate_mcp_sources()`][mcpygen.apigen.generate_mcp_sources] generates a typed Python tool API from MCP server tool schemas. Each tool becomes a module with a Pydantic `Params` class, a `run()` function, and either a typed `Result` class or a `str` return type. A `Result` class is generated when the tool schema defines an output schema; otherwise `run()` returns `str`.

## Stdio servers

For MCP servers that run as local processes, specify `command`, `args`, and optional `env`:

```python
from pathlib import Path

from mcpygen import generate_mcp_sources

server_params = {
    "command": "npx",
    "args": ["-y", "@brave/brave-search-mcp-server"],
    "env": {"BRAVE_API_KEY": "${BRAVE_API_KEY}"},
}

await generate_mcp_sources("brave_search", server_params, Path("mcptools"))
```

## Remote servers

For remote MCP servers, specify `url` and optional `headers`:

```python
server_params = {
    "url": "https://api.githubcopilot.com/mcp/",
    "headers": {"Authorization": "Bearer ${GITHUB_TOKEN}"},
}

await generate_mcp_sources("github", server_params, Path("mcptools"))
```

mcpygen auto-detects the transport type from the URL. URLs containing `/mcp` use streamable HTTP, URLs containing `/sse` use SSE. To override, set `type` to `"streamable_http"` or `"sse"`.

## Environment variable substitution

`${VAR_NAME}` placeholders in `server_params` values are replaced with the corresponding environment variable on the tool server.

## Generated package structure

The Brave Search MCP server example above generates a package structure like this:

```
mcptools/
└── brave_search/
    ├── __init__.py
    ├── brave_web_search.py
    ├── brave_local_search.py
    ├── brave_image_search.py
    └── ...
```

Each MCP server tool gets its own Python module. For example, the [fetch MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) produces the following tool module (slightly modified for readability, [source](https://github.com/gradion-ai/mcpygen/blob/main/docs/generated/mcptools/fetch_mcp/fetch.py)):

```python
--8<-- "docs/generated/mcptools/fetch_mcp/fetch.py"
```

The generated package [\_\_init\_\_.py](https://github.com/gradion-ai/mcpygen/blob/main/docs/generated/mcptools/fetch_mcp/__init__.py) configures a [`ToolRunner`][mcpygen.tool_exec.client.ToolRunner] that connects to a [tool server](toolserver.md).

## Using the generated API

```python
from mcptools.brave_search.brave_image_search import Params, Result, run

# Params validates input
params = Params(query="neural topic models", count=3)

# run() calls the MCP tool and returns a Result (or str for untyped tools)
result: Result = run(params)

for image in result.items:
    print(image.title)
```

A running [tool server](toolserver.md) is required for executing tool calls.

## Async API generation

By default, `generate_mcp_sources()` generates synchronous `run()` functions that use `ToolRunner.run_sync()`. Pass `async_api=True` to generate async functions instead:

```python
await generate_mcp_sources(
    "fetch_mcp", server_params, Path("mcptools"), async_api=True
)
```

This produces `async def run()` functions that use `await ToolRunner.run()` ([source](https://github.com/gradion-ai/mcpygen/blob/main/docs/generated/mcptools/fetch_mcp/fetch_async.py)):

```python
--8<-- "docs/generated/mcptools/fetch_mcp/fetch_async.py:run"
```

Use the async API with `await`:

```python
from mcptools.fetch_mcp.fetch import Params, run

result = await run(Params(url="https://example.com"))
```

## Tool server connection

The generated API connects to a tool server at `localhost:8900` by default. Override the host and port with environment variables:

| Variable | Default | Description |
|---|---|---|
| `TOOL_SERVER_HOST` | `localhost` | Tool server hostname |
| `TOOL_SERVER_PORT` | `8900` | Tool server port |
