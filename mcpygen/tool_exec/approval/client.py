import asyncio
import json
import logging
from functools import partial
from typing import Any, Awaitable, Callable

import aiohttp
import requests
import websockets
from pydantic_core import to_jsonable_python
from websockets import ClientConnection, ConnectionClosed

from mcpygen.tool_exec.client import _make_error

logger = logging.getLogger(__name__)


class ApprovalRequest:
    """An MCP tool call approval request.

    `ApprovalRequest` instances are passed to the approval callback registered with
    [`ApprovalClient`][mcpygen.tool_exec.approval.client.ApprovalClient]. The callback
    must call [`accept`][mcpygen.tool_exec.approval.client.ApprovalRequest.accept]
    or [`reject`][mcpygen.tool_exec.approval.client.ApprovalRequest.reject] for making
    an approval decision. Consumers can await [`response`][mcpygen.tool_exec.approval.client.ApprovalRequest.response]
    to observe the decision.

    Example:
        ```python
        async def on_approval_request(request: ApprovalRequest):
            print(f"Approval request: {request}")
            if request.tool_name == "dangerous_tool":
                await request.reject()
            else:
                await request.accept()
        ```
    """

    def __init__(
        self,
        server_name: str,
        tool_name: str,
        tool_args: dict[str, Any],
        respond: Callable[[bool], Awaitable[None]],
    ):
        """
        Args:
            server_name: Name of the MCP server providing the tool.
            tool_name: Name of the tool to execute.
            tool_args: Arguments to pass to the tool.
            respond: Function to make an approval decision.
        """
        self.server_name = server_name
        self.tool_name = tool_name
        self.tool_args = tool_args
        self._respond = respond
        self._decision = asyncio.get_running_loop().create_future()

    def __str__(self) -> str:
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in self.tool_args.items()])
        return f"{self.server_name}.{self.tool_name}({kwargs_str})"

    async def accept(self):
        """Accept the approval request."""
        self._set_decision(True)
        return await self._respond(True)

    async def reject(self):
        """Reject the approval request."""
        self._set_decision(False)
        return await self._respond(False)

    async def response(self) -> bool:
        """Wait for and return the approval decision."""
        return await self._decision

    def on_decision(self, callback: Callable[[bool], None]):
        """Register a callback invoked once when a decision is made."""

        def invoke(result: bool):
            try:
                callback(result)
            except Exception:
                logger.exception("Error in approval decision callback")

        if self._decision.done():
            invoke(self._decision.result())
            return

        def _done(fut: asyncio.Future[bool]):
            invoke(fut.result())

        self._decision.add_done_callback(_done)

    def set_on_decision(self, on_decision: Callable[[], None]):
        """Backwards-compatible alias for registering a decision callback."""
        self.on_decision(lambda _result: on_decision())

    def _set_decision(self, decision: bool):
        if not self._decision.done():
            self._decision.set_result(decision)


ApprovalCallback = Callable[[ApprovalRequest], Awaitable[None]]
"""Type alias for approval callback functions.

An approval callback is an async function that receives an
[`ApprovalRequest`][mcpygen.tool_exec.approval.client.ApprovalRequest] and must call
one of its response methods (`accept()` or `reject()`) to make an approval decision.
"""


class ApprovalClient:
    """Client for handling tool call approval requests.

    `ApprovalClient` connects to a [`ToolServer`][mcpygen.tool_exec.server.ToolServer]'s
    approval channel and receives approval requests. Each request is passed to the
    registered callback, which must accept or reject the request.

    Example:
        ```python
        async def on_approval_request(request: ApprovalRequest):
            print(f"Approval request: {request}")
            await request.accept()

        async with ApprovalClient(callback=on_approval_request):
            # Execute code that triggers MCP tool calls
            ...
        ```
    """

    def __init__(
        self,
        callback: ApprovalCallback,
        host: str = "localhost",
        port: int = 8900,
    ):
        """
        Args:
            callback: Async function called for each approval request.
            host: Hostname of the `ToolServer`.
            port: Port number of the `ToolServer`.
        """
        self.callback = callback
        self.host = host
        self.port = port

        self._uri = f"ws://{host}:{port}/approval"
        self._conn: ClientConnection | None = None
        self._task: asyncio.Task | None = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Connect to a `ToolServer`'s `ApprovalChannel`."""
        self._conn = await websockets.connect(self._uri)
        self._task = asyncio.create_task(self._recv())

    async def disconnect(self):
        """Disconnect from the `ToolServer`'s `ApprovalChannel`."""
        if self._conn:
            await self._conn.close()
            self._conn = None
        if self._task:
            await self._task
            self._task = None

    async def _send(self, result: bool, request_id: str):
        if not self._conn:
            raise RuntimeError("Not connected")

        response = {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id,
        }
        await self._conn.send(json.dumps(response))

    async def _recv(self):
        if not self._conn:
            raise RuntimeError("Not connected")

        try:
            async for msg in self._conn:
                data = json.loads(msg)

                if data.get("method") == "approve":
                    params = data.get("params", {})
                    approval = ApprovalRequest(
                        server_name=params["server_name"],
                        tool_name=params["tool_name"],
                        tool_args=params["tool_args"],
                        respond=partial(self._send, request_id=data["id"]),
                    )
                    try:
                        await self.callback(approval)
                    except Exception:
                        logger.exception("Error in approval callback")

        except ConnectionClosed:
            pass


class ApprovalRequestor:
    """Client for requesting tool call approval from a [`ToolServer`][mcpygen.tool_exec.server.ToolServer].

    `ApprovalRequestor` sends approval requests to the server's `/approve` endpoint
    without executing the tool.

    Example:
        ```python
        requestor = ApprovalRequestor(
            server_name="fetch",
            host="localhost",
            port=8900,
        )
        await requestor.request("fetch", {"url": "https://example.com"})
        ```
    """

    def __init__(
        self,
        server_name: str,
        host: str = "localhost",
        port: int = 8900,
    ):
        """
        Args:
            server_name: Name of the MCP server.
            host: Hostname of the `ToolServer`.
            port: Port number of the `ToolServer`.
        """
        self.server_name = server_name
        self.host = host
        self.port = port

        self.url = f"http://{host}:{port}/approve"

    async def request(self, tool_name: str, tool_args: dict[str, Any]) -> None:
        """Request approval for a tool call.

        Args:
            tool_name: Name of the tool to approve.
            tool_args: Arguments to pass to the tool.

        Raises:
            ApprovalRejectedError: If the tool call is rejected by the approval workflow.
            ApprovalTimeoutError: If the approval request times out.
            ToolRunnerError: If the approval request fails.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.url, json=self._create_data(tool_name, tool_args)) as response:
                response.raise_for_status()
                response_json = await response.json()

                if "error" in response_json:
                    raise _make_error(response_json)

    def request_sync(self, tool_name: str, tool_args: dict[str, Any]) -> None:
        """Synchronous version of [`request`][mcpygen.tool_exec.approval.client.ApprovalRequestor.request].

        Args:
            tool_name: Name of the tool to approve.
            tool_args: Arguments to pass to the tool.

        Raises:
            ApprovalRejectedError: If the tool call is rejected by the approval workflow.
            ApprovalTimeoutError: If the approval request times out.
            ToolRunnerError: If the approval request fails.
        """
        response = requests.post(url=self.url, json=self._create_data(tool_name, tool_args))
        response.raise_for_status()
        response_json = response.json()

        if "error" in response_json:
            raise _make_error(response_json)

    def _create_data(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        return {
            "server_name": self.server_name,
            "tool_name": tool_name,
            "tool_args": to_jsonable_python(tool_args),
        }
