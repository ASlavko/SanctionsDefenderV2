# Sanctions Defender - Monitoring Quick Reference

## Alert Setup Summary

**Status**: Ready for configuration  
**Project**: sanction-defender-firebase  
**Function**: europe-west1/download_sanctions_lists

## What You'll Get

✅ **Email alerts** when the daily import fails  
✅ **Error details** linked directly to function logs  
✅ **Automatic notifications** within 1-2 minutes

## Setup Checklist

- [ ] Go to [Notification Channels](https://console.cloud.google.com/monitoring/alerting/notificationchannels)
- [ ] Click "Create Channel"
- [ ] Type: Email
- [ ] Email: your-email@example.com
- [ ] Display name: "Sanctions Import Alerts"
- [ ] Click "Create"
- [ ] Verify email address

- [ ] Go to [Alert Policies](https://console.cloud.google.com/monitoring/alerting/policies)
- [ ] Click "Create Policy"
- [ ] Add Condition
- [ ] Metric: Cloud Functions > Executions
- [ ] Filter: resource.labels.function_name = "download_sanctions_lists"
- [ ] Condition: status = "error"
- [ ] Add notification channel: "Sanctions Import Alerts"
- [ ] Name: "Sanctions List Import Failed"
- [ ] Click "Create Policy"

- [ ] Test notification: Open policy, click 3-dot menu, "Test notification"
- [ ] Check email received

## Where to Monitor

| Location                                                                                                                                                              | Purpose                     |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| [Cloud Logs](https://console.cloud.google.com/logs?query=resource.type%3D%22cloud_function%22%20AND%20resource.labels.function_name%3D%22download_sanctions_lists%22) | View detailed function logs |
| [Cloud Function](https://console.cloud.google.com/functions/details/europe-west1/download_sanctions_lists)                                                            | View function status        |
| [Firestore](https://console.cloud.google.com/firestore/data/sanctions_entities)                                                                                       | View imported records       |
| [Cloud Scheduler](https://console.cloud.google.com/cloudscheduler)                                                                                                    | View scheduled runs         |

## Common Alerts

**"Sanctions List Import Failed"** = Function returned error  
→ Check: Data source accessibility, Firestore quota, network

**"Function Timeout"** = Import took > 540 seconds  
→ Check: File sizes, network speed, parser performance

**No alert but low record count** = Partial import  
→ Check: Log messages, Firestore write limits

## Log Search Examples

Find yesterday's import:

```
resource.type="cloud_function"
resource.labels.function_name="download_sanctions_lists"
timestamp>="2025-12-09T04:00:00Z"
```

Find all errors:

```
resource.type="cloud_function"
resource.labels.function_name="download_sanctions_lists"
severity=ERROR
```

Find progress updates:

```
resource.type="cloud_function"
resource.labels.function_name="download_sanctions_lists"
textPayload =~ "Imported.*records"
```

## First Test

After creating the alert policy:

1. Open the policy in Cloud Console
2. Click three-dot menu → "Test notification"
3. Check your email (1-2 minutes)
4. Confirm you received it

That's it! The system is now monitored.

---

**Time to setup**: ~5 minutes  
**Cost**: Free (included in GCP free tier)  
**Ongoing**: No action needed, automatic daily checks
