#!/usr/bin/env python3
"""
Check all collections in the live Firebase Firestore database.
Lists collection names and sample document counts.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

try:
    # Initialize Firebase with default credentials (gcloud CLI or GOOGLE_APPLICATION_CREDENTIALS)
    if not firebase_admin._apps:
        cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if cred_path and os.path.exists(cred_path):
            print(f"[>] Using credentials from: {cred_path}")
            firebase_admin.initialize_app(credentials.Certificate(cred_path))
        else:
            print("[>] Using Application Default Credentials (gcloud)")
            firebase_admin.initialize_app()

    db = firestore.client()
    print(f"[OK] Connected to Firestore\n")

    # Get all collections
    print("=" * 80)
    print("FIRESTORE COLLECTIONS")
    print("=" * 80)

    collections = db.collections()
    collection_list = list(collections)

    if not collection_list:
        print("[!] No collections found in Firestore")
    else:
        print(f"\nTotal collections: {len(collection_list)}\n")

        for i, coll in enumerate(collection_list, 1):
            coll_name = coll.id
            print(f"{i}. {coll_name}")

            # Count documents (limit to 100 for speed)
            docs = coll.limit(100).stream()
            doc_count = 0
            sample_ids = []

            for doc in docs:
                doc_count += 1
                if len(sample_ids) < 5:
                    sample_ids.append(doc.id)

            print(f"   Documents: {doc_count}+")
            if sample_ids:
                print(f"   Sample IDs: {', '.join(sample_ids[:3])}")

            # Check for special collections
            if coll_name == 'import_sessions':
                print(f"   [*] IMPORTANT: Found 'import_sessions' collection!")
                # List all import session docs
                sessions = coll.stream()
                for session in sessions:
                    session_data = session.to_dict()
                    status = session_data.get('status', 'unknown')
                    timestamp = session_data.get('timestamp_start', 'N/A')
                    print(f"       - {session.id}: status={status}, timestamp={timestamp}")

            if coll_name == 'latest_import_session':
                print(f"   [*] IMPORTANT: Found 'latest_import_session' document!")
                doc_data = coll.document('latest_import_session').get()
                if doc_data.exists:
                    data = doc_data.to_dict()
                    print(f"       Status: {data.get('status')}")
                    print(f"       Timestamp: {data.get('timestamp_start')}")

            if coll_name == 'audit_logs':
                print(f"   [*] Found 'audit_logs' collection")

            if coll_name == 'sanctions_entities':
                print(f"   [*] Found 'sanctions_entities' collection")

            print()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal collections found: {len(collection_list)}")
    print("\nExpected collections for import logging:")
    print("  - import_sessions        (timestamped import batch records)")
    print("  - latest_import_session  (latest import snapshot)")
    print("  - sanctions_entities     (the main data collection)")
    print("  - audit_logs             (fallback audit trail)")

except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()
