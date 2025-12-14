# Deploy Batch Screening API and Frontend (Firebase only)
# This script deploys the frontend to Firebase Hosting
# For Cloud Functions deployment, you'll need to configure gcloud CLI

param(
    [string]$ProjectId = "sanction-defender-firebase"
)

Write-Host "🚀 Deploying Sanctions Defender Frontend" -ForegroundColor Cyan
Write-Host "Project: $ProjectId" -ForegroundColor Yellow
Write-Host ""

# Check if firebase is installed
$firebaseExists = Get-Command firebase -ErrorAction SilentlyContinue
if (-not $firebaseExists) {
    Write-Host "❌ Error: firebase CLI not found. Please install Firebase CLI." -ForegroundColor Red
    exit 1
}

# Note about API URLs
Write-Host "⚠️  Note: You'll need to deploy Cloud Functions separately and update API URLs manually" -ForegroundColor Yellow
Write-Host ""
Write-Host "Cloud Functions to deploy:" -ForegroundColor Cyan
Write-Host "  1. search_sanctions (from functions/search_api.py)" -ForegroundColor White
Write-Host "  2. batch_screening (from functions/batch_screening_api.py)" -ForegroundColor White
Write-Host ""
Write-Host "After deploying functions, update these files:" -ForegroundColor Cyan
Write-Host "  • public/search.html - Update API_URL constant" -ForegroundColor White
Write-Host "  • public/batch_screening.html - Update API_URL constant" -ForegroundColor White
Write-Host ""

$response = Read-Host "Continue with frontend deployment? (y/n)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

# Deploy frontend to Firebase Hosting
Write-Host ""
Write-Host "🌐 Deploying frontend to Firebase Hosting..." -ForegroundColor Cyan
firebase deploy --only hosting

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to deploy frontend." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Deploy Cloud Functions using GCP Console or gcloud CLI" -ForegroundColor White
Write-Host "  2. Update API URLs in public/search.html and public/batch_screening.html" -ForegroundColor White
Write-Host "  3. Redeploy frontend: firebase deploy --only hosting" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Frontend URL: https://$ProjectId.web.app" -ForegroundColor Green
Write-Host "🌐 Alternative: https://$ProjectId.firebaseapp.com" -ForegroundColor Green
