#!/usr/bin/env python3
"""
Fetch Cloud Function execution logs using Firestore audit trail.
Since gcloud CLI is not available, check function logs via Cloud Logging API.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime, timedelta

try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    db = firestore.client()
    print("[>] Connected to Firestore\n")

    # Check audit_logs for recent imports
    print("=" * 80)
    print("RECENT IMPORT AUDIT LOGS (last 5)")
    print("=" * 80 + "\n")

    audit_coll = db.collection('audit_logs')
    docs = audit_coll.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()

    for doc in docs:
        data = doc.to_dict()
        print(f"ID: {doc.id}")
        print(f"  Status: {data.get('status')}")
        print(f"  Timestamp: {data.get('timestamp')}")
        print(f"  Message: {data.get('message')}")
        print(f"  Error: {data.get('error')}")
        print()

    # Try to get 'latest_import_session' if it exists
    print("\n" + "=" * 80)
    print("LATEST IMPORT SESSION (if exists)")
    print("=" * 80 + "\n")

    try:
        latest = db.collection('import_sessions').document('latest_import_session').get()
        if latest.exists:
            data = latest.to_dict()
            print(f"Status: {data.get('status')}")
            print(f"Timestamp Start: {data.get('timestamp_start')}")
            print(f"Timestamp End: {data.get('timestamp_end')}")
            print(f"Total Changes: {data.get('total_changes')}")
            print(json.dumps(data.get('statistics'), indent=2))
        else:
            print("[!] latest_import_session not found")
    except Exception as e:
        print(f"[!] Error fetching latest_import_session: {e}")

except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()
