#!/usr/bin/env python3
"""Verify import results"""

import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {'projectId': 'sanction-defender-firebase'})
    
    db = firestore.client()
    
    print("[>] Verifying import...")
    print()
    
    # Check total count
    all_docs = db.collection('sanctions_entities').stream()
    total = sum(1 for _ in all_docs)
    print(f"Total documents in Firestore: {total}")
    
    # Check by source
    sources = ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']
    for source in sources:
        query = db.collection('sanctions_entities').where('sanction_source', '==', source)
        count = sum(1 for _ in query.stream())
        print(f"  {source:20} {count:6} documents")
    
    print()
    print("[OK] Data verification complete!")
    
except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
