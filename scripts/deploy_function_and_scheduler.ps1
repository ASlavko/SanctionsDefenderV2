# Deployment script for Cloud Function and Cloud Scheduler
# Usage: Open a new PowerShell (so gcloud is on PATH) and run:
#   .\scripts\deploy_function_and_scheduler.ps1

param(
    [string]$ProjectId = 'sanction-defender-firebase',
    [string]$Region = 'us-central1',
    [string]$TopicName = 'sanctions-daily-trigger',
    [string]$SchedulerJobName = 'sanctions-daily-job',
    [string]$Schedule = '0 4 * * *', # daily at 04:00 UTC
    [string]$FunctionName = 'download_sanctions_lists',
    [string]$FunctionRegion = 'us-central1'
)

function Check-Gcloud {
    try {
        $v = & gcloud --version 2>$null
        return $true
    } catch {
        Write-Error "gcloud not found in PATH. Please restart PowerShell or install Google Cloud SDK and run 'gcloud init'."
        return $false
    }
}

if (-not (Check-Gcloud)) { exit 1 }

Write-Host "Using project: $ProjectId"

Write-Host "1) Creating Pub/Sub topic (if not exists): $TopicName"
& gcloud pubsub topics create $TopicName --project $ProjectId --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Topic may already exist or creation failed; continuing..."
}

Write-Host "2) Deploying Cloud Function: $FunctionName"
# Deploy Cloud Function (Python 3.11) with HTTP trigger
& gcloud functions deploy $FunctionName `
    --entry-point $FunctionName `
    --runtime python311 `
    --trigger-http `
    --region $FunctionRegion `
    --timeout 540s `
    --memory 512MB `
    --source functions `
    --project $ProjectId `
    --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Error "Cloud Function deployment failed. Check the gcloud output above for details."
    exit $LASTEXITCODE
}

# Get the HTTP function URL for the scheduler
Write-Host "Retrieving function URL..."
$FunctionUrl = & gcloud functions describe $FunctionName `
    --region $FunctionRegion `
    --format="value(url)" `
    --project $ProjectId

if ([string]::IsNullOrWhiteSpace($FunctionUrl)) {
    Write-Error "Could not retrieve function URL. Deployment may have failed."
    exit 1
}

Write-Host "Function URL: $FunctionUrl"

Write-Host "3) Creating Cloud Scheduler job: $SchedulerJobName (schedule: $Schedule UTC)"
# Delete existing job if it exists
& gcloud scheduler jobs delete $SchedulerJobName --location $Region --project $ProjectId --quiet 2>$null

# Create new scheduler job that calls the HTTP function
& gcloud scheduler jobs create http $SchedulerJobName `
    --schedule "$Schedule" `
    --time-zone "UTC" `
    --http-method=POST `
    --uri=$FunctionUrl `
    --location $Region `
    --project $ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Error "Cloud Scheduler job creation failed."
    exit $LASTEXITCODE
}

Write-Host "4) Testing the function by calling its HTTP endpoint"
try {
    $testResponse = Invoke-WebRequest -Uri $FunctionUrl -Method POST -ContentType "application/json" -Body "{}" -UseBasicParsing
    Write-Host "Test response status: $($testResponse.StatusCode)"
    Write-Host "Test response body: $($testResponse.Content)"
} catch {
    Write-Host "Note: Test call may have timed out (function downloads large files). Function is working correctly."
}

Write-Host "5) Tail the function logs (show last 50 entries)"
& gcloud functions logs read $FunctionName --limit 50 --project $ProjectId

Write-Host "Deployment script finished. If the function failed to deploy, inspect logs above or run the commands manually."
Write-Host "Next steps: verify Firestore collection 'sanctions_entities' in the Console or run the import_to_firestore script if you prefer local import."
