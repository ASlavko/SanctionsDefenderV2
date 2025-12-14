#!/usr/bin/env python3
"""
Test script: Import parsed sanctions data into Firestore emulator.
Uses google.cloud.firestore directly to bypass firebase_admin auth requirements.
"""

import os
import sys
import json

# Configure emulator host
os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'

# Use google.cloud.firestore directly (avoids firebase_admin credential issues)
from google.cloud import firestore

# Initialize Firestore client (emulator ignores credentials)
try:
    db = firestore.Client(project='sanctions-app')
    print("[✓] Connected to Firestore emulator at localhost:8080")
except Exception as e:
    print(f"[✗] Failed to initialize Firestore: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Import parsed JSONL files into Firestore
parsed_dir = os.path.join(os.path.dirname(__file__), 'data', 'parsed')
sources = ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']

total_imported = 0
for source_name in sources:
    jsonl_file = os.path.join(parsed_dir, f"{source_name}.jsonl")
    
    if not os.path.exists(jsonl_file):
        print(f"[⚠] File not found: {jsonl_file}")
        continue
    
    coll = db.collection('sanctions_entities')
    imported = 0
    errors = 0
    
    print(f"\n[→] Importing {source_name} from {jsonl_file}...")
    
    with open(jsonl_file, 'r', encoding='utf-8') as jf:
        for line_num, line in enumerate(jf, 1):
            try:
                rec = json.loads(line)
                
                # Skip error lines
                if 'error' in rec:
                    errors += 1
                    continue
                
                # Use 'id' field as document ID if available, else generate one
                doc_id = rec.get('id')
                if doc_id:
                    doc_ref = coll.document(doc_id)
                    doc_ref.set(rec, merge=True)
                else:
                    # Auto-generate document ID
                    coll.add(rec)
                
                imported += 1
                
                # Print progress every 500 records
                if imported % 500 == 0:
                    print(f"  ... {imported} records imported")
                    
            except json.JSONDecodeError as je:
                print(f"  [!] Line {line_num}: JSON decode error: {je}")
                errors += 1
            except Exception as ie:
                print(f"  [!] Line {line_num}: Import error: {ie}")
                errors += 1
    
    print(f"[✓] {source_name}: Imported {imported} records (errors: {errors})")
    total_imported += imported

print(f"\n[✓] Total imported: {total_imported} records")

# Verify import by querying one collection
print(f"\n[→] Verifying data in Firestore...")
try:
    docs = db.collection('sanctions_entities').limit(3).stream()
    sample_count = 0
    for doc in docs:
        sample_count += 1
        data = doc.to_dict()
        print(f"  Sample {sample_count}: {data.get('id')} - {data.get('main_name', 'N/A')} ({data.get('sanction_source', 'N/A')})")
    
    # Count total documents
    total_docs = len(db.collection('sanctions_entities').stream())
    print(f"[✓] Total documents in 'sanctions_entities' collection: {total_docs}")
except Exception as e:
    print(f"[✗] Error verifying data: {e}")

print("\n[✓] Test completed successfully!")
