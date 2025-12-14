#!/usr/bin/env python3
"""
Manually create import_sessions collection and latest_import_session document
to prove the Firestore writes are possible and the collection structure works.
"""

import firebase_admin
from firebase_admin import firestore
from datetime import datetime
import os

os.environ['GOOGLE_CLOUD_PROJECT'] = 'sanction-defender-firebase'

firebase_admin.initialize_app()
db = firestore.client()

import_batch_id = f"manual_import_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

print(f"[>] Writing to import_sessions/{import_batch_id}...")

session_data = {
    'import_session_id': import_batch_id,
    'timestamp_start': datetime.utcnow().isoformat(),
    'timestamp_end': datetime.utcnow().isoformat(),
    'duration_seconds': 0,
    'status': 'manually_created_for_testing',
    'error': None,
    'statistics': {
        'total': {'added': 5, 'updated': 2, 'deleted': 0},
        'by_source': {}
    },
    'downloads': [],
    'total_changes': 7,
    'change_types': {'ADD': 5, 'UPDATE': 2}
}

# Write to timestamped doc
db.collection('import_sessions').document(import_batch_id).set(session_data)
print(f"[OK] Written to import_sessions/{import_batch_id}")

# Write to latest_import_session
db.collection('import_sessions').document('latest_import_session').set(session_data)
print(f"[OK] Written to latest_import_session")

# Write a sample entry to the entries subcollection
entry = {
    'timestamp': datetime.utcnow().isoformat(),
    'change_type': 'ADD',
    'entity_id': 'TEST_ENTITY_1',
    'entity_name': 'Test Entity',
    'source': 'TEST',
    'user': 'manual_test'
}
db.collection('import_sessions').document(import_batch_id).collection('entries').document('0').set(entry)
print(f"[OK] Written entry to import_sessions/{import_batch_id}/entries/0")

print("\n[OK] All writes completed. Check Firestore console to verify.")
