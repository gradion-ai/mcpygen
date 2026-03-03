## mcpygen.tool_exec.server.ToolServer

```
ToolServer(
    host="localhost",
    port: int = 8900,
    approval_required: bool = False,
    approval_timeout: float | None = None,
    connect_timeout: float = 30,
    log_to_stderr: bool = False,
    log_level: str = "INFO",
)
```

HTTP server that manages MCP servers and executes their tools with optional approval.

ToolServer provides HTTP endpoints for executing MCP tools and a WebSocket endpoint for sending approval requests to clients. MCP servers are started on demand when tools are first executed and cached for subsequent calls.

Endpoints:

- `PUT /reset`: Closes all started MCP servers
- `POST /run`: Executes an MCP tool (with optional approval)
- `WS /approval`: WebSocket endpoint for ApprovalClient connections

Example

```
async with ToolServer(approval_required=True) as server:
    async with ApprovalClient(callback=on_approval_request):
        # Execute code that calls MCP tools
        ...
```

Parameters:

| Name                | Type    | Description                                            | Default                                                                   |
| ------------------- | ------- | ------------------------------------------------------ | ------------------------------------------------------------------------- |
| `host`              |         | Hostname the server binds to.                          | `'localhost'`                                                             |
| `port`              | `int`   | Port number the server listens on.                     | `8900`                                                                    |
| `approval_required` | `bool`  | Whether tool calls require approval.                   | `False`                                                                   |
| `approval_timeout`  | \`float | None\`                                                 | Timeout in seconds for approval requests. If None, no timeout is applied. |
| `connect_timeout`   | `float` | Timeout in seconds for starting MCP servers.           | `30`                                                                      |
| `log_to_stderr`     | `bool`  | Whether to log to stderr instead of stdout.            | `False`                                                                   |
| `log_level`         | `str`   | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). | `'INFO'`                                                                  |

### join

```
join()
```

Wait for the HTTP server task to stop.

### start

```
start()
```

Start the HTTP server.

Raises:

| Type           | Description                       |
| -------------- | --------------------------------- |
| `RuntimeError` | If the server is already running. |

### stop

```
stop()
```

Stop the HTTP server and close all managed MCP servers.
