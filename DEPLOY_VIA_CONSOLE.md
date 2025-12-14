# Cloud Functions Deployment Guide (GCP Console)

Since gcloud CLI is not available in your PATH, follow these steps to deploy the Cloud Functions via the GCP Console.

## Prerequisites

- GCP Console access: https://console.cloud.google.com
- Project: `sanction-defender-firebase`
- Region: `europe-west1`

## Function 1: Search API

### Step 1: Navigate to Cloud Functions

1. Go to https://console.cloud.google.com/functions
2. Click "CREATE FUNCTION"

### Step 2: Configure Function (Basics)

- **Environment**: 2nd gen
- **Function name**: `search_sanctions`
- **Region**: `europe-west1`
- **Trigger type**: HTTPS
- **Authentication**: Allow unauthenticated invocations ✓
- Click "SAVE" then "NEXT"

### Step 3: Configure Runtime

- **Runtime**: Python 3.11
- **Entry point**: `search_sanctions`
- **Source code**: Inline editor or ZIP upload

### Step 4: Upload Code

#### Option A: Inline Editor

1. Delete default content
2. Copy content from `functions/search_api.py` to `main.py`
3. Copy content from `functions/requirements.txt` to `requirements.txt`

#### Option B: ZIP Upload

1. Create a ZIP file containing:
   - `search_api.py` (rename to `main.py`)
   - `requirements.txt`
2. Upload via Cloud Storage or local file

### Step 5: Configure Resources

- **Memory**: 512 MiB
- **Timeout**: 60 seconds
- **Environment variables**:
  - `GOOGLE_CLOUD_PROJECT`: `sanction-defender-firebase`

### Step 6: Deploy

- Click "DEPLOY"
- Wait 2-3 minutes for deployment
- Copy the **Trigger URL** from the function details

---

## Function 2: Batch Screening API

### Step 1: Create Second Function

1. Click "CREATE FUNCTION" again
2. Follow same process as above with these differences:

### Step 2: Configure Function (Basics)

- **Function name**: `batch_screening`
- **Region**: `europe-west1`
- **Trigger type**: HTTPS
- **Authentication**: Allow unauthenticated invocations ✓

### Step 3: Configure Runtime

- **Runtime**: Python 3.11
- **Entry point**: `batch_screening`
- **Source code**: Upload `functions/batch_screening_api.py` as `main.py`

### Step 4: Configure Resources

- **Memory**: 2048 MiB (2 GB) - Important for file processing!
- **Timeout**: 540 seconds (9 minutes)
- **Environment variables**:
  - `GOOGLE_CLOUD_PROJECT`: `sanction-defender-firebase`

### Step 5: Deploy

- Click "DEPLOY"
- Wait 3-4 minutes for deployment
- Copy the **Trigger URL** from the function details

---

## Update Frontend with API URLs

After both functions are deployed:

### 1. Update search.html

Edit `public/search.html` and replace:

```javascript
const API_URL = "/search"; // Will be updated to Cloud Function URL
```

With:

```javascript
const API_URL =
  "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions";
```

### 2. Update batch_screening.html

Edit `public/batch_screening.html` and replace:

```javascript
const API_URL = "/batch_screening"; // Will be updated to Cloud Function URL
```

With:

```javascript
const API_URL =
  "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/batch_screening";
```

### 3. Redeploy Frontend

```powershell
firebase deploy --only hosting
```

---

## Alternative: Deploy via ZIP Files

If inline editing is difficult, you can prepare ZIP files:

### search_sanctions.zip structure:

```
search_sanctions.zip
├── main.py (contents of search_api.py)
└── requirements.txt
```

### batch_screening.zip structure:

```
batch_screening.zip
├── main.py (contents of batch_screening_api.py)
└── requirements.txt
```

Upload these ZIP files via Cloud Storage bucket and reference them in the function configuration.

---

## Verify Deployment

After deployment, test the functions:

### Test Search API:

```powershell
$searchUrl = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"
Invoke-RestMethod -Uri "$searchUrl?q=putin&limit=5" -Method GET
```

### Test Batch Screening API:

Upload a test CSV file via the web UI at:
https://sanction-defender-firebase.web.app/batch_screening.html

---

## Troubleshooting

### Common Issues:

1. **Timeout errors**: Increase timeout in Runtime settings
2. **Memory errors**: Increase memory allocation (especially for batch screening)
3. **Permission denied**: Enable "Allow unauthenticated invocations"
4. **CORS errors**: Ensure CORS headers are in the function code (already included)

### View Logs:

https://console.cloud.google.com/logs/query?project=sanction-defender-firebase

---

## Quick Links

- **Cloud Functions Console**: https://console.cloud.google.com/functions?project=sanction-defender-firebase
- **Cloud Logs**: https://console.cloud.google.com/logs?project=sanction-defender-firebase
- **Firebase Hosting**: https://console.firebase.google.com/project/sanction-defender-firebase/hosting
- **Frontend URL**: https://sanction-defender-firebase.web.app
