## mcpygen.tool_exec.client.ToolRunner

```
ToolRunner(
    server_name: str,
    server_params: dict[str, Any],
    host: str = "localhost",
    port: int = 8900,
)
```

Client for executing MCP tools on a ToolServer.

Example

```
runner = ToolRunner(
    server_name="fetch",
    server_params={"command": "uvx", "args": ["mcp-server-fetch"]},
)
result = await runner.run("fetch", {"url": "https://example.com"})
```

Parameters:

| Name            | Type             | Description                    | Default       |
| --------------- | ---------------- | ------------------------------ | ------------- |
| `server_name`   | `str`            | Name of the MCP server.        | *required*    |
| `server_params` | `dict[str, Any]` | MCP server parameters.         | *required*    |
| `host`          | `str`            | Hostname of the ToolServer.    | `'localhost'` |
| `port`          | `int`            | Port number of the ToolServer. | `8900`        |

### reset

```
reset()
```

Reset the `ToolServer`, stopping all started MCP servers.

### run

```
run(
    tool_name: str, tool_args: dict[str, Any]
) -> dict[str, Any] | str | None
```

Execute a tool on the configured MCP server.

Parameters:

| Name        | Type             | Description                    | Default    |
| ----------- | ---------------- | ------------------------------ | ---------- |
| `tool_name` | `str`            | Name of the tool to execute.   | *required* |
| `tool_args` | `dict[str, Any]` | Arguments to pass to the tool. | *required* |

Returns:

| Type             | Description |
| ---------------- | ----------- |
| \`dict[str, Any] | str         |

Raises:

| Type                    | Description                                            |
| ----------------------- | ------------------------------------------------------ |
| `ApprovalRejectedError` | If the tool call is rejected by the approval workflow. |
| `ApprovalTimeoutError`  | If the approval request times out.                     |
| `ToolRunnerError`       | If tool execution fails.                               |

### run_sync

```
run_sync(
    tool_name: str, tool_args: dict[str, Any]
) -> dict[str, Any] | str | None
```

Synchronous version of run.

Parameters:

| Name        | Type             | Description                    | Default    |
| ----------- | ---------------- | ------------------------------ | ---------- |
| `tool_name` | `str`            | Name of the tool to execute.   | *required* |
| `tool_args` | `dict[str, Any]` | Arguments to pass to the tool. | *required* |

Returns:

| Type             | Description |
| ---------------- | ----------- |
| \`dict[str, Any] | str         |

Raises:

| Type                    | Description                                            |
| ----------------------- | ------------------------------------------------------ |
| `ApprovalRejectedError` | If the tool call is rejected by the approval workflow. |
| `ApprovalTimeoutError`  | If the approval request times out.                     |
| `ToolRunnerError`       | If tool execution fails.                               |
