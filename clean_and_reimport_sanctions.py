#!/usr/bin/env python3
"""
Clean and re-import sanctions data with proper source isolation.

This script:
1. Deletes all existing sanctions_entities documents
2. Re-imports all data with strict source isolation
3. Uses merge=False to prevent data corruption
"""

import os
import json
import sys

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    project_id = 'sanction-defender-firebase'
    
    if not firebase_admin._apps:
        # Try to use service account key if available
        service_account_path = 'dummy-service-account.json'
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
        else:
            cred = credentials.ApplicationDefault()
        
        firebase_admin.initialize_app(cred, {'projectId': project_id})
    
    db = firestore.client()
    print(f"[OK] Connected to Firestore")

except Exception as e:
    print(f"[X] Failed to initialize Firebase Admin: {e}")
    sys.exit(1)

# Confirm before deleting
print("\n" + "=" * 80)
print("DANGEROUS OPERATION: This will delete ALL sanctions_entities documents!")
print("=" * 80)
response = input("\nType 'DELETE_ALL_SANCTIONS_DATA' to confirm: ").strip()

if response != 'DELETE_ALL_SANCTIONS_DATA':
    print("[!] Operation cancelled.")
    sys.exit(0)

print("\n[>] Deleting all existing sanctions_entities documents...")
coll = db.collection('sanctions_entities')
docs = coll.stream()
deleted = 0
for doc in docs:
    doc.reference.delete()
    deleted += 1
    if deleted % 1000 == 0:
        print(f"  Deleted {deleted} documents...")

print(f"[OK] Deleted {deleted} documents total")

# Re-import with proper source isolation
parsed_dir = os.path.join(os.path.dirname(__file__), 'data', 'parsed')
sources = ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']

total_imported = 0
for source_name in sources:
    jsonl_file = os.path.join(parsed_dir, f"{source_name}.jsonl")
    
    if not os.path.exists(jsonl_file):
        print(f"[!] File not found: {jsonl_file}")
        continue
    
    coll = db.collection('sanctions_entities')
    imported = 0
    
    print(f"\n[>] Importing {source_name} from {jsonl_file}...")
    
    with open(jsonl_file, 'r', encoding='utf-8') as jf:
        for line_num, line in enumerate(jf, 1):
            try:
                rec = json.loads(line)
                
                # Skip error lines
                if 'error' in rec:
                    continue
                
                # Verify source matches filename
                if rec.get('sanction_source') != source_name:
                    print(f"  [!] Line {line_num}: Record has sanction_source='{rec.get('sanction_source')}' but expected '{source_name}'")
                    print(f"      Skipping to prevent data corruption!")
                    continue
                
                # Use 'id' field as document ID
                doc_id = rec.get('id')
                if doc_id:
                    coll.document(doc_id).set(rec, merge=False)  # IMPORTANT: merge=False
                    imported += 1
                
                if imported % 1000 == 0:
                    print(f"  Imported {imported}...")
            
            except json.JSONDecodeError as e:
                print(f"  [!] JSON error on line {line_num}: {e}")
    
    print(f"[OK] Imported {imported} records from {source_name}")
    total_imported += imported

print(f"\n{'='*80}")
print(f"[OK] Import complete! Total imported: {total_imported} records")
print(f"{'='*80}")

# Verify import
print("\n[>] Verifying import...")
for source_name in sources:
    count = len(list(coll.where('sanction_source', '==', source_name).stream()))
    print(f"  {source_name}: {count} records")
