# Deploying the daily sanctions downloader + parser

This document shows how to deploy `download_sanctions_lists` as a Google Cloud Function triggered daily by Cloud Scheduler (via Pub/Sub).

Prerequisites

- Install and authenticate `gcloud` CLI and enable Cloud Functions, Cloud Scheduler, Pub/Sub and Firestore APIs for your project.
- Ensure your project id is set: `gcloud config set project YOUR_PROJECT_ID`
- Install Python dependencies from `functions/requirements.txt` when deploying (Cloud Functions will install them).

Steps

1. Create a Pub/Sub topic that will trigger the function:

```powershell
gcloud pubsub topics create sanctions-daily-trigger
```

2. Deploy the Cloud Function. This repository exposes the function `download_sanctions_lists` in `functions/main.py`.
   - Using `gcloud` (recommended):

```powershell
gcloud functions deploy download_sanctions_lists \
  --entry-point download_sanctions_lists \
  --runtime python311 \
  --trigger-topic sanctions-daily-trigger \
  --region us-central1 \
  --timeout 540s \
  --memory 512MB
```

3. Create a Cloud Scheduler job that publishes to the topic daily. The schedule below runs at 04:00 UTC daily — adjust to your timezone.

```powershell
gcloud scheduler jobs create pubsub sanctions-daily-job \
  --schedule "0 4 * * *" \
  --time-zone "UTC" \
  --topic sanctions-daily-trigger \
  --message-body '{}' \
  --location us-central1
```

Notes and testing

- To test immediately, publish a message to the topic:

```powershell
gcloud pubsub topics publish sanctions-daily-trigger --message '{}'
```

- If you want the Cloud Function to write into Firestore emulator during local testing, set the environment variable `FIRESTORE_EMULATOR_HOST` to the emulator host (for example `localhost:8080`) and start the Firestore emulator via the Firebase emulator suite (requires Java for the emulator). The Cloud Function code handles emulator detection and will try to initialize firebase_admin accordingly.

- If you prefer HTTP-triggered function, deploy with `--trigger-http` and protect it with IAM; then schedule an HTTP job in Cloud Scheduler.

Security

- Keep production credentials and service accounts secure. If the function needs elevated permissions to write to Firestore, grant them to the function's service account via IAM.

If you want, I can create a Deployment script (PowerShell) that runs the above `gcloud` commands and validates the job creation.
