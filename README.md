# Abaqus MCP Autostart for opencode

**A low-cost Abaqus AI automation assistant that lets AI agents drive simulation workflows through MCP.**

This project adapts [Cai-aa/abaqus-mcp](https://github.com/Cai-aa/abaqus-mcp) for opencode and other local MCP clients. It is not just a collection of Abaqus scripts: it turns Abaqus/CAE into an agent-callable simulation environment where an AI assistant can generate Abaqus Python, build models, submit jobs, inspect ODB files, capture result images, and support post-processing workflows from natural-language instructions.

> Chinese summary: this project makes Abaqus callable by AI agents. Users describe simulation tasks in natural language, and the agent can use MCP tools to drive modeling, solving, result reading, screenshots, and post-processing.

## What Is This Project?

The original Abaqus MCP architecture has two processes:

- `mcp_server.py` runs outside Abaqus and exposes MCP tools to an AI client.
- `abaqus_mcp_plugin.py` runs inside Abaqus/CAE and polls file-based commands.

Many MCP clients, including opencode, can start the first process but do not automatically start the Abaqus-side polling loop. That causes a common failure mode: the MCP server appears in the client, but `check_abaqus_connection` reports `stopped` or times out.

This adaptation adds an autostart wrapper:

- `mcp_server_autostart.py` checks whether the Abaqus backend is running.
- If needed, it launches `abaqus cae noGUI=start_abaqus_mcp_nogui.py`.
- It waits until the Abaqus backend reports `running`.
- It then delegates to the original `mcp_server.py`.

The result is a smoother workflow for AI-assisted Abaqus automation, especially when using opencode with low-cost models such as DeepSeek.

## Key Features

- Natural-language-driven Abaqus automation through an MCP client.
- Automatic Abaqus noGUI backend startup for opencode.
- Execute Python scripts inside the Abaqus kernel environment.
- Query Abaqus model structure, jobs, materials, steps, loads, boundary conditions, and interactions.
- Submit Abaqus jobs already defined in the current session.
- Read ODB metadata such as steps, frames, parts, and instances.
- Capture Abaqus viewport images as base64 data URLs.
- File-based IPC design inherited from the upstream project.
- Windows helper scripts for manual backend start/stop.

## What You Can Do With This Project

- Describe an Abaqus simulation task in natural language.
- Let an AI agent generate and execute Abaqus Python scripts.
- Build or modify CAE models through agent-written scripts.
- Submit and monitor Abaqus jobs exposed in the current session.
- Extract ODB metadata for result inspection.
- Export viewport images for reports or review.
- Ask the AI to write CSV exporters, plots, or post-processing scripts using Abaqus Python.
- Run simple parameter studies at low LLM cost by repeatedly generating or modifying scripts.

## Quick Start

### 1. Requirements

- Windows
- Abaqus/CAE installed and licensed
- Python with the `mcp` package installed
- opencode, or another MCP client that can launch a local stdio server

Install the Python MCP package if needed:

```powershell
pip install mcp
```

### 2. Configure opencode

Copy or merge this into your opencode config:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "abaqus-mcp-server": {
      "type": "local",
      "command": [
        "python",
        "C:\\path\\to\\abaqus-mcp\\mcp_server_autostart.py"
      ]
    }
  }
}
```

On Windows, the usual global opencode config location is:

```text
%USERPROFILE%\.config\opencode\opencode.json
```

This repository also includes:

- `opencode.config.example.json` for a generic opencode example
- `opencode.local.example.json` for the local machine layout used during development
- `.mcp.example.json` for clients that use the common `mcpServers` format

### 3. Start opencode

Start opencode normally. When opencode launches `abaqus-mcp-server`, `mcp_server_autostart.py` will:

1. read `status.json`, if it exists
2. decide whether the Abaqus backend is already running
3. start `abaqus cae noGUI=start_abaqus_mcp_nogui.py` if needed
4. wait for the backend status to become `running`
5. run the original `mcp_server.py`

### 4. Test the connection

Ask your MCP client to call:

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

## Examples / Case Studies

Case studies show what this project can do from a user's point of view: a natural-language request goes in, and Abaqus scripts, solver jobs, result databases, screenshots, or reports come out.

### Case Study 1: Bullet Impact on a Steel Plate

**User task in natural language**

```text
Create an Abaqus/Explicit simulation of a bullet penetrating a steel plate. Generate the model, submit the job, and extract the final stress, plastic strain, and bullet displacement summary.
```

**What the AI agent completed**

- Generated an Abaqus Python script for the plate, projectile, materials, contact, boundary conditions, and initial velocity.
- Built a 200 mm x 200 mm x 10 mm mild steel plate and a hardened steel bullet with a small flat tip for mesh stability.
- Created an Abaqus/Explicit impact step with general contact and friction.
- Applied clamped boundary conditions to the plate edges and an initial bullet velocity of 800 m/s.
- Wrote the Abaqus input file, ran a datacheck, submitted the explicit job, and confirmed successful completion.
- Opened the ODB and extracted final-frame result metrics using an Abaqus Python post-processing script.

**Model and analysis setup**

| Item | Value |
| --- | --- |
| Geometry | 0.20 m square plate, 0.010 m thick; bullet radius 0.005 m, total length 0.030 m |
| Materials | Mild steel plate and hardened steel bullet |
| Solver | Abaqus/Explicit 2024 |
| Step time | `8.0e-5 s` |
| Contact | General contact, hard normal behavior, friction coefficient 0.12 |
| Loading | Bullet initial velocity = 800 m/s in the negative Z direction |
| Status | Analysis completed successfully |

**Generated result files**

Files included in this repository:

- [`examples/bullet-plate-penetration/create_bullet_plate_penetration.py`](examples/bullet-plate-penetration/create_bullet_plate_penetration.py)
- [`examples/bullet-plate-penetration/postprocess_bullet_plate.py`](examples/bullet-plate-penetration/postprocess_bullet_plate.py)
- [`examples/bullet-plate-penetration/README_bullet_plate_penetration.md`](examples/bullet-plate-penetration/README_bullet_plate_penetration.md)
- [`examples/bullet-plate-penetration/images/bullet_plate_result.png`](examples/bullet-plate-penetration/images/bullet_plate_result.png)

Files generated during the local Abaqus run:

- `bullet_plate_penetration.cae`
- `bullet_plate_penetration.inp`
- `bullet_plate_penetration.odb`
- `bullet_plate_penetration.sta`
- `bullet_plate_penetration.dat`

Large solver outputs such as `.odb` and `.inp` are intentionally not committed by default because they can be large and machine-specific.

**Result summary**

| Output | Value |
| --- | --- |
| Frames | 21 |
| Final step time | `7.9999998e-05 s` |
| Maximum PEEQ | 28.2147 |
| Maximum von Mises stress | `1.600e9 Pa` |
| Average bullet U3 | `-0.01945 m` |

**Result preview**

![Bullet impact result](examples/bullet-plate-penetration/images/bullet_plate_result.png)

**Capability demonstrated**

This case shows a higher-dynamics workflow: the AI agent creates an Abaqus/Explicit impact model, handles contact setup, runs the solver, and uses a post-processing script to read final ODB outputs. It demonstrates how natural-language instructions can drive a complete impact simulation workflow rather than only generating a standalone script.

**Cost**

LLM Cost: about `~&yen;0.5` using DeepSeek for this simple simulation automation task. This estimate includes only LLM/API token usage. It does not include Abaqus software licensing, local computing resources, storage, or solver runtime.

### Case Study 2: Axial Crushing of a Steel Tube

**User task in natural language**

```text
Create an Abaqus simulation of a circular steel tube under axial compression. Build the model, run the analysis, extract the main stress/displacement results, and generate a short report.
```

**What the AI agent completed**

- Generated an Abaqus Python script for a 3D deformable circular tube model.
- Defined steel material behavior with elastic and plastic hardening data.
- Created a Static General analysis step with geometric nonlinearity enabled.
- Applied a fixed boundary condition at the lower end and a 10 mm axial compression displacement at the upper end.
- Meshed the tube with C3D8R solid elements.
- Submitted the Abaqus/Standard job and confirmed successful completion.
- Read the result database and summarized key outputs in a Markdown report.

**Model and analysis setup**

| Item | Value |
| --- | --- |
| Geometry | Circular tube, OD 50 mm, ID 40 mm, length 200 mm |
| Material | Steel, E = 210 GPa, nu = 0.3, yield stress = 250 MPa |
| Solver | Abaqus/Standard 2024, Static General |
| Nonlinearity | `nlgeom=ON` |
| Mesh | C3D8R, global seed size 2.5 mm |
| Loading | Upper-end axial displacement `U3 = -10 mm` |
| Status | Analysis completed successfully in 26 increments |

**Generated result files**

Files included in this repository:

- [`examples/pipe-axial-crush/pipe_axial_crush.py`](examples/pipe-axial-crush/pipe_axial_crush.py)
- [`examples/pipe-axial-crush/pipe_axial_crush_report.md`](examples/pipe-axial-crush/pipe_axial_crush_report.md)
- [`examples/pipe-axial-crush/images/`](examples/pipe-axial-crush/images/)

Files generated during the local Abaqus run:

- `PipeAxialCrush.odb`
- `PipeAxialCrush.inp`
- `PipeAxialCrush.sta`
- `PipeAxialCrush.msg`
- `PipeAxialCrush.dat`

Large solver outputs such as `.odb` and `.inp` are intentionally not committed by default because they can be large and machine-specific.

**Result summary**

| Output | Value |
| --- | --- |
| Maximum von Mises stress | 336.5 MPa |
| Maximum axial displacement U3 | 10.000 mm |
| Maximum reaction force | 2462.7 N |
| Final step time | 1.000 |

**Result previews**

The images below are generated from the example run and stored with relative paths so they render on GitHub.

![Pipe axial crush overview](examples/pipe-axial-crush/images/pipe_axial_crush_overview.png)

| Preview | Preview |
| --- | --- |
| ![Pipe axial crush result 1](examples/pipe-axial-crush/images/7216d89e4599208801cd1baf17ca3f86.png) | ![Pipe axial crush result 2](examples/pipe-axial-crush/images/6e2476a118e627786a33a5894e77931f.png) |
| ![Pipe axial crush result 3](examples/pipe-axial-crush/images/3dce79a919eb3e0402a8c69ae09e3b37.png) | ![Pipe axial crush result 4](examples/pipe-axial-crush/images/29d05982fa8ea975e3d11dd9659b4247.png) |

**Capability demonstrated**

This case shows the end-to-end value of the MCP workflow: the user describes an engineering problem, the AI agent writes Abaqus Python, runs a nonlinear static simulation, extracts numerical results, and produces a readable engineering report. It demonstrates practical automation for routine structural simulation tasks rather than only isolated script generation.

**Cost**

LLM Cost: about `~&yen;0.5` using DeepSeek for this simple simulation automation task. This estimate includes only LLM/API token usage. It does not include Abaqus software licensing, local computing resources, storage, or solver runtime.

## Cost Efficiency

With DeepSeek models, simple Abaqus automation tasks can cost as low as around `&yen;0.5` in LLM usage, making AI-assisted simulation workflows practical for everyday engineering and research use.

The main benefit is not only that each prompt is cheap. Low LLM cost makes iterative engineering workflows more realistic:

- trying several modeling approaches
- generating post-processing scripts repeatedly
- running small parameter sweeps
- extracting result summaries from many ODB files
- creating report-ready plots or images after a solve

Cost notes:

- The estimate refers only to LLM/API token usage.
- Abaqus licensing is not included.
- Local hardware, solver runtime, storage, and electricity are not included.
- Larger models, long conversations, or large generated scripts will increase the AI API cost.

## Configuration

### Abaqus executable

The wrapper searches for Abaqus in this order:

1. `%ABAQUS_COMMAND%`
2. `C:\SIMULIA\Commands\abaqus.bat`
3. `C:\cae\Software\abaqus.bat`

If Abaqus is somewhere else, set `ABAQUS_COMMAND` to the full path of `abaqus.bat`.

Example:

```powershell
$env:ABAQUS_COMMAND = "D:\SIMULIA\Commands\abaqus.bat"
```

### Manual backend start and stop

Start the Abaqus backend manually:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\path\to\abaqus-mcp\start_backend.ps1"
```

