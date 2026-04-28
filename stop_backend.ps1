$ErrorActionPreference = "Stop"

$McpHome = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:ABAQUS_MCP_HOME = $McpHome

python (Join-Path $McpHome "stop_mcp.py")
Start-Sleep -Seconds 2

$StatusFile = Join-Path $McpHome "status.json"
if (Test-Path -LiteralPath $StatusFile) {
    Get-Content -LiteralPath $StatusFile
}
