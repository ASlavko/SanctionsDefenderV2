# Deploy Search API and Frontend

$gcPath = "C:\Users\Slavko\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
$projectId = "sanction-defender-firebase"
$region = "europe-west1"

Write-Host "Deploying Sanctions Search API and Frontend..." -ForegroundColor Cyan

# Step 1: Deploy Search API
Write-Host "`n[Step 1] Deploying Search API..." -ForegroundColor Yellow
& $gcPath functions deploy search_sanctions `
  --region=$region `
  --runtime=python311 `
  --trigger-http `
  --source=functions `
  --entry-point=search_sanctions `
  --memory=512MB `
  --timeout=30s `
  --project=$projectId `
  --allow-unauthenticated `
  --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Search API deployed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Search API deployment failed" -ForegroundColor Red
    exit 1
}

# Step 2: Get the function URL
Write-Host "`n[Step 2] Getting function URL..." -ForegroundColor Yellow
$functionUrl = & $gcPath functions describe search_sanctions `
  --region=$region `
  --project=$projectId `
  --format='value(httpsTrigger.url)'

Write-Host "Function URL: $functionUrl" -ForegroundColor Cyan

# Step 3: Update search.html with API URL
Write-Host "`n[Step 3] Updating search.html with API URL..." -ForegroundColor Yellow
$searchHtmlPath = ".\public\search.html"
$htmlContent = Get-Content $searchHtmlPath -Raw
$htmlContent = $htmlContent -replace "const API_URL = '/search';", "const API_URL = '$functionUrl';"
$htmlContent | Set-Content $searchHtmlPath -Encoding UTF8
Write-Host "✓ search.html updated with API URL" -ForegroundColor Green

# Step 4: Deploy Frontend
Write-Host "`n[Step 4] Deploying frontend..." -ForegroundColor Yellow
firebase deploy --only hosting --project=$projectId --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend deployed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend deployment failed" -ForegroundColor Red
    exit 1
}

# Step 5: Get hosting URL
Write-Host "`n[Step 5] Getting hosting URL..." -ForegroundColor Yellow
$hostingUrl = & $gcPath firebase hosting:sites:list `
  --project=$projectId `
  --format='value(defaultUrl)' 2>$null | Select-Object -First 1

if ($hostingUrl) {
    Write-Host "Hosting URL: $hostingUrl/search.html" -ForegroundColor Cyan
}

Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Cyan

Write-Host @"

✓ Search API Endpoint:
  $functionUrl

✓ Frontend URL:
  $hostingUrl/search.html

✓ Documentation:
  See SEARCH_API.md for full API documentation

Next Steps:
  1. Visit the frontend to test the search
  2. Try searching for common sanctions entities
  3. Review logs if you encounter issues

View Logs:
  gcloud functions logs read search_sanctions --region=$region --project=$projectId

"@ -ForegroundColor White
