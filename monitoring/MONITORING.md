# Sanctions Defender - Monitoring & Alerting Setup

## Overview

Configure error monitoring and email alerts for the daily sanctions list import function.

## Quick Start - Setup in 5 Minutes

### Step 1: Create Email Notification Channel

1. Go to https://console.cloud.google.com/monitoring/alerting/notificationchannels
2. Click "Create Channel"
3. Select "Email" as the type
4. Enter email: YOUR_EMAIL@example.com
5. Display name: "Sanctions Import Alerts"
6. Click "Create"
7. Check your email and click verify link

### Step 2: Create Alert Policy

1. Go to https://console.cloud.google.com/monitoring/alerting/policies
2. Click "Create Policy"
3. Click "Add Condition"
4. Select metric type: **Cloud Functions > Executions**
5. Set resource filter:
   - resource.labels.function_name = "download_sanctions_lists"
6. Set metric filter:
   - metric.labels.status = "error"
7. Condition: **Any monitored resource | Status equals "error"**
8. Time window: **1 minute**
9. Click "Add Condition"
10. Click "Add Notification Channels"
11. Select "Sanctions Import Alerts" channel
12. Name policy: "Sanctions List Import Failed"
13. Click "Create Policy"

**Done!** You'll now receive email alerts if the import fails.

## What Gets Monitored

- ✅ **Function Execution Errors**: When function returns error status
- ✅ **Import Failures**: When records fail to import to Firestore
- ✅ **Timeout Events**: When function exceeds 540s timeout
- ✅ **Memory Issues**: When memory usage is excessive
- ✅ **Data Loss**: When imported record count is abnormally low

## Useful Cloud Console Links

| Link                                                                                                        | Purpose                   |
| ----------------------------------------------------------------------------------------------------------- | ------------------------- |
| [Cloud Logs](https://console.cloud.google.com/logs)                                                         | View function logs        |
| [Cloud Functions](https://console.cloud.google.com/functions/details/europe-west1/download_sanctions_lists) | View function details     |
| [Alert Policies](https://console.cloud.google.com/monitoring/alerting/policies)                             | Manage alerts             |
| [Notification Channels](https://console.cloud.google.com/monitoring/alerting/notificationchannels)          | Manage alert destinations |
| [Dashboards](https://console.cloud.google.com/dashboards)                                                   | Create custom dashboards  |

## Log Queries

### View Recent Imports

```
resource.type="cloud_function"
resource.labels.function_name="download_sanctions_lists"
```

### View Import Progress (Last 24h)

```
resource.type="cloud_function"
resource.labels.function_name="download_sanctions_lists"
textPayload =~ "Imported.*records"
```

### View Errors Only

```
resource.type="cloud_function"
resource.labels.function_name="download_sanctions_lists"
severity=ERROR
```

## Testing Your Alert

To verify alerts work:

1. In Cloud Console, open the alert policy
2. Click the three-dot menu
3. Select "Test notification"
4. Check your email (should arrive within 1-2 minutes)

## Interpreting Alerts

### Alert: "Sanctions List Import Failed"

- **Severity**: High
- **Possible Causes**:
  - Data source unavailable (EU, UK, or OFAC servers down)
  - Firestore quota exceeded
  - Network connectivity issues
  - Function timeout (> 540 seconds)
- **How to Fix**:
  1. Open [Cloud Function logs](https://console.cloud.google.com/functions/details/europe-west1/download_sanctions_lists)
  2. Look for error messages in recent logs
  3. Check if data source URLs are accessible
  4. Verify Firestore quota not exceeded
  5. Check function timeout/memory settings

## Creating a Monitoring Dashboard (Optional)

Create a custom dashboard to visualize function health:

1. Go to https://console.cloud.google.com/dashboards
2. Click "Create Dashboard"
3. Name it: "Sanctions Defender"
4. Add Widget > Line chart
5. Select metric: **Cloud Functions > Executions**
6. Filter: `resource.labels.function_name = "download_sanctions_lists"`
7. Add another widget for errors: Add filter `metric.labels.status = "error"`
8. Add Text widget with:
   - Title: "View Logs"
   - Link: https://console.cloud.google.com/logs

## Advanced: Slack Integration (Optional)

To send alerts to Slack instead of (or in addition to) email:

1. Create Slack Webhook:
   - Go to https://api.slack.com/messaging/webhooks
   - Click "Create New App"
   - Choose "From an app manifest"
   - Paste webhook configuration
2. In Cloud Console:
   - Create new notification channel
   - Type: Slack
   - Paste webhook URL
   - Add to alert policy

## Log Levels in Cloud Function

The import function uses these log levels:

- **INFO**: Normal operation progress ("Imported X records")
- **WARNING**: Recoverable issues (skipped records, partial imports)
- **ERROR**: Critical failures (connection errors, Firestore errors)

## Firestore Quota Monitoring

If you see "quota exceeded" errors:

1. Check Firestore quota usage: https://console.cloud.google.com/firestore/quotas
2. Monitor database size in Firestore settings
3. Consider archiving old records or enabling auto-delete

## Common Issues

| Error                 | Cause                        | Solution                                               |
| --------------------- | ---------------------------- | ------------------------------------------------------ |
| "Connection timeout"  | Network or data source issue | Check data source URL, verify internet connectivity    |
| "Quota exceeded"      | Too many Firestore writes    | Check if test mode is limiting writes, upgrade billing |
| "Function timeout"    | Large files taking > 540s    | Monitor file sizes, consider increasing timeout        |
| "No records imported" | Parsing error                | Check XML source format, review parser logs            |

## Next Steps

- [x] Read this documentation
- [ ] Create email notification channel
- [ ] Create alert policy for function errors
- [ ] Test alert with "Test notification" button
- [ ] (Optional) Create monitoring dashboard
- [ ] (Optional) Setup Slack integration

## Support

For help with monitoring:

- Cloud Monitoring Docs: https://cloud.google.com/monitoring/docs
- Cloud Logging Docs: https://cloud.google.com/logging/docs
- Alert Policies: https://cloud.google.com/monitoring/alerts

---

**Project**: sanction-defender-firebase  
**Function**: europe-west1/download_sanctions_lists  
**Schedule**: Daily at 04:00 UTC  
**Created**: December 10, 2025
