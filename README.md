# mcpygen

<p align="left">
    <a href="https://gradion-ai.github.io/mcpygen/"><img alt="Website" src="https://img.shields.io/website?url=https%3A%2F%2Fgradion-ai.github.io%2Fmcpygen%2F&up_message=online&down_message=offline&label=docs"></a>
    <a href="https://pypi.org/project/mcpygen/"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/mcpygen?color=blue"></a>
    <a href="https://github.com/gradion-ai/mcpygen/releases"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/gradion-ai/mcpygen"></a>
    <a href="https://github.com/gradion-ai/mcpygen/actions"><img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/gradion-ai/mcpygen/test.yml"></a>
    <a href="https://github.com/gradion-ai/mcpygen/blob/main/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/gradion-ai/mcpygen?color=blueviolet"></a>
</p>

[mcpygen](https://gradion-ai.github.io/mcpygen/) generates typed Python APIs from MCP server tool schemas. Tool calls made through the generated APIs are executed on a local tool server that manages MCP server connections.

## Features

| Feature | Description |
| --- | --- |
| **API generation** | Generate typed Python tool APIs from MCP server schemas. Each tool becomes a module with a Pydantic `Params` model and a `run()` function. Tools that provide an output schema also get a typed `Result` model. |
| **Tool server** | Local server that manages stdio MCP servers and connects to remote streamable HTTP or SSE servers |
| **Approval workflow** | Gate tool calls with a WebSocket-based approval channel before execution |

## Documentation

- [Documentation](https://gradion-ai.github.io/mcpygen/)
- [llms.txt](https://gradion-ai.github.io/mcpygen/llms.txt)
- [llms-full.txt](https://gradion-ai.github.io/mcpygen/llms-full.txt)
