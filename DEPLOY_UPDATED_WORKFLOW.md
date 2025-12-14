# Deploy Updated Workflow to Production

## What Changed

The `download_sanctions_lists` Cloud Function now:

1. Downloads and parses sanctions lists ✓ (same as before)
2. **NEW**: Automatically triggers two-stage import with validation
3. **NEW**: Uses `merge=False` to prevent data corruption
4. **NEW**: Creates comprehensive audit logs with full change history

## Deployment Steps

### Option 1: Deploy via Firebase CLI (Recommended)

```powershell
# From project root directory
cd C:\Users\Slavko\SanctionDefenderApp

# Deploy the updated function (uses firebase.json config)
firebase deploy --only functions:download_sanctions_lists
```

This will:

- Deploy the updated `functions/main.py`
- Deploy the `functions/import_sanctions_two_stage.py` module
- Keep existing Cloud Scheduler job unchanged
- Run at 04:00 UTC daily

### Option 2: Deploy via gcloud CLI

```powershell
$ProjectId = "sanction-defender-firebase"
$Region = "europe-west1"
$FunctionName = "download_sanctions_lists"

cd C:\Users\Slavko\SanctionDefenderApp\functions

gcloud functions deploy $FunctionName `
  --gen2 `
  --runtime python311 `
  --trigger-http `
  --entry-point download_sanctions_lists `
  --allow-unauthenticated `
  --timeout 600 `
  --memory 512MB `
  --project $ProjectId `
  --region $Region
```

### Option 3: Update Scheduler Job (if not using firebase deploy)

If you want to ensure the scheduler is updated:

```powershell
$ProjectId = "sanction-defender-firebase"
$Region = "europe-west1"
$JobName = "sanctions-daily-job"

# Get the function URL
$FunctionUrl = gcloud functions describe download_sanctions_lists `
  --gen2 `
  --region $Region `
  --project $ProjectId `
  --format='value(serviceConfig.uri)'

Write-Host "Function URL: $FunctionUrl"

# Delete old job
gcloud scheduler jobs delete $JobName `
  --location $Region `
  --project $ProjectId `
  --quiet

# Create new job with updated function
gcloud scheduler jobs create http $JobName `
  --schedule "0 4 * * *" `
  --uri $FunctionUrl `
  --http-method POST `
  --location $Region `
  --project $ProjectId
```

## Verification

### 1. Check Function Deployment

```powershell
gcloud functions describe download_sanctions_lists `
  --gen2 `
  --region europe-west1 `
  --project sanction-defender-firebase
```

Should show:

- Status: ACTIVE
- Latest execution status: OK or latest update timestamp

### 2. Check Scheduler Job

```powershell
gcloud scheduler jobs describe sanctions-daily-job `
  --location europe-west1 `
  --project sanction-defender-firebase
```

Should show:

- Schedule: `0 4 * * *`
- State: ENABLED

### 3. Test Manual Execution

```powershell
# Trigger the function
$url = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/download_sanctions_lists"
$response = Invoke-WebRequest -Uri $url -Method POST
$result = $response.Content | ConvertFrom-Json

# Should show:
# - status: "completed"
# - details: [source files downloaded and imported]
# - details.*.import_status: "completed_with_validation"

$result | ConvertTo-Json -Depth 5
```

### 4. Check Logs

```powershell
# View recent function logs (last 10 minutes)
gcloud functions logs read download_sanctions_lists `
  --limit 100 `
  --gen2 `
  --region europe-west1 `
  --project sanction-defender-firebase
```

Look for:

- `[>] Starting daily sanctions list download`
- `[>] Triggering two-stage import validation`
- `[OK] COMMIT SUCCESSFUL` (from import stage)
- Import status per source

### 5. Verify Firestore Audit Logs

```powershell
# Check if audit logs were created
# Via Cloud Console:
# Firestore > Collections > audit_logs > [import_YYYYMMDD_HHMMSS]
```

## Rollback Plan

If the new function causes issues:

```powershell
# Rollback to previous version
gcloud functions deploy download_sanctions_lists `
  --gen2 `
  --runtime python311 `
  --trigger-http `
  --entry-point download_sanctions_lists `
  --update-from-source <previous-backup.zip> `
  --project sanction-defender-firebase `
  --region europe-west1
```

Or redeploy the backup:

```powershell
# If you saved a backup of functions/ directory
Copy-Item "C:\backup\functions\main.py" "C:\Users\Slavko\SanctionDefenderApp\functions\main.py" -Force
firebase deploy --only functions:download_sanctions_lists
```

## Files Changed

| File                                      | Change                              | Status       |
| ----------------------------------------- | ----------------------------------- | ------------ |
| `functions/main.py`                       | Updated to trigger two-stage import | ✅ Ready     |
| `functions/import_sanctions_two_stage.py` | Copied from root                    | ✅ Ready     |
| `firebase.json`                           | No changes needed                   | ✅ Unchanged |
| Cloud Scheduler                           | No changes needed                   | ✅ Unchanged |

## Post-Deployment Checklist

- [ ] Function deployed successfully
- [ ] Manual test trigger completed
- [ ] No errors in Cloud Function logs
- [ ] Audit logs created in Firestore
- [ ] Firestore document counts increased
- [ ] Scheduler still scheduled for 04:00 UTC
- [ ] Team notified of changes

## Support

If deployment fails:

1. Check error messages in `gcloud functions deploy` output
2. View detailed logs: Cloud Console > Cloud Functions > download_sanctions_lists > Logs
3. Check Python syntax: `python -m py_compile functions/main.py`
4. Verify `.firebaserc` has correct project ID
