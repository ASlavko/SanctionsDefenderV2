# Daily Download & Import Workflow - UPDATED

## Overview

The daily sanctions list download and import process now uses **two-stage validation** to ensure data integrity and prevent data corruption.

## Workflow Sequence

### 1. **Cloud Scheduler Trigger** (04:00 UTC daily)

- Triggers `download_sanctions_lists` Cloud Function via HTTP

### 2. **Download Phase** (`download_sanctions_lists` function)

- Downloads XML files from official sources:
  - EU: OFAC consolidated list
  - UK: UK sanctions list
  - US_SDN_SIMPLE: US SDN consolidated list
  - US_NON_SDN_SIMPLE: US non-SDN consolidated list
- Saves XML files to `/tmp/sanctions/` (Cloud Run) or `data/sanctions/` (local)
- Parses XML into JSONL format using language-specific parsers
- Saves parsed JSONL to `/tmp/parsed/` (Cloud Run) or `data/parsed/` (local)
- **Status**: Parsed and ready for import

### 3. **Two-Stage Import Phase** (NEW - automatically triggered)

#### Stage 1: Validation (Read-only)

- Loads all new parsed JSONL data
- Validates data integrity:
  - Required fields (id, sanction_source, main_name, entity_type)
  - Duplicate detection
  - Source consistency
- Fetches all existing data from Firestore by source
- Compares using content hashing:
  - **Added**: New entities not in Firestore
  - **Updated**: Changed entities (detected by hash)
  - **Unchanged**: Identical records
  - **Removed**: Entities no longer in source files
- Generates detailed change report with progress logging

#### Stage 2: Commit (Auto-executed)

- Executes all changes (zero manual confirmation needed)
- Uses `merge=False` to prevent data corruption
- Creates comprehensive audit log entries:
  - Timestamp
  - Change type (ADD/UPDATE/REMOVE)
  - Entity ID and source
  - Old and new data (full history)
  - Reason for change
- Batches audit records by import ID for easy tracking

## Key Improvements

✅ **No More Data Corruption**

- Changed from `merge=True` (was combining records) to `merge=False` (replaces)
- Each import starts with full validation

✅ **Complete Audit Trail**

- Every change logged with before/after values
- Batch IDs for tracking across imports
- Timestamps for compliance

✅ **Progress Visibility**

- Download logs: Every source download attempt
- Parsing logs: Record counts per source
- Validation logs: Progress every 1,000 records during comparison
- Commit logs: Progress every 1,000 records during changes

✅ **Removed Entity Handling**

- Detects when entities are removed from source lists
- Warns about removals (data quality check)
- Logs all removals for audit

## Configuration

### Schedule

- **Trigger**: Cloud Scheduler: `sanctions-daily-job`
- **Schedule**: `0 4 * * *` (04:00 UTC daily)
- **Function**: `download_sanctions_lists`

### Cloud Function Details

- **Location**: `europe-west1`
- **Runtime**: Python 3.11
- **Timeout**: 600 seconds (10 minutes - sufficient for all operations)
- **Memory**: 512 MB

## Code Files

| File                            | Purpose                          | Location                       |
| ------------------------------- | -------------------------------- | ------------------------------ |
| `main.py`                       | Download & trigger import        | `functions/main.py`            |
| `import_sanctions_two_stage.py` | Two-stage validation & import    | `functions/` + root            |
| `matching.py`                   | Phonetic matching for comparison | `functions/matching.py`        |
| `parse_eu.py`                   | EU XML parser                    | `functions/parse_eu.py`        |
| `parse_uk.py`                   | UK XML parser                    | `functions/parse_uk.py`        |
| `parse_us_simple.py`            | US XML parser                    | `functions/parse_us_simple.py` |

## Monitoring

### View Download Logs

```powershell
gcloud functions logs read download_sanctions_lists `
  --limit 50 `
  --project sanction-defender-firebase
```

### View Scheduler Runs

```powershell
gcloud scheduler jobs describe sanctions-daily-job `
  --location europe-west1 `
  --project sanction-defender-firebase
```

### Check Audit Trail

```
Firestore > audit_logs > [import_YYYYMMDD_HHMMSS]
```

## Manual Trigger (for testing)

```powershell
$url = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/download_sanctions_lists"
$response = Invoke-WebRequest -Uri $url -Method POST
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

## Error Handling

If validation detects issues:

1. Import aborts before commit phase
2. Detailed error logs written to Cloud Functions logs
3. Audit log created but with 0 committed changes
4. No data corruption possible (read-only validation)

If commit fails on individual records:

- Continues processing remaining records
- Logs all failures with line numbers
- Audit trail captures partial commits
- Manual review of audit logs recommended

## Future Enhancements

- [ ] Email notifications on import completion
- [ ] Metrics dashboard for import history
- [ ] Automatic retry on timeout
- [ ] Incremental import (only changed records)
- [ ] Slack alerts for validation failures
