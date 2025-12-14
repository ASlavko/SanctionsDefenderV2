# Batch Screening API & Frontend

## Overview

The batch screening functionality allows users to upload Excel (.xlsx, .xls) or CSV files containing lists of company names or individual names for automated sanctions screening.

## Features

- **File Upload**: Support for Excel and CSV formats
- **Entity Type Selection**: Radio button to specify if the list contains company names (default) or individual names
- **Configurable Threshold**: Adjustable match threshold (50-100%, default 80%)
- **Fuzzy Matching**: Token-based matching with scoring
- **Results Summary**: Statistics showing total screened, clear, and potential matches
- **Export Functionality**: Download results as CSV

## API Endpoint

### POST /batch_screening

Screens multiple entities from an uploaded file against the sanctions database.

**Request:**

- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file`: Excel or CSV file (required)
  - `entity_type`: `"company"` or `"individual"` (default: `"company"`)
  - `threshold`: Match threshold percentage, 50-100 (default: `80`)

**File Format:**

- First column should contain entity names
- First row is automatically detected and skipped if it appears to be a header
- Duplicate names are automatically removed

**Response:**

```json
{
  "status": "success",
  "results": [
    {
      "name": "Example Company Ltd",
      "status": "CLEAR" | "POTENTIAL_MATCH",
      "match_count": 0,
      "matches": [
        {
          "id": "EU_123456",
          "source": "EU",
          "name": "Example Entity",
          "aliases": ["Example Co", "Example Corp"],
          "entity_type": "company",
          "country": "Russia",
          "programs": ["EU Sanctions"],
          "confidence": 85.5
        }
      ]
    }
  ],
  "summary": {
    "total_screened": 100,
    "clear": 95,
    "potential_matches": 5,
    "entity_type": "company",
    "threshold": 80
  },
  "query_time_ms": 1234.56
}
```

**Error Response:**

```json
{
  "status": "error",
  "error": "Error message",
  "query_time_ms": 123.45
}
```

## Frontend UI

### Location

- **URL**: `/batch_screening.html`
- Navigation tabs allow switching between single search and batch screening

### User Flow

1. Select entity type (company or individual) via radio buttons
2. Set match threshold (default 80%)
3. Upload Excel or CSV file via:
   - Click to browse
   - Drag and drop
4. Click "Screen Entities" to process
5. Review results showing clear and potential matches
6. Export results as CSV for further analysis

### UI Components

- **Entity Type Selector**: Radio buttons for company (default) or individual
- **File Upload Area**: Drag-and-drop zone with file selection
- **Threshold Slider**: Adjustable matching sensitivity
- **Results Summary**: Statistics cards showing screening overview
- **Results List**: Detailed view of each entity with match information
- **Export Button**: Download results as CSV

## Matching Algorithm

The fuzzy matching algorithm uses multiple scoring methods:

1. **Exact Match**: 100% confidence
2. **Substring Match**: Calculated based on word overlap percentage
3. **Alias Matching**: Up to 95% confidence for alias matches
4. **Token-Based Matching**: Word overlap scoring up to 80%

Only matches at or above the specified threshold are returned (max 5 per entity).

## Deployment

Deploy the batch screening API alongside the search API:

```powershell
# Deploy batch screening function
gcloud functions deploy batch_screening `
  --gen2 `
  --runtime=python311 `
  --region=europe-west1 `
  --source=./functions `
  --entry-point=batch_screening `
  --trigger-http `
  --allow-unauthenticated `
  --timeout=540s `
  --memory=2GB

# Deploy frontend
firebase deploy --only hosting
```

## Configuration

### requirements.txt

The following dependencies are required:

```
firebase_functions~=0.1.0
requests
firebase-admin>=7.0.0
google-cloud-firestore>=2.0.0
openpyxl>=3.0.0
flask>=3.0.0
flask-cors>=4.0.0
```

### Cloud Function Settings

- **Memory**: 2GB (to handle large files)
- **Timeout**: 540s (9 minutes for large batches)
- **Runtime**: Python 3.11

## Usage Examples

### CSV File Format

```csv
Company Name
Acme Corporation
Global Trading Ltd
Example Industries Inc
```

### Excel File Format

| Company Name           |
| ---------------------- |
| Acme Corporation       |
| Global Trading Ltd     |
| Example Industries Inc |

## Security Considerations

- File size limit: 10MB (client-side validation)
- Supported formats: .xlsx, .xls, .csv only
- CORS enabled for cross-origin requests
- Input validation for entity type and threshold

## Performance

- Processing time depends on file size and database size
- Typical performance: ~100-200 names per minute
- Results are streamed to provide real-time feedback
- Top 5 matches per entity to limit response size

## Future Enhancements

As outlined in the project plan:

1. Store screening results in Firestore (`screening_jobs` collection)
2. Implement decision workflow (confirm/clear/revoke)
3. Add audit trail logging
4. Support for stored decisions and auto-application
5. PDF report generation
6. Real-time progress dashboard
7. Multi-company support with role-based access
