$ErrorActionPreference = "Stop"

$McpHome = Split-Path -Parent $MyInvocation.MyCommand.Path
$StatusFile = Join-Path $McpHome "status.json"
$StopFile = Join-Path $McpHome "stop.flag"
$StartScript = Join-Path $McpHome "start_abaqus_mcp_nogui.py"

$Abaqus = $env:ABAQUS_COMMAND
if (-not $Abaqus) {
    if (Test-Path -LiteralPath "C:\SIMULIA\Commands\abaqus.bat") {
        $Abaqus = "C:\SIMULIA\Commands\abaqus.bat"
    } elseif (Test-Path -LiteralPath "C:\cae\Software\abaqus.bat") {
        $Abaqus = "C:\cae\Software\abaqus.bat"
    }
}
if (-not $Abaqus) {
    throw "Abaqus launcher not found. Set ABAQUS_COMMAND to the full path of abaqus.bat."
}

if (Test-Path -LiteralPath $StatusFile) {
    $status = Get-Content -LiteralPath $StatusFile -Raw | ConvertFrom-Json
    if ($status.status -eq "running") {
        Write-Host "Abaqus MCP backend is already running."
        exit 0
    }
}

if (Test-Path -LiteralPath $StopFile) {
    Remove-Item -LiteralPath $StopFile -Force
}

$env:ABAQUS_MCP_HOME = $McpHome
$process = Start-Process `
    -FilePath $Abaqus `
    -ArgumentList @("cae", "noGUI=$StartScript") `
    -WorkingDirectory $McpHome `
    -WindowStyle Hidden `
    -PassThru

Write-Host "Started Abaqus MCP backend process: $($process.Id)"

$deadline = (Get-Date).AddSeconds(60)
while ((Get-Date) -lt $deadline) {
    if (Test-Path -LiteralPath $StatusFile) {
        $status = Get-Content -LiteralPath $StatusFile -Raw | ConvertFrom-Json
        if ($status.status -eq "running") {
            Write-Host "Abaqus MCP backend is running."
            exit 0
        }
    }
    Start-Sleep -Milliseconds 500
}

throw "Timed out waiting for Abaqus MCP backend to become running."
