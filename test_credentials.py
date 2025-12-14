#!/usr/bin/env python3
"""Quick test to verify Firebase credentials work"""

import os
import sys

# Set encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("[TEST] Firebase Credentials Test")
print(f"[>] GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'NOT SET')}")

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    print("[>] Imported firebase_admin successfully")
    
    if firebase_admin._apps:
        print("[!] Firebase app already initialized, clearing...")
        for app in firebase_admin._apps.values():
            firebase_admin.delete_app(app)
    
    print("[>] Attempting to create credentials...")
    cred = credentials.ApplicationDefault()
    print("[OK] Created ApplicationDefault credentials")
    
    print("[>] Attempting to initialize app...")
    firebase_admin.initialize_app(cred, {'projectId': 'sanction-defender-firebase'})
    print("[OK] Initialized Firebase app")
    
    print("[>] Getting Firestore client...")
    db = firestore.client()
    print("[OK] Got Firestore client")
    
    print("[>] Testing Firestore connection...")
    docs = db.collection('sanctions_entities').limit(1).stream()
    doc_count = sum(1 for _ in docs)
    print(f"[OK] Firestore connection works! Found {doc_count} document(s) in test query")
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SUCCESS] All tests passed!")