Stop the backend and release the Abaqus license:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\path\to\abaqus-mcp\stop_backend.ps1"
```

### Optional Abaqus GUI plugin

The optional GUI menu plugin is preserved from the upstream project:

```text
abaqus_plugins/mcp_control
```

If you use the Abaqus GUI workflow, copy this folder to your Abaqus plugin directory. The noGUI autostart backend is still recommended for opencode because it avoids relying on a manually started GUI session.

## Tools / MCP Capabilities

This project exposes the following MCP resource and tools.

### Resource

| Resource | Purpose |
| --- | --- |
| `abaqus://status` | Current Abaqus MCP backend status, including running/stopped state and heartbeat metadata. |

### Tools

| Tool | Purpose |
| --- | --- |
| `check_abaqus_connection` | Check whether the Abaqus-side MCP plugin is running and responding. |
| `execute_script` | Execute Python inside the Abaqus kernel environment with access to `mdb` and `session`. |
| `get_model_info` | Return structured information about models, parts, materials, steps, loads, BCs, interactions, and assembly instances. |
| `list_jobs` | List jobs defined in the current Abaqus session and their statuses. |
| `submit_job` | Submit an existing Abaqus job by name and wait for completion. |
| `get_odb_info` | Open an ODB file read-only and return metadata such as steps, frame counts, parts, and instances. |
| `get_viewport_image` | Capture an Abaqus viewport image as a base64 data URL. |
| `ping` | Send a lightweight ping to the Abaqus backend and expect `pong`. |

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

