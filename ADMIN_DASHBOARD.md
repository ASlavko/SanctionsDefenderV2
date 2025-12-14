# Admin Dashboard Documentation

## Overview
The Sanction Defender Admin Dashboard provides comprehensive monitoring and management capabilities for the sanctions database system.

## Access
- **URL**: https://sanction-defender-firebase.web.app/admin.html
- **Local Development**: http://localhost:5000/admin.html (when Firebase emulator is running)

## Features

### 1. System Health Monitoring
- **Overall Health Status**: Real-time system health indicator (Healthy/Warning/Error)
- **Total Records**: Current count of active sanctions entities across all sources
- **Last Update**: Timestamp of the most recent data import
- **Next Scheduled Update**: Countdown to next automatic import (4 AM UTC daily)

### 2. Data Sources Overview
Interactive table displaying statistics for each sanctions list:
- 🇪🇺 **European Union** (EC Financial Sanctions)
- 🇬🇧 **United Kingdom** (FCDO Sanctions List)
- 🇺🇸 **US SDN** (OFAC SDN List)
- 🇺🇸 **US Consolidated** (OFAC Consolidated List)

**Per-Source Metrics**:
- Health status indicator
- Current record count
- Records added (since last import)
- Records updated (since last import)
- Records deleted (since last import)
- Last update timestamp

### 3. Import History
Displays the last 10 import sessions with detailed statistics:
- Import timestamp
- Duration (seconds)
- Records downloaded
- Records added
- Records updated
- Records deleted
- Total records after update
- Session status

### 4. Administrative Controls
- **Refresh Button**: Manually refresh dashboard data
- **Run Update Now**: Trigger immediate sanctions list update (bypasses scheduled run)
- **Auto-Refresh**: Dashboard automatically refreshes every 30 seconds

### 5. Key Performance Indicators (KPIs)

#### Current KPIs:
- Total database size (30,376+ records)
- Per-source record counts
- Change tracking (add/update/delete counts)
- Import duration metrics
- System health status

#### Future KPIs (Suggested):
- Average import duration trend
- Success rate percentage
- Data freshness indicator (time since last update)
- Growth rate (records added over time)
- Source reliability metrics
- Change frequency by source
- Alert indicators for stale data or failed imports
- Download performance metrics (MB/s, file sizes)

## Technical Architecture

### Backend API Endpoint
**Function**: `admin_dashboard_api`
- **Region**: europe-west1
- **Runtime**: Python 3.11
- **Memory**: 512MB
- **Timeout**: 540s
- **URL**: https://europe-west1-sanction-defender-firebase.cloudfunctions.net/admin_dashboard_api

**API Response Structure**:
```json
{
  "timestamp": "2025-12-12T14:00:00.000000",
  "system_health": "healthy",
  "total_records": 30376,
  "sources": {
    "EU": {
      "current_count": 5820,
      "health": "healthy"
    },
    "UK": {...},
    "US_SDN_SIMPLE": {...},
    "US_NON_SDN_SIMPLE": {...}
  },
  "latest_import": {
    "import_session_id": "import_20251212_133518",
    "timestamp_end": "2025-12-12T13:35:45.123456",
    "duration_seconds": 287,
    "status": "completed",
    "statistics": {
      "total": {
        "downloaded": 30376,
        "added": 0,
        "updated": 0,
        "deleted": 0,
        "unchanged": 6263,
        "before_update": 30376,
        "after_update": 30376
      },
      "by_source": {
        "EU": {...},
        "UK": {...},
        "US_SDN_SIMPLE": {...},
        "US_NON_SDN_SIMPLE": {...}
      }
    }
  },
  "import_history": [...],
  "next_scheduled_run": "2025-12-13T04:00:00",
  "scheduler": {
    "schedule": "0 4 * * *",
    "timezone": "UTC",
    "description": "Daily at 4 AM UTC"
  }
}
```

### Frontend
**File**: `public/admin.html`
- **Framework**: Vanilla JavaScript (no dependencies)
- **Styling**: Embedded CSS with gradient design
- **Features**:
  - Responsive design (mobile-friendly)
  - Real-time data visualization
  - Auto-refresh capability
  - Interactive controls
  - Error handling with user feedback
  - CORS-enabled API calls

