# Approval workflow

When `approval_required=True`, each tool call on the [tool server](https://gradion-ai.github.io/mcpygen/toolserver/index.md) requires approval via WebSocket before execution.

```
from mcpygen import ApprovalClient, ApprovalRequest, ToolServer

async def on_approval(request: ApprovalRequest):
    print(f"Tool call: {request}")
    await request.accept()  # or request.reject()

async with ToolServer(approval_required=True) as server:
    async with ApprovalClient(callback=on_approval):
        # Tool calls now require approval
        ...
```

## Typed approval errors

Generated tool APIs raise specific error types for approval failures:

- ApprovalRejectedError: The tool call was rejected
- ApprovalTimeoutError: The approval request timed out

Both inherit from ToolRunnerError.
