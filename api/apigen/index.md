## mcpygen.apigen.generate_mcp_sources

```
generate_mcp_sources(
    server_name: str,
    server_params: dict[str, Any],
    root_dir: Path,
) -> list[str]
```

Generate a typed Python tool API for an MCP server.

Connects to an MCP server, discovers available tools, and generates a Python package with typed functions backed by Pydantic models. Each tool becomes a module with a `Params` class for input validation and a `run()` function to invoke the tool.

When calling the generated API, the corresponding tools are executed on a ToolServer.

If a directory for the server already exists under `root_dir`, it is removed and recreated.

Parameters:

| Name            | Type             | Description                                                                                                                                           | Default    |
| --------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `server_name`   | `str`            | Name for the generated package directory. Also used to identify the server in the generated client code.                                              | *required* |
| `server_params` | `dict[str, Any]` | MCP server connection parameters. For stdio servers, provide command, args, and optionally env. For HTTP servers, provide url and optionally headers. | *required* |
| `root_dir`      | `Path`           | Parent directory where the package will be created. The generated package is written to root_dir/server_name/.                                        | *required* |

Returns:

| Type        | Description                                                               |
| ----------- | ------------------------------------------------------------------------- |
| `list[str]` | List of sanitized tool names corresponding to the generated module files. |

Example

Generate a Python tool API for the fetch MCP server:

```
server_params = {
    "command": "uvx",
    "args": ["mcp-server-fetch"],
}
await generate_mcp_sources("fetch_mcp", server_params, Path("mcptools"))
```