### Data Flow
1. **Frontend Request**: Dashboard loads and calls admin_dashboard_api endpoint
2. **Backend Processing**:
   - Initializes Firestore client
   - Queries sanctions_entities collection for current counts per source
   - Retrieves latest import_sessions document
   - Fetches last 10 import sessions for history
   - Calculates next scheduled run
   - Compiles response with all statistics
3. **Frontend Rendering**:
   - Parses JSON response
   - Renders statistics cards
   - Populates data sources table
   - Displays import history timeline
   - Updates last refresh timestamp

## Database Collections

### `sanctions_entities`
Stores individual sanction records with:
- `sanction_id`: Unique identifier
- `sanction_source`: Source identifier (EU/UK/US_SDN_SIMPLE/US_NON_SDN_SIMPLE)
- `name`: Entity name
- `entity_type`: Type (Individual/Entity)
- Additional fields: aliases, dates, programs, etc.

### `import_sessions`
Audit trail of import operations with:
- `import_session_id`: Unique session identifier
- `timestamp_start`: Import start time
- `timestamp_end`: Import completion time
- `duration_seconds`: Total duration
- `status`: completed/failed
- `statistics`: Aggregated statistics object
  - `total`: Overall statistics (downloaded, added, updated, deleted, etc.)
  - `by_source`: Per-source breakdown
- `changes`: Array of change records (optimized for ADD/UPDATE, full for DELETE)

**Storage Optimization**:
- ADD/UPDATE changes: Store only ID and name (~560KB per session)
- DELETE changes: Store full record data for audit trail
- Aggregated statistics at document root for fast queries

## Scheduled Operations

### Cloud Scheduler Job
- **Name**: download-sanctions-daily
- **Schedule**: `0 4 * * *` (Daily at 4 AM UTC)
- **Region**: europe-west1
- **Target**: download_sanctions_lists HTTP function
- **Retry Configuration**: Automatic retries on failure

### Manual Trigger
Users can bypass scheduled runs using the "Run Update Now" button, which:
1. Sends POST request to download_sanctions_lists function
2. Triggers immediate sanctions list download and processing
3. Updates database and creates new import session
4. Automatically refreshes dashboard upon completion

## Performance Considerations

### API Response Time
- **Typical**: 2-5 seconds
- **Factors**: Number of records, Firestore query performance, network latency

### Optimization Strategies
1. **Aggregated Statistics**: Pre-calculated totals in import_sessions documents
2. **Indexed Queries**: Firestore indexes on timestamp_end for fast sorting
3. **Limited History**: Only fetch last 10 sessions to reduce payload
4. **Minimal Change Data**: Store only essential fields for ADD/UPDATE operations
5. **Client-Side Caching**: Auto-refresh reduces redundant requests

### Scalability
- **Current Load**: 30,000+ records
- **Query Efficiency**: O(n) for record counts, O(log n) for session queries
- **Memory Usage**: ~512MB function memory handles large datasets
- **Concurrent Users**: Unlimited (stateless API, auto-scaling)

## Security

### CORS Configuration
- **Allowed Origins**: `*` (all origins)
- **Allowed Methods**: GET, POST, OPTIONS
- **Allowed Headers**: Content-Type
- **Max Age**: 3600 seconds

### Authentication
- **Current**: None (public dashboard)
- **Recommended**: Firebase Authentication for production
- **Future Enhancement**: Role-based access control (RBAC)

### Data Protection
- **Firestore Rules**: Configure read permissions in firestore.rules
- **Function Auth**: Can add `--no-allow-unauthenticated` flag for private access
- **API Keys**: Consider API key requirement for production

## Monitoring and Alerting

### Current Monitoring
- Real-time dashboard updates every 30 seconds
- Manual health checks via dashboard UI
- Import session audit trail in Firestore

### Recommended Additions
1. **Cloud Monitoring**: Set up alerts for function failures
2. **Error Logging**: Integrate with Google Cloud Logging
3. **Performance Metrics**: Track API response times
4. **Uptime Monitoring**: External service to ping dashboard
5. **Email Alerts**: Notify admins of failed imports or stale data

## Troubleshooting

