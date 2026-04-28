# Notice

This repository is an adaptation of [Cai-aa/abaqus-mcp](https://github.com/Cai-aa/abaqus-mcp).

Original project components retained here include:

- `mcp_server.py`
- `abaqus_mcp_plugin.py`
- `stop_mcp.py`
- `abaqus_v6.env.example`
- `abaqus_plugins/mcp_control`

Adaptation-specific additions include:

- `mcp_server_autostart.py`
- `start_abaqus_mcp_nogui.py`
- `start_backend.ps1`
- `stop_backend.ps1`
- `opencode.config.example.json`
- `.mcp.example.json`
- this README/NOTICE packaging

The purpose of this adaptation is to make the Abaqus backend start automatically for opencode and other local MCP clients that only launch a stdio MCP server.
