# Python tool API generation

generate_mcp_sources() generates a typed Python tool API from MCP server tool schemas. Each tool becomes a module with a Pydantic `Params` class, a `run()` function, and either a typed `Result` class or a `str` return type. A `Result` class is generated when the tool schema defines an output schema; otherwise `run()` returns `str`.

## Stdio servers

For MCP servers that run as local processes, specify `command`, `args`, and optional `env`:

```
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

```
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

```
from typing import Optional

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, conint

from . import CLIENT


class Params(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
    )
    url: AnyUrl = Field(..., title="Url")
    """
    URL to fetch
    """
    max_length: Optional[conint(lt=1000000, gt=0)] = Field(5000, title="Max Length")
    """
    Maximum number of characters to return.
    """
    start_index: Optional[conint(ge=0)] = Field(0, title="Start Index")
    """
    On return output starting at this character index.
    """
    raw: Optional[bool] = Field(False, title="Raw")
    """
    Get the actual HTML content of the requested page, without simplification.
    """


def run(params: Params) -> str:
    """Fetches a URL from the internet and extracts its contents as markdown."""
    return CLIENT.run_sync(tool_name="fetch", tool_args=params.model_dump(exclude_none=True))
```

The generated package [__init__.py](https://github.com/gradion-ai/mcpygen/blob/main/docs/generated/mcptools/fetch_mcp/__init__.py) configures a ToolRunner that connects to a [tool server](https://gradion-ai.github.io/mcpygen/toolserver/index.md).

## Using the generated API

```
from mcptools.brave_search.brave_image_search import Params, Result, run

# Params validates input
params = Params(query="neural topic models", count=3)

# run() calls the MCP tool and returns a Result (or str for untyped tools)
result: Result = run(params)

for image in result.items:
    print(image.title)
```

A running [tool server](https://gradion-ai.github.io/mcpygen/toolserver/index.md) is required for executing tool calls.

## Async API generation

By default, `generate_mcp_sources()` generates synchronous `run()` functions that use `ToolRunner.run_sync()`. Pass `async_api=True` to generate async functions instead:

```
await generate_mcp_sources(
    "fetch_mcp", server_params, Path("mcptools"), async_api=True
)
```

This produces `async def run()` functions that use `await ToolRunner.run()` ([source](https://github.com/gradion-ai/mcpygen/blob/main/docs/generated/mcptools/fetch_mcp/fetch_async.py)):

```
async def run(params: Params) -> str:
    """Fetches a URL from the internet and extracts its contents as markdown."""
    return await CLIENT.run(tool_name="fetch", tool_args=params.model_dump(exclude_none=True))
```

Use the async API with `await`:

```
from mcptools.fetch_mcp.fetch import Params, run

result = await run(Params(url="https://example.com"))
```

## Tool server connection

The generated API connects to a tool server at `localhost:8900` by default. Override the host and port with environment variables:

| Variable           | Default     | Description          |
| ------------------ | ----------- | -------------------- |
| `TOOL_SERVER_HOST` | `localhost` | Tool server hostname |
| `TOOL_SERVER_PORT` | `8900`      | Tool server port     |
