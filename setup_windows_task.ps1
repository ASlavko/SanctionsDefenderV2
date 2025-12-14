$ErrorActionPreference = "Stop"

# Get current directory
$WorkDir = Get-Location
$PythonPath = "$WorkDir\venv\Scripts\python.exe"
$ScriptPath = "$WorkDir\run_scheduled_update.py"
$TaskName = "SanctionDefenderUpdate"
$Time = "03:00"

# Verify Python exists
if (-not (Test-Path $PythonPath)) {
    Write-Error "Python executable not found at $PythonPath. Please ensure venv is created."
}

# Create the Action
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory $WorkDir

# Create the Trigger
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time

# Create the Settings (Allow running on battery, wake to run)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun

# Register the Task
Write-Host "Registering task '$TaskName' to run daily at $Time..."
Register-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings -TaskName $TaskName -Description "Daily Sanctions Update for SanctionDefenderApp" -Force

Write-Host "Task registered successfully!"
Write-Host "You can view it in Task Scheduler under the name '$TaskName'."