## Notes and Limitations

- This project does not remove the need for a valid Abaqus installation and license.
- The AI agent can generate and execute Abaqus Python, but the quality of the simulation still depends on engineering judgment, model assumptions, mesh quality, material data, and verification.
- `submit_job` submits jobs already defined in the current Abaqus session.
- `get_odb_info` returns ODB metadata; detailed custom extraction may require an agent-generated Abaqus Python post-processing script via `execute_script`.
- If the MCP client reports `stopped`, the Abaqus-side polling loop is not running. Restarting the MCP client usually fixes this because the autostart wrapper should relaunch the backend.
- Opening an `.odb` file is not normally the cause of `stopped`; the status means the backend polling process is absent, stale, or stopped.
- This adaptation is primarily tested on Windows.

## Troubleshooting

If autostart does not work:

- check `autostart.log`
- check `abaqus_mcp_backend.err.log`
- verify your Abaqus path or set `%ABAQUS_COMMAND%`
- run `start_backend.ps1` manually
- call `check_abaqus_connection` again

If a generated Abaqus script fails, ask the agent to inspect the Abaqus error message and revise the script. Treat AI-generated simulation scripts as drafts that should be reviewed before engineering use.

## Roadmap

- Add more real example case folders with images, prompts, scripts, and result summaries.
- Add reusable prompt templates for common workflows such as static analysis, explicit impact, modal analysis, and ODB extraction.
- Add richer post-processing helpers for CSV export and report generation.
- Improve packaging for easier installation across machines.
- Explore non-Windows startup support.
- Add CI checks for README links and Python syntax where possible without requiring Abaqus.

## Attribution

This project is based on [Cai-aa/abaqus-mcp](https://github.com/Cai-aa/abaqus-mcp).

The main adaptation here is the opencode-oriented autostart layer and packaging cleanup. The original MCP server, Abaqus plugin, file-based IPC design, and MIT license are from the upstream project.
