# Google Cloud CLI Installation Script for Windows
# Run this in PowerShell as Administrator

Write-Host "Installing Google Cloud CLI..." -ForegroundColor Cyan

# Download the installer
$installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
$installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"

Write-Host "Downloading installer..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

Write-Host "Running installer..." -ForegroundColor Yellow
Write-Host "Please follow the installation wizard." -ForegroundColor Green
Start-Process -FilePath $installerPath -Wait

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "Please restart your PowerShell terminal and run: gcloud init" -ForegroundColor Yellow

Remove-Item $installerPath -ErrorAction SilentlyContinue
