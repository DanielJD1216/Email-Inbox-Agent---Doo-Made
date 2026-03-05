$ErrorActionPreference = "Stop"

param(
    [string]$TaskName = "EmailInboxAgent"
)

Write-Host "Removing scheduled task '$TaskName'..."
schtasks.exe /Delete /TN $TaskName /F | Out-Host

Write-Host ""
Write-Host "Scheduler disabled."
