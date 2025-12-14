# Verify ADC Setup Script
# Run this after setting up gcloud auth application-default login

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "VERIFYING APPLICATION DEFAULT CREDENTIALS SETUP" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Check if gcloud is installed
Write-Host "`n1. Checking gcloud CLI installation..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "   ✓ gcloud CLI installed: $gcloudVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ gcloud CLI not found. Please install it first." -ForegroundColor Red
    Write-Host "     Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Check current gcloud config
Write-Host "`n2. Checking gcloud configuration..." -ForegroundColor Yellow
try {
    $account = gcloud config get-value account 2>$null
    $project = gcloud config get-value project 2>$null
    
    if ($account) {
        Write-Host "   ✓ Logged in as: $account" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Not logged in. Run: gcloud init" -ForegroundColor Red
    }
    
    if ($project) {
        Write-Host "   ✓ Default project: $project" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ No default project set" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ Error checking gcloud config" -ForegroundColor Red
}

# Check for ADC credentials file
Write-Host "`n3. Checking Application Default Credentials..." -ForegroundColor Yellow
$adcPath = "$env:APPDATA\gcloud\application_default_credentials.json"

if (Test-Path $adcPath) {
    Write-Host "   ✓ ADC file found at: $adcPath" -ForegroundColor Green
    
    # Check if file is valid JSON
    try {
        $adcContent = Get-Content $adcPath -Raw | ConvertFrom-Json
        if ($adcContent.type) {
            Write-Host "   ✓ Credential type: $($adcContent.type)" -ForegroundColor Green
        }
    } catch {
        Write-Host "   ⚠ ADC file exists but may be invalid" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ ADC file not found" -ForegroundColor Red
    Write-Host "     Run: gcloud auth application-default login" -ForegroundColor Yellow
}

# Test Firebase Admin SDK
Write-Host "`n4. Testing Firebase Admin SDK connection..." -ForegroundColor Yellow
Write-Host "   Running Python test..." -ForegroundColor Gray

$pythonScript = @"
import sys
try:
    import firebase_admin
    from firebase_admin import firestore
    
    # Try to initialize
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app()
    
    # Try to get Firestore client
    db = firestore.client()
    print('   ✓ Firebase Admin SDK initialized successfully')
    print('   ✓ Firestore client created')
    sys.exit(0)
except Exception as e:
    print(f'   ✗ Error: {e}')
    sys.exit(1)
"@

$pythonScript | Out-File -FilePath "$env:TEMP\test_adc.py" -Encoding UTF8

try {
    $result = & "C:/Users/Slavko/SanctionDefenderApp/functions/venv/Scripts/python.exe" "$env:TEMP\test_adc.py" 2>&1
    Write-Host $result
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n   ✓ All checks passed!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ Python test failed" -ForegroundColor Red
}

Remove-Item "$env:TEMP\test_adc.py" -ErrorAction SilentlyContinue

Write-Host "`n" + "=" * 70 -ForegroundColor Cyan
Write-Host "VERIFICATION COMPLETE" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. If gcloud is not installed: Run install_gcloud.ps1" -ForegroundColor White
Write-Host "  2. If not logged in: Run 'gcloud init'" -ForegroundColor White
Write-Host "  3. If ADC not set up: Run 'gcloud auth application-default login'" -ForegroundColor White
Write-Host "  4. Set project: Run 'gcloud config set project sanction-defender-firebase'" -ForegroundColor White
