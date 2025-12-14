#!/usr/bin/env python3
"""
Simple, fast sanctions import without two-stage validation.
Imports all parsed data directly to Firestore with audit logging.
"""

import os
import json
import sys
from datetime import datetime

# Add functions directory to path to import matching logic
sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))
from matching import NameMatcher

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Get project ID from .firebaserc
    firebaserc_path = os.path.join(os.path.dirname(__file__), '.firebaserc')
    project_id = 'sanction-defender-firebase'
    
    if os.path.exists(firebaserc_path):
        try:
            with open(firebaserc_path, 'r') as f:
                config = json.load(f)
                project_id = config.get('projects', {}).get('default', project_id)
        except Exception as e:
            print(f"[!] Could not read .firebaserc: {e}")
    
    print(f"[>] Using Google Cloud Project: {project_id}")
    
    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {'projectId': project_id})
    
    db = firestore.client()
    print(f"[OK] Connected to Firestore")
    
except Exception as e:
    print(f"[X] Firebase initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def import_source(source_name: str, file_path: str):
    """Import data from a single source file"""
    
    if not os.path.exists(file_path):
        print(f"[X] File not found: {file_path}")
        return 0, 0
    
    print(f"\n[>] Importing {source_name}...")
    
    coll = db.collection('sanctions_entities')
    imported = 0
    skipped = 0
    errors = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                record = json.loads(line)
                
                # Skip error records
                if 'error' in record:
                    skipped += 1
                    continue
                
                # Validate required fields
                if not all(record.get(field) for field in ['id', 'sanction_source', 'main_name', 'entity_type']):
                    skipped += 1
                    continue
                
                # Verify source matches
                if record.get('sanction_source') != source_name:
                    skipped += 1
                    continue
                
                # Generate search tokens if missing
                if 'search_tokens' not in record:
                    tokens = set()
                    # Add tokens from main name
                    if record.get('main_name'):
                        tokens.update(NameMatcher.generate_search_tokens(record['main_name']))
                    
                    # Add tokens from aliases
                    for alias in record.get('aliases', []):
                        if alias:
                            tokens.update(NameMatcher.generate_search_tokens(alias))
                    
                    record['search_tokens'] = list(tokens)

                # Set the document
                doc_id = record.get('id')
                coll.document(doc_id).set(record, merge=False)
                imported += 1
                
                # Show progress
                if imported % 1000 == 0:
                    print(f"    Imported {imported} records...")
                
            except json.JSONDecodeError:
                errors += 1
            except Exception as e:
                errors += 1
                if errors <= 5:  # Log first few errors
                    print(f"    [!] Error at line {line_num}: {e}")
    
    print(f"   [OK] {source_name}: {imported} imported, {skipped} skipped, {errors} errors")
    return imported, errors


def main():
    print("=" * 80)
    print("SANCTIONS DATA IMPORT")
    print("=" * 80)
    
    import_batch_id = f"import_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    sources = [
        ('EU', 'data/parsed/EU.jsonl'),
        ('UK', 'data/parsed/UK.jsonl'),
        ('US_SDN_SIMPLE', 'data/parsed/US_SDN_SIMPLE.jsonl'),
        ('US_NON_SDN_SIMPLE', 'data/parsed/US_NON_SDN_SIMPLE.jsonl'),
    ]
    
    total_imported = 0
    total_errors = 0
    
    for source_name, file_path in sources:
        file_path = os.path.join(os.path.dirname(__file__), file_path)
        imported, errors = import_source(source_name, file_path)
        total_imported += imported
        total_errors += errors
    
    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"Batch ID: {import_batch_id}")
    print(f"Total imported: {total_imported}")
    print(f"Total errors: {total_errors}")
    
    # Create audit log entry
    try:
        audit_doc = db.collection('audit_logs').document(import_batch_id)
        audit_doc.set({
            'import_batch_id': import_batch_id,
            'timestamp': datetime.utcnow().isoformat(),
            'total_imported': total_imported,
            'total_errors': total_errors,
            'type': 'simple_import',
        })
        print(f"[OK] Audit log saved: audit_logs/{import_batch_id}")
    except Exception as e:
        print(f"[!] Could not save audit log: {e}")
    
    if total_errors > 0:
        print(f"\n[!] WARNING: {total_errors} errors occurred during import")
    
    print("\n[SUCCESS] Import completed!")


if __name__ == '__main__':
    main()
