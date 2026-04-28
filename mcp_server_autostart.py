#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Autostart wrapper for Abaqus MCP.

OpenCode starts only the MCP stdio server. The Abaqus-side polling loop is a
separate Abaqus process, so this wrapper starts that backend first when needed.
"""

import json
import os
import runpy
import subprocess
import sys
import time
from pathlib import Path


MCP_HOME = Path(os.environ.get("ABAQUS_MCP_HOME", Path(__file__).resolve().parent))
STATUS_FILE = MCP_HOME / "status.json"
STOP_FILE = MCP_HOME / "stop.flag"
REAL_SERVER = MCP_HOME / "mcp_server.py"
START_SCRIPT = MCP_HOME / "start_abaqus_mcp_nogui.py"
LOG_FILE = MCP_HOME / "autostart.log"

DEFAULT_ABAQUS_CANDIDATES = (
    r"C:\SIMULIA\Commands\abaqus.bat",
    r"C:\cae\Software\abaqus.bat",
)


def log(message):
    try:
        MCP_HOME.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + message + "\n")
    except Exception:
        pass


def find_abaqus():
    configured = os.environ.get("ABAQUS_COMMAND")
    candidates = [configured] if configured else []
    candidates.extend(DEFAULT_ABAQUS_CANDIDATES)
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    return None


def read_status():
    try:
        with STATUS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def status_is_running():
    status = read_status()
    if status.get("status") != "running":
        return False
    try:
        timestamp = float(status.get("timestamp", 0))
    except Exception:
        return False
    return time.time() - timestamp < 20


def ensure_abaqus_backend():
    if status_is_running():
        log("Abaqus MCP backend already running")
        return

    if STOP_FILE.exists():
        try:
            STOP_FILE.unlink()
        except Exception:
            pass

    abaqus = find_abaqus()
    if not abaqus:
        log("Abaqus launcher not found. Set ABAQUS_COMMAND to abaqus.bat.")
        return
    if not START_SCRIPT.exists():
        log("Abaqus MCP start script not found: " + str(START_SCRIPT))
        return

    out = MCP_HOME / "abaqus_mcp_backend.out.log"
    err = MCP_HOME / "abaqus_mcp_backend.err.log"
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    env = os.environ.copy()
    env["ABAQUS_MCP_HOME"] = str(MCP_HOME)

    log("Starting Abaqus MCP backend with " + str(abaqus))
    with out.open("ab") as stdout, err.open("ab") as stderr:
        subprocess.Popen(
            [str(abaqus), "cae", "noGUI=" + str(START_SCRIPT)],
            cwd=str(MCP_HOME),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            creationflags=creationflags,
        )

    deadline = time.time() + 75
    while time.time() < deadline:
        if status_is_running():
            log("Abaqus MCP backend running")
            return
        time.sleep(0.5)

    log("Timed out waiting for Abaqus MCP backend")


if __name__ == "__main__":
    os.environ["ABAQUS_MCP_HOME"] = str(MCP_HOME)
    ensure_abaqus_backend()
    sys.argv = [str(REAL_SERVER)]
    runpy.run_path(str(REAL_SERVER), run_name="__main__")
