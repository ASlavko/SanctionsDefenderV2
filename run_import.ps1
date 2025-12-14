# Wrapper script to run the two-stage import with proper credentials
# This ensures the GOOGLE_APPLICATION_CREDENTIALS environment variable is set

$ErrorActionPreference = "Stop"

# Set up environment
$adc_path = "$env:APPDATA\gcloud\legacy_credentials\azman.slavko@gmail.com\adc.json"

if(-not (Test-Path $adc_path)) {
    Write-Host "[X] ADC file not found at: $adc_path" -ForegroundColor Red
    Write-Host "[!] Make sure you have gcloud authenticated with:" -ForegroundColor Yellow
    Write-Host "    gcloud auth application-default login"
    exit 1
}

Write-Host "[>] Setting up credentials from: $adc_path" -ForegroundColor Cyan
$env:GOOGLE_APPLICATION_CREDENTIALS = $adc_path
$env:PYTHONIOENCODING = 'utf-8'

Write-Host "[>] GOOGLE_APPLICATION_CREDENTIALS is set" -ForegroundColor Green
Write-Host "[>] Starting two-stage sanctions import..." -ForegroundColor Cyan
Write-Host ""

# Run the import
cd C:\Users\Slavko\SanctionDefenderApp
& C:/Users/Slavko/SanctionDefenderApp/functions/venv/Scripts/python.exe import_sanctions_two_stage.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Import completed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[ERROR] Import failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
