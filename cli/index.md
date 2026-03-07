# CLI Reference

mcpygen provides a command-line interface with two subcommands.

## `mcpygen apigen`

Generate typed Python tool APIs from MCP server schemas.

```
mcpygen apigen \
    --server-name fetch_mcp \
    --server-params '{"command": "uvx", "args": ["mcp-server-fetch"]}' \
    --root-dir mcptools
```

**Arguments:**

| Argument          | Description                                        |
| ----------------- | -------------------------------------------------- |
| `--server-name`   | Name for the generated package directory           |
| `--server-params` | MCP server connection parameters (JSON string)     |
| `--root-dir`      | Parent directory where the package will be created |
| `--async`         | Generate async API (`async def run`)               |

## `mcpygen toolserver`

Run a standalone tool server instance.

```
mcpygen toolserver --host localhost --port 8900 --log-level INFO
```

**Arguments:**

| Argument      | Default     | Description         |
| ------------- | ----------- | ------------------- |
| `--host`      | `localhost` | Hostname to bind to |
| `--port`      | `8900`      | Port to listen on   |
| `--log-level` | `INFO`      | Logging level       |
