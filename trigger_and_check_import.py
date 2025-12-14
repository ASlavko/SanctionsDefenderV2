#!/usr/bin/env python3
"""
Trigger import and check if it creates import_sessions entry
"""

import requests
import time
import json
from datetime import datetime
from firebase_admin import firestore, credentials, initialize_app
import os

# Get the Cloud Function URL
CLOUD_FUNCTION_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/download_sanctions_lists"

print(f"[>] Triggering import at {datetime.now()}...")
print(f"[>] Cloud Function: {CLOUD_FUNCTION_URL}")

try:
        response = requests.post(CLOUD_FUNCTION_URL, json={}, timeout=600)
    print(f"\n[OK] HTTP Status: {response.status_code}")
    print(f"[OK] Response:")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    import_status = result.get('details', {}).get('import_status', 'unknown')
    print(f"\n[INFO] Import status: {import_status}")
    
except Exception as e:
    print(f"[ERROR] Failed to trigger: {e}")
    exit(1)

# Wait for function to complete
print(f"\n[>] Waiting 15 seconds for import session to be written...")
time.sleep(15)

# Check Firestore for new import_sessions
print(f"\n[>] Checking Firestore for new import_sessions...")

try:
    if not firebase_admin._apps:
        initialize_app()
    db = firestore.client()
    
    # List all documents in import_sessions
    docs = db.collection('import_sessions').stream()
    sessions = []
    for doc in docs:
        if doc.id != 'latest_import_session':
            data = doc.to_dict()
            sessions.append({
                'id': doc.id,
                'status': data.get('status'),
                'timestamp_end': data.get('timestamp_end'),
                'total_changes': data.get('total_changes', 0)
            })
    
    # Sort by timestamp
    sessions.sort(key=lambda x: x.get('timestamp_end', ''), reverse=True)
    
    print(f"\n[INFO] Found {len(sessions)} import sessions (excluding latest_import_session):")
    for session in sessions[:5]:  # Show top 5
        print(f"\n  {session['id']}")
        print(f"    Status: {session['status']}")
        print(f"    Timestamp: {session['timestamp_end']}")
        print(f"    Changes: {session['total_changes']}")
    
    # Check if there's a NEW session (one created in last 20 seconds)
    if sessions:
        latest_session = sessions[0]
        latest_timestamp = latest_session.get('timestamp_end', '')
        
        # Parse timestamp
        try:
            from datetime import datetime
            ts_obj = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00'))
            now = datetime.now(ts_obj.tzinfo)
            age_seconds = (now - ts_obj).total_seconds()
            
            if age_seconds < 25:
                print(f"\n[SUCCESS] ✓ New import_sessions entry found!")
                print(f"  Entry: {latest_session['id']}")
                print(f"  Age: {age_seconds:.1f} seconds")
                print(f"  Status: {latest_session['status']}")
                print(f"  Total changes: {latest_session['total_changes']}")
            else:
                print(f"\n[WARNING] Latest session is {age_seconds:.1f} seconds old (expected < 25)")
        except Exception as parse_err:
            print(f"\n[WARNING] Could not parse timestamp: {parse_err}")
    else:
        print(f"\n[ERROR] No import sessions found!")
        
except Exception as e:
    print(f"[ERROR] Failed to check Firestore: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"\n[OK] Check complete at {datetime.now()}")
