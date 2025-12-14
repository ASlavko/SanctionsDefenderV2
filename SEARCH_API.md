# Sanctions Search API & Frontend

## Overview

Complete search interface for the 30,382 sanctions records across EU, UK, and OFAC lists.

## Features

✅ **Full-text search** by name, aliases, country  
✅ **Filtering** by source, entity type, program  
✅ **Confidence scoring** for match accuracy  
✅ **Beautiful responsive UI** for web and mobile  
✅ **Fast queries** (<500ms average)  
✅ **CORS enabled** for public access

## API Endpoint

**URL**: `https://YOUR_REGION-sanction-defender-firebase.cloudfunctions.net/search`

**Method**: `GET`

### Query Parameters

| Parameter | Type   | Description             | Example                                          |
| --------- | ------ | ----------------------- | ------------------------------------------------ |
| `q`       | string | Search query (name)     | `Putin`                                          |
| `country` | string | Filter by country       | `Russia`                                         |
| `program` | string | Filter by program       | `SDN`, `SDGT`, `EU`                              |
| `type`    | string | Entity type             | `individual` or `company`                        |
| `source`  | string | Sanctions source        | `EU`, `UK`, `US_SDN_SIMPLE`, `US_NON_SDN_SIMPLE` |
| `limit`   | number | Results limit (max 500) | `50`                                             |

### Query Examples

**Search by name:**

```
GET /search?q=Putin&limit=10
```

**Search by country:**

```
GET /search?country=Russia&type=individual&limit=50
```

**Search by program:**

```
GET /search?program=SDN&source=US_SDN_SIMPLE&limit=100
```

**Combined search:**

```
GET /search?q=Bank&country=Iran&program=SDGT&limit=50
```

### Response Format

```json
{
  "status": "success",
  "matches": [
    {
      "id": "EU_12345",
      "source": "EU",
      "name": "Vladimir Putin",
      "aliases": ["V. Putin", "Vladimir V. Putin"],
      "entity_type": "individual",
      "country": "Russian Federation",
      "gender": "Male",
      "dob": "1952-10-01",
      "programs": ["EU_RUSSIA"],
      "confidence": 95.5
    }
  ],
  "count": 1,
  "query_time_ms": 245.3,
  "query": {
    "search": "putin",
    "country": null,
    "program": null,
    "type": null,
    "source": null
  }
}
```

## Frontend

Access at: `https://sanction-defender-firebase.web.app/search.html`

### Features

- Real-time search with confidence scoring
- Color-coded match confidence (high/medium/low)
- Responsive design for desktop and mobile
- Export-ready format (copy/paste to spreadsheet)
- Multiple filter options
- Query performance display

## Deployment

### 1. Deploy Search API

```powershell
$gcPath = "C:\Users\Slavko\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

& $gcPath functions deploy search_sanctions `
  --region=europe-west1 `
  --runtime=python311 `
  --trigger-http `
  --source=functions `
  --entry-point=search_sanctions `
  --memory=512MB `
  --timeout=30s `
  --project=sanction-defender-firebase
```

### 2. Update search.html with API URL

Edit `public/search.html` and replace:

```javascript
const API_URL = "/search"; // Change to actual Cloud Function URL
```

With your deployed function URL:

```javascript
const API_URL =
  "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions";
```

### 3. Deploy Frontend

```powershell
firebase deploy --only hosting
```

## Performance

- **Search latency**: 100-500ms (depends on result set size)
- **Memory usage**: 512MB (enough for Firestore client)
- **Concurrent users**: Scales automatically with Cloud Functions
- **Cost**: Free tier covers ~2M API calls/month

## Search Scoring Algorithm

Confidence scores are calculated based on:

- **Name matching** (primary): 100% for exact match, 80% for substring, 60% for alias match, 40% for word match
- **Country matching**: +20% if country matches
- **Program matching**: +20% if program matches
- **Maximum**: 100%

Example:

- Exact name match + country + program = 100%
- Name substring match + program = 80% + 20% = 100%
- Partial name match + country = 40% + 20% = 60%

## API Error Responses

**Missing parameters** (400):

```json
{
  "error": "At least one search parameter required (q, country, program, source)",
  "status": "invalid_request"
}
```

**Server error** (500):

```json
{
  "status": "error",
  "error": "Database connection failed",
  "query_time_ms": 125.3
}
```

## Security & Privacy

- **Public API**: No authentication required (intentional for compliance screening)
- **Rate limiting**: None configured (add if needed)
- **Data protection**: Firestore security rules in place
- **CORS**: Enabled for all origins
- **No logging**: Search queries not logged

## Testing

### Local Testing

```bash
cd functions
pip install -r requirements.txt
python search_api.py
```

### cURL Examples

```bash
# Search by name
curl "http://localhost:8080/search_sanctions?q=putin"

# Filter by country
curl "http://localhost:8080/search_sanctions?country=russia&type=individual"

# Combined
curl "http://localhost:8080/search_sanctions?q=bank&country=iran&program=SDN&limit=100"
```

## Future Enhancements

- [ ] Add fuzzy matching for misspelled names
- [ ] Implement phonetic matching (Soundex, Metaphone)
- [ ] Add batch screening API (POST endpoint)
- [ ] Webhook integration for real-time updates
- [ ] Search result caching
- [ ] Advanced analytics dashboard
- [ ] Integration with third-party KYC providers

## Support

For issues or questions:

1. Check Cloud Function logs: `gcloud functions logs read search_sanctions --region=europe-west1`
2. Review Firestore quota: `gcloud firestore describe`
3. Test API directly: Use cURL or browser to verify endpoint
