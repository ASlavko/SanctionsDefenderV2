# Quick Start: Deploy and Schedule Daily Sanctions Download

## Prerequisites

- **Firebase CLI** installed and logged in (`firebase login` — already done ✓)
- **GCP Project** with Firestore enabled (`sanction-defender-firebase` — confirmed ✓)

## Step 1: Deploy the Cloud Function

Deploy the `download_sanctions_lists` function to GCP Cloud Functions:

```powershell
$env:JAVA_HOME = 'C:\Java\openjdk17\jdk-17.0.13+11'

gcloud functions deploy download_sanctions_lists `
  --runtime python3.11 `
  --trigger-topic sanctions-daily-trigger `
  --entry-point download_sanctions_lists `
  --memory 512MB `
  --timeout 540 `
  --project sanction-defender-firebase
```

## Step 2: Create a Pub/Sub Topic (if not exists)

```powershell
gcloud pubsub topics create sanctions-daily-trigger `
  --project sanction-defender-firebase
```

## Step 3: Create a Cloud Scheduler Job

Schedule the function to run daily at 04:00 UTC:

```powershell
gcloud scheduler jobs create pubsub sanctions-daily-job `
  --schedule "0 4 * * *" `
  --time-zone "UTC" `
  --topic sanctions-daily-trigger `
  --message-body '{}' `
  --location us-central1 `
  --project sanction-defender-firebase
```

(Adjust the schedule and time-zone to your preference.)

## Step 4: Test the Cloud Function Immediately

To test without waiting for the schedule, publish a message:

```powershell
gcloud pubsub topics publish sanctions-daily-trigger `
  --message '{}' `
  --project sanction-defender-firebase
```

## Verification

- View function logs:

  ```powershell
  gcloud functions log download_sanctions_lists `
    --limit 50 `
    --project sanction-defender-firebase
  ```

- View Cloud Scheduler job status:
  ```powershell
  gcloud scheduler jobs describe sanctions-daily-job `
    --location us-central1 `
    --project sanction-defender-firebase
  ```

---

## Troubleshooting

**Issue:** `gcloud: The term 'gcloud' is not recognized`

**Solution:** Install the Google Cloud SDK:

1. Download from: https://cloud.google.com/sdk/docs/install
2. Run the installer
3. Restart your terminal

**Issue:** Firestore collection not getting data

**Possible causes:**

1. Cloud Function deployment failed — check logs with `gcloud functions log`
2. Firestore permissions — ensure the Cloud Functions service account has Firestore write access
3. Parser errors — check if parsed JSONL files are being created

---

## Next Steps (Optional)

- **Enable audit logging** in the Cloud Function to track downloads and imports
- **Add error alerts** via Cloud Monitoring
- **Customize the schedule** in Step 3 to match your needs (e.g., `0 0 * * 0` = weekly)
- **Set up Firestore rules** to control who can read/write sanctions data
