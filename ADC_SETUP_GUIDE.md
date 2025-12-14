# Application Default Credentials (ADC) Setup Guide

This guide will help you set up proper authentication for local development and deployment.

## Overview

Application Default Credentials (ADC) is a strategy used by Google Cloud libraries to automatically find credentials based on the application environment. This allows your code to run seamlessly in both local development and production environments.

## Prerequisites

- Windows 10/11
- PowerShell 5.1 or higher
- Active Google account with access to the Firebase project

## Setup Steps

### Step 1: Install Google Cloud CLI

#### Option A: Using the Installer (Recommended)

1. Download the installer:
   - Go to: https://cloud.google.com/sdk/docs/install
   - Click "Download for Windows (x86_64)"
   - Run the downloaded `GoogleCloudSDKInstaller.exe`

2. Follow the installation wizard:
   - Accept the default installation location
   - Check "Start Cloud SDK Shell" when prompted
   - Check "Run 'gcloud init'" when prompted

#### Option B: Using PowerShell Script

Run the provided installation script:

```powershell
.\install_gcloud.ps1
```

### Step 2: Initialize gcloud CLI

After installation, **restart PowerShell** and run:

```powershell
gcloud init
```

Follow the prompts:
1. Choose "Log in with a new account"
2. Your browser will open - sign in with your Google account
3. Select your project: `sanction-defender-firebase`
4. Choose a default compute region (e.g., `europe-west1`)

### Step 3: Set Up Application Default Credentials

Run this command to create local ADC credentials:

```powershell
gcloud auth application-default login
```

This will:
- Open your browser for authentication
- Store credentials at: `%APPDATA%\gcloud\application_default_credentials.json`
- Allow all Google Cloud client libraries to authenticate automatically

**Important Notes:**
- This file contains a refresh token - keep it secure
- The credentials are tied to your user account
- You may need additional quota project configuration for some APIs

### Step 4: Configure Default Project

Ensure your default project is set correctly:

```powershell
gcloud config set project sanction-defender-firebase
```

### Step 5: Verify Setup

Run the verification script:

```powershell
.\verify_adc_setup.ps1
```

This will check:
- ✓ gcloud CLI installation
- ✓ Current authentication status
- ✓ ADC credentials file existence
- ✓ Firebase Admin SDK connectivity

## Expected Credential Locations

After setup, your credentials will be stored at:

- **Windows:** `%APPDATA%\gcloud\application_default_credentials.json`
- **Full path:** `C:\Users\<YourUsername>\AppData\Roaming\gcloud\application_default_credentials.json`

## How ADC Works

When your code calls Google Cloud APIs, ADC searches for credentials in this order:

1. **GOOGLE_APPLICATION_CREDENTIALS** environment variable (if set)
2. **User credentials** from `gcloud auth application-default login`
3. **Service account** attached to the resource (in production)

For local development, we use option #2 (user credentials).

## Common Issues and Solutions

### Issue: "gcloud: command not found"

**Solution:** Restart PowerShell after installing gcloud CLI, or add gcloud to PATH:

```powershell
$env:Path += ";C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"
```

### Issue: "DefaultCredentialsError: Your default credentials were not found"

**Solution:** Run the ADC login command:

```powershell
gcloud auth application-default login
```

### Issue: "API not enabled" or "No quota project"

**Solution:** Some APIs require additional configuration. Add a quota project:

```powershell
gcloud auth application-default set-quota-project sanction-defender-firebase
```

### Issue: "Permission denied" errors

**Solution:** Ensure your Google account has the necessary IAM roles:
- Firebase Admin SDK Admin Service Agent
- Cloud Datastore User (for Firestore access)
- Cloud Functions Developer (for deployment)

Check roles at: https://console.cloud.google.com/iam-admin/iam

## Security Best Practices

1. **Never commit credentials to source control**
   - The ADC file is stored outside your project directory
   - Add `*.json` to `.gitignore` for any service account keys

2. **Revoke credentials when not needed:**
   ```powershell
   gcloud auth application-default revoke
   ```

3. **Use user credentials for development, service accounts for production**
   - Local: User credentials (what we just set up)
   - Cloud Functions: Automatic service account (no setup needed)

4. **Regularly rotate service account keys** (if using them)

## Verification Checklist

Before proceeding with development, verify:

- [ ] Google Cloud CLI installed (`gcloud --version` works)
- [ ] Logged in to gcloud (`gcloud auth list` shows your account)
- [ ] Default project set (`gcloud config get-value project` returns `sanction-defender-firebase`)
- [ ] ADC credentials exist (`Test-Path $env:APPDATA\gcloud\application_default_credentials.json` returns `True`)
- [ ] Firebase Admin SDK connects (run `verify_adc_setup.ps1`)

## Next Steps

Once ADC is set up:

1. **Local Development:**
   - Your Python scripts will automatically authenticate
   - No code changes needed
   - Run: `python check_database_counts.py`

2. **Firebase Deployment:**
   - Firebase CLI will use your gcloud credentials
   - Run: `firebase deploy --only functions`

3. **Testing:**
   - Test local scripts that access Firestore
   - Verify deployments work without credential errors

## Additional Resources

- [Official ADC Documentation](https://cloud.google.com/docs/authentication/application-default-credentials)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
- [Firebase Admin SDK Authentication](https://firebase.google.com/docs/admin/setup)
- [Troubleshooting ADC](https://cloud.google.com/docs/authentication/troubleshoot-adc)

## Quick Reference Commands

```powershell
# Check authentication status
gcloud auth list

# Check current configuration
gcloud config list

# Set default project
gcloud config set project sanction-defender-firebase

# Login for ADC
gcloud auth application-default login

# Revoke ADC credentials
gcloud auth application-default revoke

# View ADC credentials location
echo $env:APPDATA\gcloud\application_default_credentials.json

# Test Firestore connection
python check_database_counts.py
```

---

**Need Help?**
If you encounter any issues during setup, check the verification script output or refer to the troubleshooting section above.
