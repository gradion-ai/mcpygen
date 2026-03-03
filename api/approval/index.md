## mcpygen.tool_exec.approval.client.ApprovalClient

```
ApprovalClient(
    callback: ApprovalCallback,
    host: str = "localhost",
    port: int = 8900,
)
```

Client for handling tool call approval requests.

`ApprovalClient` connects to a ToolServer's approval channel and receives approval requests. Each request is passed to the registered callback, which must accept or reject the request.

Example

```
async def on_approval_request(request: ApprovalRequest):
    print(f"Approval request: {request}")
    await request.accept()

async with ApprovalClient(callback=on_approval_request):
    # Execute code that triggers MCP tool calls
    ...
```

Parameters:

| Name       | Type               | Description                                      | Default       |
| ---------- | ------------------ | ------------------------------------------------ | ------------- |
| `callback` | `ApprovalCallback` | Async function called for each approval request. | *required*    |
| `host`     | `str`              | Hostname of the ToolServer.                      | `'localhost'` |
| `port`     | `int`              | Port number of the ToolServer.                   | `8900`        |

### connect

```
connect()
```

Connect to a `ToolServer`'s `ApprovalChannel`.

### disconnect

```
disconnect()
```

Disconnect from the `ToolServer`'s `ApprovalChannel`.

## mcpygen.tool_exec.approval.client.ApprovalRequest

```
ApprovalRequest(
    server_name: str,
    tool_name: str,
    tool_args: dict[str, Any],
    respond: Callable[[bool], Awaitable[None]],
)
```

An MCP tool call approval request.

`ApprovalRequest` instances are passed to the approval callback registered with ApprovalClient. The callback must call accept or reject for making an approval decision. Consumers can await response to observe the decision.

Example

```
async def on_approval_request(request: ApprovalRequest):
    print(f"Approval request: {request}")
    if request.tool_name == "dangerous_tool":
        await request.reject()
    else:
        await request.accept()
```

Parameters:

| Name          | Type                                | Description                                | Default    |
| ------------- | ----------------------------------- | ------------------------------------------ | ---------- |
| `server_name` | `str`                               | Name of the MCP server providing the tool. | *required* |
| `tool_name`   | `str`                               | Name of the tool to execute.               | *required* |
| `tool_args`   | `dict[str, Any]`                    | Arguments to pass to the tool.             | *required* |
| `respond`     | `Callable[[bool], Awaitable[None]]` | Function to make an approval decision.     | *required* |

### server_name

```
server_name = server_name
```

### tool_name

```
tool_name = tool_name
```

### tool_args

```
tool_args = tool_args
```

### accept

```
accept()
```

Accept the approval request.

### reject

```
reject()
```

Reject the approval request.

### response

```
response() -> bool
```

Wait for and return the approval decision.

## mcpygen.tool_exec.client.ToolRunnerError

Bases: `Exception`

Raised when tool execution fails on the server.

## mcpygen.tool_exec.client.ApprovalRejectedError

Bases: `ToolRunnerError`

Raised when a tool call is rejected by the approval workflow.

## mcpygen.tool_exec.client.ApprovalTimeoutError

Bases: `ToolRunnerError`

Raised when an approval request times out.
