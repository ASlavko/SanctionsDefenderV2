#!/usr/bin/env python3
"""
Check import_sessions collection and list recent imports
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

try:
    # Initialize Firebase
    if not firebase_admin._apps:
        cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if cred_path and os.path.exists(cred_path):
            firebase_admin.initialize_app(credentials.Certificate(cred_path))
        else:
            firebase_admin.initialize_app()

    db = firestore.client()
    print(f"[OK] Connected to Firestore\n")

    # Query import_sessions collection
    print("=" * 80)
    print("IMPORT_SESSIONS COLLECTION")
    print("=" * 80)

    coll = db.collection('import_sessions')
    
    # Get all documents, limited to 20
    docs = coll.limit(20).stream()
    sessions = []
    
    for doc in docs:
        data = doc.to_dict()
        sessions.append({
            'id': doc.id,
            'status': data.get('status', 'unknown'),
            'timestamp_start': data.get('timestamp_start', 'N/A'),
            'timestamp_end': data.get('timestamp_end', 'N/A'),
            'total_changes': data.get('total_changes', 0),
            'import_session_id': data.get('import_session_id', 'N/A')
        })
    
    # Sort by timestamp_end descending
    sessions.sort(key=lambda x: x['timestamp_end'], reverse=True)
    
    print(f"\nFound {len(sessions)} import sessions:\n")
    
    for i, session in enumerate(sessions, 1):
        print(f"{i}. {session['id']}")
        print(f"   Status: {session['status']}")
        print(f"   Started: {session['timestamp_start']}")
        print(f"   Ended:   {session['timestamp_end']}")
        print(f"   Changes: {session['total_changes']}")
        print()
    
    # Check if we have recent imports (last 5 minutes)
    if sessions:
        latest = sessions[0]
        try:
            if 'Z' in latest['timestamp_end']:
                ts_str = latest['timestamp_end'].replace('Z', '+00:00')
            else:
                ts_str = latest['timestamp_end']
            
            from datetime import datetime, timezone
            ts_obj = datetime.fromisoformat(ts_str)
            now_utc = datetime.now(timezone.utc)
            age_seconds = (now_utc - ts_obj).total_seconds()
            
            print("=" * 80)
            print("ANALYSIS")
            print("=" * 80)
            print(f"\nLatest import: {latest['id']}")
            print(f"Age: {age_seconds:.1f} seconds")
            
            if age_seconds < 120:  # 2 minutes
                print(f"[SUCCESS] ✓ VERY RECENT IMPORT DETECTED!")
                print(f"  This appears to be from the recent function trigger.")
            elif age_seconds < 300:  # 5 minutes
                print(f"[INFO] Recent import found (within 5 minutes)")
            else:
                print(f"[INFO] Latest import is {age_seconds/60:.1f} minutes old")
        
        except Exception as parse_err:
            print(f"\n[WARNING] Could not parse timestamp: {parse_err}")
    else:
        print("\n[WARNING] No import sessions found!")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
