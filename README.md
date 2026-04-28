# Abaqus MCP Autostart for opencode

An opencode-friendly adaptation of [Cai-aa/abaqus-mcp](https://github.com/Cai-aa/abaqus-mcp).

This version keeps the original file-based Abaqus MCP idea, but adds an autostart wrapper so opencode can start the Abaqus-side backend automatically instead of failing with a `stopped` connection state.

## What Changed

The upstream project expects two processes to exist:

- a normal MCP stdio server, `mcp_server.py`
- an Abaqus/CAE-side polling loop loaded from `abaqus_mcp_plugin.py`

opencode can start the first process, but the second process must also be running inside Abaqus. If it is not running, opencode can still see the MCP server, but calls such as `check_abaqus_connection` report `stopped` or time out.

This fork/adaptation adds:

- `mcp_server_autostart.py`: a wrapper that starts the Abaqus noGUI backend when needed, then delegates to the original `mcp_server.py`
- `start_abaqus_mcp_nogui.py`: the Abaqus-side noGUI bootstrap script
- `start_backend.ps1` and `stop_backend.ps1`: Windows helper scripts for manual start/stop
- `opencode.config.example.json`: an opencode MCP config example
- `.mcp.example.json`: a common `mcpServers` config example for other MCP clients
- a cleaned README and runtime `.gitignore`

The original source files `mcp_server.py`, `abaqus_mcp_plugin.py`, `stop_mcp.py`, `abaqus_v6.env.example`, and the optional Abaqus GUI plugin are preserved from the upstream project.

## Requirements

- Windows
- Abaqus/CAE installed and licensed
- Python with the `mcp` package installed
- opencode, or another MCP client that can launch a local stdio server

The wrapper searches for Abaqus in this order:

1. `%ABAQUS_COMMAND%`
2. `C:\SIMULIA\Commands\abaqus.bat`
3. `C:\cae\Software\abaqus.bat`

If Abaqus is somewhere else, set `ABAQUS_COMMAND` to the full path of `abaqus.bat`.

## opencode Setup

Copy or merge this into your opencode config:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "abaqus-mcp-server": {
      "type": "local",
      "command": [
        "python",
        "C:\\path\\to\\abaqus-mcp-opencode\\mcp_server_autostart.py"
      ]
    }
  }
}
```

On Windows, the usual global opencode config location is:

```text
%USERPROFILE%\.config\opencode\opencode.json
```

## Usage

Start opencode normally. When opencode launches `abaqus-mcp-server`, `mcp_server_autostart.py` will:

1. read `status.json`, if it exists
2. decide whether the Abaqus backend is already running
3. start `abaqus cae noGUI=start_abaqus_mcp_nogui.py` if needed
4. wait for the backend status to become `running`
5. run the original `mcp_server.py`

To test the connection from your MCP client, call:

```text
check_abaqus_connection
```

Expected result:

```text
Connected to Abaqus MCP v4.0.0.
Status: running
```

You can also call:

```text
ping
```

Expected result:

```text
pong (v4.0.0)
```

## Manual Start and Stop

Start the Abaqus backend manually:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\path\to\abaqus-mcp-opencode\start_backend.ps1"
```

Stop the backend and release the Abaqus license:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\path\to\abaqus-mcp-opencode\stop_backend.ps1"
```

## Runtime Files

The following files and folders are generated at runtime and should not be committed:

- `commands/`
- `results/`
- `scripts/`
- `screenshots/`
- `status.json`
- `stop.flag`
- `mcp.log`
- `autostart.log`
- Abaqus-generated `.rpy`, `.jnl`, `.log`, `.dat`, `.odb`, and similar analysis files

They are ignored by the included `.gitignore`.

## Troubleshooting

If the MCP client reports `stopped`, the Abaqus-side polling loop is not running. With this adaptation, restarting the MCP client usually fixes it because the wrapper should autostart the backend.

If autostart does not work:

- check `autostart.log`
- check `abaqus_mcp_backend.err.log`
- verify your Abaqus path or set `%ABAQUS_COMMAND%`
- run `start_backend.ps1` manually

Opening an `.odb` file is not normally the cause of `stopped`. The status only means the backend polling process is absent, stale, or stopped.

## Attribution

This project is based on [Cai-aa/abaqus-mcp](https://github.com/Cai-aa/abaqus-mcp).

The main adaptation here is the opencode-oriented autostart layer and packaging cleanup. The original MCP server, Abaqus plugin, file-based IPC design, and MIT license are from the upstream project.