### Dashboard Not Loading
1. Check browser console for JavaScript errors
2. Verify API endpoint URL is correct
3. Test API endpoint directly: `curl https://europe-west1-sanction-defender-firebase.cloudfunctions.net/admin_dashboard_api`
4. Check CORS configuration if cross-origin issues

### API Returns Empty Data
1. Verify Firestore collections exist and contain data
2. Check Firebase Admin SDK initialization
3. Review Firestore security rules for read permissions
4. Inspect Cloud Function logs in Google Cloud Console

### Import History Not Showing
1. Confirm import_sessions collection has documents
2. Check timestamp_end field exists and is properly formatted
3. Verify Firestore query ordering is correct
4. Look for query errors in function logs

### Manual Update Not Working
1. Ensure download_sanctions_lists function is deployed
2. Check function has proper permissions to write to Firestore
3. Verify HTTP trigger is publicly accessible
4. Review function execution logs for errors

## Development and Testing

### Local Development
```powershell
# Start Firebase emulator
firebase emulators:start

# Access local dashboard
http://localhost:5000/admin.html

# Local API endpoint
http://127.0.0.1:5001/sanction-defender-firebase/europe-west1/admin_dashboard_api
```

### Testing API Endpoint
```powershell
# Test production API
Invoke-WebRequest -Uri "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/admin_dashboard_api" | Select-Object -ExpandProperty Content | ConvertFrom-Json

# Test local API
Invoke-WebRequest -Uri "http://127.0.0.1:5001/sanction-defender-firebase/europe-west1/admin_dashboard_api" | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### Deployment
```powershell
# Deploy only admin API function
gcloud functions deploy admin_dashboard_api --gen2 --runtime=python311 --region=europe-west1 --source=functions --entry-point=admin_dashboard_api --trigger-http --allow-unauthenticated --memory=512MB --timeout=540s

# Deploy only hosting (dashboard frontend)
firebase deploy --only hosting

# Deploy everything
firebase deploy
```

## Future Enhancements

### Dashboard Features
1. **Charts and Graphs**: Visualize trends over time (import duration, record growth)
2. **Filtering and Search**: Filter import history by date range or source
3. **Export Functionality**: Download import history as CSV/Excel
4. **Real-time Updates**: WebSocket connection for live updates
5. **Detailed Drill-Down**: Click on source to see individual record changes
6. **Performance Dashboards**: API response times, query performance metrics
7. **User Management**: Admin user authentication and role-based access

### Backend Enhancements
1. **Caching Layer**: Redis cache for frequent queries
2. **Pagination**: Paginate import history for better performance
3. **Advanced Metrics**: Calculate success rates, data quality scores
4. **Alerting System**: Automatic notifications for anomalies
5. **Backup Management**: Display backup status and restore options
6. **Audit Trail**: Track admin actions (manual updates, configuration changes)

### Operational Improvements
1. **Health Checks**: Automated endpoint health monitoring
2. **SLA Tracking**: Monitor uptime and performance SLAs
3. **Cost Analysis**: Track and display Firebase/GCP costs
4. **Capacity Planning**: Predict storage needs and function usage
5. **Disaster Recovery**: Backup and restore procedures documentation

## Maintenance

### Regular Tasks
- Monitor import session logs for failures
- Review dashboard performance metrics
- Update frontend design as needed
- Optimize Firestore queries if response times increase
- Archive old import sessions (older than 90 days)

### Version History
- **v1.0** (Dec 2025): Initial admin dashboard release
  - Real-time monitoring
  - Import history tracking
  - Manual update trigger
  - Responsive design

## Support
For issues or questions:
1. Check Cloud Function logs in Google Cloud Console
2. Review Firestore data for consistency
3. Test API endpoint directly with curl/Invoke-WebRequest
4. Consult Firebase documentation for configuration changes

## Related Documentation
- [DEPLOY_SCHEDULER.md](DEPLOY_SCHEDULER.md) - Cloud Scheduler setup
- [IMPORT_SUMMARY_2025_12_11.md](IMPORT_SUMMARY_2025_12_11.md) - Import session logging design
- [STATUS.md](STATUS.md) - Project status and deployment info
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development environment setup
