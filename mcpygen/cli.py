import argparse
import asyncio
import json
from pathlib import Path

from mcpygen.apigen import generate_mcp_sources
from mcpygen.tool_exec.server import ToolServer


def main():
    parser = argparse.ArgumentParser(prog="mcpygen", description="MCP tooling infrastructure")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # apigen subcommand
    apigen_parser = subparsers.add_parser("apigen", help="Generate typed Python tool APIs from MCP server schemas")
    apigen_parser.add_argument("--server-name", required=True, help="Name for the generated package directory")
    apigen_parser.add_argument("--server-params", required=True, help="MCP server connection parameters as JSON string")
    apigen_parser.add_argument("--root-dir", required=True, help="Parent directory where the package will be created")
    apigen_parser.add_argument(
        "--async", dest="async_api", action="store_true", help="Generate async API (async def run with await)"
    )

    # toolserver subcommand
    toolserver_parser = subparsers.add_parser("toolserver", help="Run a standalone ToolServer instance")
    toolserver_parser.add_argument("--host", type=str, default="localhost", help="Hostname to bind to")
    toolserver_parser.add_argument("--port", type=int, default=8900, help="Port to listen on")
    toolserver_parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")

    args = parser.parse_args()

    match args.command:
        case "apigen":
            _run_apigen(args)
        case "toolserver":
            _run_toolserver(args)


def _run_apigen(args: argparse.Namespace):
    server_params = json.loads(args.server_params)
    root_dir = Path(args.root_dir)

    tool_names = asyncio.run(
        generate_mcp_sources(
            server_name=args.server_name,
            server_params=server_params,
            root_dir=root_dir,
            async_api=args.async_api,
        )
    )

    for name in tool_names:
        print(name)


def _run_toolserver(args: argparse.Namespace):
    async def _serve():
        async with ToolServer(
            host=args.host,
            port=args.port,
            log_level=args.log_level,
        ) as server:
            await server.join()

    asyncio.run(_serve())


if __name__ == "__main__":
    main()
