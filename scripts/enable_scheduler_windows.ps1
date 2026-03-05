param(
    [string]$TaskName = "EmailInboxAgent",
    [ValidateRange(1, 60)]
    [int]$EveryMinutes = 2
)

$ErrorActionPreference = "Stop"

$repoPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonPath = Join-Path $repoPath ".venv\Scripts\python.exe"
$logsDir = Join-Path $repoPath "logs"
$logPath = Join-Path $logsDir "agent.log"

if (-not (Test-Path $pythonPath)) {
    Write-Host "Virtual environment not found: $pythonPath" -ForegroundColor Yellow
    Write-Host "Run this first:"
    Write-Host "  .\scripts\first_run_windows.ps1"
    exit 1
}

New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

$taskCommand = "cmd.exe /c cd /d `"$repoPath`" && `"$pythonPath`" -m app.main >> `"$logPath`" 2>&1"

Write-Host "Creating/updating scheduled task '$TaskName' (every $EveryMinutes minute(s))..."
schtasks.exe /Create /TN $TaskName /SC MINUTE /MO $EveryMinutes /TR $taskCommand /F | Out-Host

Write-Host "Starting task now..."
schtasks.exe /Run /TN $TaskName | Out-Host

Write-Host ""
Write-Host "Scheduler is enabled."
Write-Host "Task name: $TaskName"
Write-Host "Interval : every $EveryMinutes minute(s)"
Write-Host "Log file : $logPath"
Write-Host ""
Write-Host "Check status:"
Write-Host "  schtasks /Query /TN $TaskName /V /FO LIST"
Write-Host "Disable later:"
Write-Host "  .\scripts\disable_scheduler_windows.ps1 -TaskName `"$TaskName`""
