# Google Cloud Credentials Setup

## Current Configuration

**Project ID:** `sanction-defender-firebase`
**User Email:** `azman.slavko@gmail.com`
**Credentials Type:** Application Default Credentials (ADC) - User Credentials

## Credentials Location

```
Windows User Profile:
  C:\Users\Slavko\AppData\Roaming\gcloud\legacy_credentials\azman.slavko@gmail.com\adc.json

Credentials Type:
  authorized_user (OAuth2 user credentials, not a service account)
```

## How It Works

1. **gcloud CLI** stores user credentials locally when you run:

   ```powershell
   gcloud auth application-default login
   ```

2. **Python firebase-admin SDK** can use these cached credentials automatically via:

   - `credentials.ApplicationDefault()` method
   - Or by setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable

3. **Our setup** uses the environment variable approach for reliability:
   ```powershell
   $env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Slavko\AppData\Roaming\gcloud\legacy_credentials\azman.slavko@gmail.com\adc.json"
   ```

## Running the Import Script

Use the wrapper script to ensure credentials are set:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\Slavko\SanctionDefenderApp\run_import.ps1"
```

The wrapper script automatically:

1. Sets the `GOOGLE_APPLICATION_CREDENTIALS` environment variable
2. Sets UTF-8 encoding for Python output
3. Runs the two-stage import with proper error handling

## Important Notes

- ⚠️ **DO NOT share the ADC file** - it contains valid OAuth2 tokens
- The credentials have **User permissions**, not Service Account permissions
- If you need higher-level permissions, request a Service Account key from GCP
- The refresh_token in the ADC file is valid and allows automatic token refresh

## If Credentials Stop Working

1. Check if the refresh token expired (unlikely for offline use)
2. Re-authenticate with:
   ```powershell
   gcloud auth application-default login
   ```
3. This will create a fresh `adc.json` file in the same location

## Service Account vs User Credentials

| Aspect         | User Credentials (Current)             | Service Account                |
| -------------- | -------------------------------------- | ------------------------------ |
| Type           | `authorized_user`                      | `service_account`              |
| Location       | `~/.config/gcloud/legacy_credentials/` | Downloaded from GCP            |
| Used For       | Local development, testing             | Production, automated services |
| Refresh Token  | Yes (manual refresh possible)          | No (uses key file)             |
| Current Status | ✓ Working and configured               | Not set up                     |

## Files Involved

- `import_sanctions_two_stage.py` - Two-stage import with validation & audit logs
- `run_import.ps1` - Wrapper script that sets credentials
- `test_credentials.py` - Quick credential test script
- `.firebaserc` - Firebase project configuration
