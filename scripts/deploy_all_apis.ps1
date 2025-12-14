# Deploy Batch Screening API and Frontend
# This script deploys both the search and batch screening APIs to Google Cloud Functions
# and the frontend to Firebase Hosting

param(
    [string]$ProjectId = "sanction-defender-firebase",
    [string]$Region = "europe-west1"
)

Write-Host "🚀 Deploying Sanctions Defender - Search & Batch Screening" -ForegroundColor Cyan
Write-Host "Project: $ProjectId" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host ""

# Check if gcloud is installed
$gcloudExists = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudExists) {
    Write-Host "❌ Error: gcloud CLI not found. Please install Google Cloud SDK." -ForegroundColor Red
    exit 1
}

# Check if firebase is installed
$firebaseExists = Get-Command firebase -ErrorAction SilentlyContinue
if (-not $firebaseExists) {
    Write-Host "❌ Error: firebase CLI not found. Please install Firebase CLI." -ForegroundColor Red
    exit 1
}

# Set the project
Write-Host "📌 Setting project to $ProjectId..." -ForegroundColor Cyan
gcloud config set project $ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set project. Please check your project ID." -ForegroundColor Red
    exit 1
}

# Deploy Search API Function
Write-Host ""
Write-Host "📦 Deploying Search API Function..." -ForegroundColor Cyan
gcloud functions deploy search_sanctions `
    --gen2 `
    --runtime=python311 `
    --region=$Region `
    --source=./functions `
    --entry-point=search_sanctions `
    --trigger-http `
    --allow-unauthenticated `
    --timeout=60s `
    --memory=512MB `
    --set-env-vars GOOGLE_CLOUD_PROJECT=$ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to deploy Search API function." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Search API deployed successfully!" -ForegroundColor Green

# Deploy Batch Screening API Function
Write-Host ""
Write-Host "📦 Deploying Batch Screening API Function..." -ForegroundColor Cyan
gcloud functions deploy batch_screening `
    --gen2 `
    --runtime=python311 `
    --region=$Region `
    --source=./functions `
    --entry-point=batch_screening `
    --trigger-http `
    --allow-unauthenticated `
    --timeout=540s `
    --memory=2GB `
    --set-env-vars GOOGLE_CLOUD_PROJECT=$ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to deploy Batch Screening API function." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Batch Screening API deployed successfully!" -ForegroundColor Green

# Get the function URLs
Write-Host ""
Write-Host "🔗 Retrieving function URLs..." -ForegroundColor Cyan

$searchUrl = gcloud functions describe search_sanctions --region=$Region --gen2 --format="value(serviceConfig.uri)" 2>$null
$batchUrl = gcloud functions describe batch_screening --region=$Region --gen2 --format="value(serviceConfig.uri)" 2>$null

if ($searchUrl) {
    Write-Host "Search API URL: $searchUrl" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  Could not retrieve Search API URL. Check Cloud Console." -ForegroundColor Yellow
}

if ($batchUrl) {
    Write-Host "Batch Screening API URL: $batchUrl" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  Could not retrieve Batch Screening API URL. Check Cloud Console." -ForegroundColor Yellow
}

# Update frontend with API URLs
Write-Host ""
Write-Host "📝 Updating frontend with API URLs..." -ForegroundColor Cyan

if ($searchUrl) {
    # Update search.html
    $searchHtmlPath = ".\public\search.html"
    if (Test-Path $searchHtmlPath) {
        $content = Get-Content $searchHtmlPath -Raw
        $content = $content -replace "const API_URL = '/search';", "const API_URL = '$searchUrl';"
        Set-Content $searchHtmlPath -Value $content
        Write-Host "✅ Updated search.html with API URL" -ForegroundColor Green
    }
}

if ($batchUrl) {
    # Update batch_screening.html
    $batchHtmlPath = ".\public\batch_screening.html"
    if (Test-Path $batchHtmlPath) {
        $content = Get-Content $batchHtmlPath -Raw
        $content = $content -replace "const API_URL = '/batch_screening';", "const API_URL = '$batchUrl';"
        Set-Content $batchHtmlPath -Value $content
        Write-Host "✅ Updated batch_screening.html with API URL" -ForegroundColor Green
    }
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
Write-Host "✅ All components deployed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Deployment Summary:" -ForegroundColor Cyan
Write-Host "  • Search API: $searchUrl" -ForegroundColor White
Write-Host "  • Batch Screening API: $batchUrl" -ForegroundColor White
Write-Host "  • Frontend: https://$ProjectId.web.app" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Deployment complete! Visit your app at: https://$ProjectId.web.app" -ForegroundColor Green
