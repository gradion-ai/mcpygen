from typing import Any, Awaitable, Callable

import pytest
import pytest_asyncio

from mcpygen.tool_exec.approval.client import ApprovalClient, ApprovalRequest, ApprovalRequestor
from mcpygen.tool_exec.client import ApprovalRejectedError, ApprovalTimeoutError, ToolRunnerError
from mcpygen.tool_exec.server import ToolServer
from mcpygen.utils import arun

TOOL_SERVER_PORT = 8920
MCP_SERVER_NAME = "test_mcp_server"

RequestApprovalFunc = Callable[[ApprovalRequestor, str, dict[str, Any]], Awaitable[None]]


@pytest_asyncio.fixture
async def tool_server():
    """Start a ToolServer with approval enabled."""
    async with ToolServer(port=TOOL_SERVER_PORT, approval_required=True, log_level="WARNING") as server:
        yield server


@pytest.fixture(params=["async", "sync"])
def request_approval(request) -> RequestApprovalFunc:
    """Fixture that provides approval requesting in both async and sync modes."""
    if request.param == "async":

        async def _request(requestor: ApprovalRequestor, tool_name: str, tool_args: dict[str, Any]) -> None:
            await requestor.request(tool_name, tool_args)
    else:

        async def _request(requestor: ApprovalRequestor, tool_name: str, tool_args: dict[str, Any]) -> None:
            await arun(requestor.request_sync, tool_name, tool_args)

    return _request


class TestApprovalRequestor:
    """Integration tests for ApprovalRequestor."""

    @pytest.mark.asyncio
    async def test_approved(
        self,
        tool_server: ToolServer,
        request_approval: RequestApprovalFunc,
    ):
        """Test that approved requests complete without error."""
        requestor = ApprovalRequestor(MCP_SERVER_NAME, port=TOOL_SERVER_PORT)

        async def accept_all(request: ApprovalRequest):
            await request.accept()

        async with ApprovalClient(callback=accept_all, port=TOOL_SERVER_PORT):
            await request_approval(requestor, "tool-1", {"s": "approved"})

    @pytest.mark.asyncio
    async def test_rejected(
        self,
        tool_server: ToolServer,
        request_approval: RequestApprovalFunc,
    ):
        """Test that rejected requests raise ApprovalRejectedError."""
        requestor = ApprovalRequestor(MCP_SERVER_NAME, port=TOOL_SERVER_PORT)

        async def reject_all(request: ApprovalRequest):
            await request.reject()

        async with ApprovalClient(callback=reject_all, port=TOOL_SERVER_PORT):
            with pytest.raises(ApprovalRejectedError, match="rejected"):
                await request_approval(requestor, "tool-1", {"s": "rejected"})

    @pytest.mark.asyncio
    async def test_receives_correct_data(
        self,
        tool_server: ToolServer,
        request_approval: RequestApprovalFunc,
    ):
        """Test that approval callback receives correct request data."""
        requestor = ApprovalRequestor(MCP_SERVER_NAME, port=TOOL_SERVER_PORT)
        received_request: ApprovalRequest | None = None

        async def capture_request(request: ApprovalRequest):
            nonlocal received_request
            received_request = request
            await request.accept()

        async with ApprovalClient(callback=capture_request, port=TOOL_SERVER_PORT):
            await request_approval(requestor, "tool_3", {"name": "test_name", "level": 42})

        assert received_request is not None
        assert received_request.server_name == MCP_SERVER_NAME
        assert received_request.tool_name == "tool_3"
        assert received_request.tool_args == {"name": "test_name", "level": 42}

    @pytest.mark.asyncio
    async def test_no_approval_client_raises_error(
        self,
        tool_server: ToolServer,
        request_approval: RequestApprovalFunc,
    ):
        """Test that requests fail when no ApprovalClient is connected."""
        requestor = ApprovalRequestor(MCP_SERVER_NAME, port=TOOL_SERVER_PORT)

        with pytest.raises(ToolRunnerError, match="failed"):
            await request_approval(requestor, "tool-1", {"s": "no_client"})

    @pytest.mark.asyncio
    async def test_timeout(self, request_approval: RequestApprovalFunc):
        """Test that requests fail when approval times out."""
        async with ToolServer(port=TOOL_SERVER_PORT, approval_required=True, approval_timeout=0.1, log_level="WARNING"):
            requestor = ApprovalRequestor(MCP_SERVER_NAME, port=TOOL_SERVER_PORT)

            async def never_respond(request: ApprovalRequest):
                pass

            async with ApprovalClient(callback=never_respond, port=TOOL_SERVER_PORT):
                with pytest.raises(ApprovalTimeoutError, match="expired"):
                    await request_approval(requestor, "tool-1", {"s": "timeout_test"})
