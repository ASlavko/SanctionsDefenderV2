#!/usr/bin/env python3
"""
Import parsed sanctions data into real Firestore database.
Uses firebase_admin with cached Firebase CLI credentials.
"""

import os
import sys
import json

# Try to use the credentials from Firebase CLI cache
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Get project ID
    firebaserc_path = os.path.join(os.path.dirname(__file__), '.firebaserc')
    project_id = 'sanction-defender-firebase'
    
    if os.path.exists(firebaserc_path):
        try:
            with open(firebaserc_path, 'r') as f:
                config = json.load(f)
                project_id = config.get('projects', {}).get('default', project_id)
        except Exception as e:
            print(f"[⚠] Could not read .firebaserc: {e}")
    
    print(f"[>] Using Google Cloud Project: {project_id}")
    
    # Initialize Firebase Admin SDK with default application credentials
    # This will use the cached credentials from Firebase CLI login
    if not firebase_admin._apps:
        # Try to get credentials from the environment or Firebase cache
        cred = None
        
        # Check for GOOGLE_APPLICATION_CREDENTIALS env var
        if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            cred = credentials.Certificate(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
        else:
            # Use Application Default Credentials (which Firebase CLI sets up)
            cred = credentials.ApplicationDefault()
        
        firebase_admin.initialize_app(cred, {
            'projectId': project_id
        })
    
    db = firestore.client()
    print(f"[OK] Connected to Firestore database for project '{project_id}'")

except Exception as e:
    print(f"[X] Failed to initialize Firebase Admin: {e}")
    print(f"\n[!] SOLUTION: Download a service account key from GCP and set it:")
    print(f"    1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts")
    print(f"    2. Select your project (sanction-defender-firebase)")
    print(f"    3. Create a new service account or select existing Firebase admin service account")
    print(f"    4. Generate a JSON key and download it")
    print(f"    5. Set the environment variable:")
    print(f"       $env:GOOGLE_APPLICATION_CREDENTIALS = 'C:\\path\\to\\service-account-key.json'")
    print(f"    6. Run this script again")
    sys.exit(1)

# Import parsed JSONL files into Firestore
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
    errors = 0
    
    print(f"\n[>] Importing {source_name} from {jsonl_file}...")
    
    with open(jsonl_file, 'r', encoding='utf-8') as jf:
        for line_num, line in enumerate(jf, 1):
            try:
                rec = json.loads(line)
                
                # Skip error lines
                if 'error' in rec:
                    errors += 1
                    continue
                
                # Use 'id' field as document ID if available
                doc_id = rec.get('id')
                if doc_id:
                    doc_ref = coll.document(doc_id)
                    doc_ref.set(rec, merge=False)  # IMPORTANT: merge=False to prevent data corruption
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
    
    print(f"[OK] {source_name}: Imported {imported} records (errors: {errors})")
    total_imported += imported

print(f"\n[OK] Total imported: {total_imported} records")

# Verify import by querying the collection
print(f"\n[>] Verifying data in Firestore...")
try:
    coll = db.collection('sanctions_entities')
    docs = list(coll.limit(3).stream())
    
    print(f"[OK] Sample records from Firestore:")
    for i, doc in enumerate(docs, 1):
        data = doc.to_dict()
        print(f"  Sample {i}: {data.get('id')} - {data.get('main_name', 'N/A')} ({data.get('sanction_source', 'N/A')})")
    
    # Count total documents
    all_docs = list(coll.stream())
    total_docs = len(all_docs)
    print(f"[OK] Total documents in 'sanctions_entities' collection: {total_docs}")
except Exception as e:
    print(f"[X] Error verifying data: {e}")

print("\n[OK] Import completed successfully!")
