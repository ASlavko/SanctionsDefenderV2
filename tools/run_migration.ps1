# PowerShell script to run the migration SQL file for PostgreSQL
# Usage: .\run_migration.ps1 -DbUser "your_user" -DbName "your_db" [-Host "localhost"] [-Port 5432]

param(
    [string]$DbUser,
    [string]$DbName,
    [string]$Host = "localhost",
    [int]$Port = 5432
)

$scriptPath = Join-Path $PSScriptRoot "..\tools\2025-12-28_decision_audit_migration.sql"

Write-Host "Running migration script: $scriptPath"

$env:PGPASSWORD = Read-Host -Prompt "Enter PostgreSQL password for user $DbUser"

$psqlCmd = "psql -U $DbUser -d $DbName -h $Host -p $Port -f `"$scriptPath`""

Write-Host "Executing: $psqlCmd"

Invoke-Expression $psqlCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration completed successfully."
} else {
    Write-Host "Migration failed with exit code $LASTEXITCODE."
}
