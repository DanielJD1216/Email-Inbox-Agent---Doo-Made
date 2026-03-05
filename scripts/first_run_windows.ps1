$ErrorActionPreference = "Stop"

function Get-PythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @("py", "-3")
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @("python")
    }
    return $null
}

Write-Host ""
Write-Host "=== Email Agent First-Run Setup (Windows) ==="
Write-Host ""

$pythonCmd = Get-PythonCommand
if ($null -eq $pythonCmd) {
    Write-Host "Python is not installed (or not on PATH)." -ForegroundColor Yellow
    Write-Host "Install Python 3.11+ from: https://www.python.org/downloads/windows/"
    Write-Host "During install, make sure 'Add python.exe to PATH' is checked."
    exit 1
}

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..."
    if ($pythonCmd.Length -eq 1) {
        & $pythonCmd[0] -m venv .venv
    }
    else {
        & $pythonCmd[0] $pythonCmd[1] -m venv .venv
    }
}

Write-Host "Installing dependencies..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path ".\.env")) {
    Copy-Item .\.env.example .\.env
    Write-Host "Created .env from .env.example"
}

Write-Host ""
Write-Host "Starting interactive setup wizard..."
& .\.venv\Scripts\python.exe -m app.setup_wizard

Write-Host ""
$runNow = Read-Host "Setup complete. Run agent now? (y/n)"
if ($runNow -match "^(y|yes)$") {
    & .\.venv\Scripts\python.exe -m app.main
}

Write-Host ""
$scheduleNow = Read-Host "Enable near-live scheduler every 2 minutes? (y/n)"
if ($scheduleNow -match "^(y|yes)$") {
    & .\scripts\enable_scheduler_windows.ps1 -EveryMinutes 2
}
