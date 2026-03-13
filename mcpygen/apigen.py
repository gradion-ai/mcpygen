import asyncio
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

import aiofiles
import aiofiles.os
from datamodel_code_generator import DataModelType, Formatter, PythonVersion
from datamodel_code_generator.model import get_data_model_types
from datamodel_code_generator.model.base import ALL_MODEL
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser

from mcpygen.client import MCPClient

_DEFAULT_FORMATTERS: list[Formatter] = [Formatter.BLACK, Formatter.ISORT]


def generate_init_definition(server_name: str, server_params: dict[str, Any]) -> str:
    return f"""\
import os
from mcpygen.tool_exec.client import ToolRunner

CLIENT = ToolRunner(
    server_name={repr(server_name)},
    server_params={repr(server_params)},
    host=os.environ.get("TOOL_SERVER_HOST", "localhost"),
    port=int(os.environ.get("TOOL_SERVER_PORT", "8900")),
)
"""


def _safe_docstring(description: str) -> str:
    safe = description.replace("\x00", "").replace("\\", "\\\\").replace('"""', '""\\"')
    lines = safe.split("\n")
    indented = (
        lines[0] + "\n" + "\n".join("    " + line if line else line for line in lines[1:])
        if len(lines) > 1
        else lines[0]
    )
    return f'"""{indented}\n    """'


def generate_function_definition(
    original_name: str, description: str, structured_output: bool, async_api: bool = False
) -> str:
    name = json.dumps(original_name)
    desc = _safe_docstring(description)
    def_kw = "async def" if async_api else "def"
    call = f"await CLIENT.run(tool_name={name}" if async_api else f"CLIENT.run_sync(tool_name={name}"
    args = ", tool_args=params.model_dump(exclude_none=True))"
    if structured_output:
        return f"""\
from . import CLIENT

{def_kw} run(params: Params) -> Result:
    {desc}
    result = {call}{args}
    return Result.model_validate(result)
"""
    return f"""\
from . import CLIENT

{def_kw} run(params: Params) -> str:
    {desc}
    return {call}{args}
"""


def generate_input_model_code(schema: dict[str, Any]) -> str:
    return _generate_model_code(schema, "Params")


def generate_output_model_code(schema: dict[str, Any]) -> str:
    return _generate_model_code(schema, "Result")


def _generate_model_code(schema: dict[str, Any], class_name: str) -> str:
    """Generate a Pydantic model from JSON schema."""
    data_model_types = get_data_model_types(
        data_model_type=DataModelType.PydanticV2BaseModel,
        target_python_version=PythonVersion.PY_311,
    )

    extra_template_data = defaultdict(dict)  # type: ignore
    extra_template_data[ALL_MODEL]["config"] = {"use_enum_values": True}

    parser = JsonSchemaParser(
        source=json.dumps(schema),
        class_name=class_name,
        data_model_type=data_model_types.data_model,
        data_model_root_type=data_model_types.root_model,
        data_model_field_type=data_model_types.field_model,
        data_type_manager_type=data_model_types.data_type_manager,
        dump_resolve_reference_action=data_model_types.dump_resolve_reference_action,
        use_field_description=True,
        use_double_quotes=True,
        extra_template_data=extra_template_data,
        formatters=_DEFAULT_FORMATTERS,
    )
    return parser.parse()


async def generate_mcp_sources(
    server_name: str, server_params: dict[str, Any], root_dir: Path, async_api: bool = False
) -> list[str]:
    """Generate a typed Python tool API for an MCP server.

    Connects to an MCP server, discovers available tools, and generates a Python
    package with typed functions backed by Pydantic models. Each tool becomes a
    module with a `Params` class for input validation and a `run()` function to
    invoke the tool.

    When calling the generated API, the corresponding tools are executed on a
    [`ToolServer`][mcpygen.tool_exec.server.ToolServer].

    If a directory for the server already exists under `root_dir`, it is removed
    and recreated.

    Args:
        server_name: Name for the generated package directory. Also used to
            identify the server in the generated client code.
        server_params: MCP server connection parameters. For stdio servers,
            provide `command`, `args`, and optionally `env`. For HTTP servers,
            provide `url` and optionally `headers`.
        root_dir: Parent directory where the package will be created. The
            generated package is written to `root_dir/server_name/`.
        async_api: When `True`, generate async `run()` functions that use
            `await CLIENT.run(...)` instead of sync `CLIENT.run_sync(...)`.

    Returns:
        List of sanitized tool names corresponding to the generated module files.

    Example:
        Generate a Python tool API for the fetch MCP server:

        ```python
        server_params = {
            "command": "uvx",
            "args": ["mcp-server-fetch"],
        }
        await generate_mcp_sources("fetch_mcp", server_params, Path("mcptools"))
        ```
    """
    async with MCPClient(server_params) as server:
        if await aiofiles.os.path.exists(root_dir / server_name):
            await asyncio.get_running_loop().run_in_executor(None, shutil.rmtree, root_dir / server_name)

        await aiofiles.os.makedirs(root_dir / server_name)

        async with aiofiles.open(root_dir / server_name / "__init__.py", "w") as f:
            await f.write(generate_init_definition(server_name, server_params))

        result = []  # type: ignore

        for tool in await server.list_tools():
            original_name = tool.name
            sanitized_name = sanitize_name(tool.name)
            result.append(sanitized_name)

            # Generate input model (Params)
            input_model_code = generate_input_model_code(tool.inputSchema)

            output_schema = tool.outputSchema
            output_model_code = None

            if output_schema:
                output_model_code = generate_output_model_code(output_schema)
                output_model_code = strip_imports(output_model_code)

            # Generate function with appropriate return type
            function_definition = generate_function_definition(
                original_name=original_name,
                description=tool.description or "",
                structured_output=output_schema is not None,
                async_api=async_api,
            )

            # Write file with models and function
            async with aiofiles.open(root_dir / server_name / f"{sanitized_name}.py", "w") as f:
                if output_schema:
                    await f.write(f"{input_model_code}\n\n{output_model_code}\n\n{function_definition}")
                else:
                    await f.write(f"{input_model_code}\n\n{function_definition}")

        return result


def strip_imports(code: str) -> str:
    filtered_lines = []
    for line in code.split("\n"):
        if line.strip() == "from __future__ import annotations":
            continue
        filtered_lines.append(line)
    return "\n".join(filtered_lines)


def sanitize_name(name: str) -> str:
    """Sanitize a name for being used as module name."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name).lower()
