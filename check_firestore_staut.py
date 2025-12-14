#!/usr/bin/env python3
"""
Check what's actually in Firestore for a specific entity
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase with Application Default Credentials
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {'projectId': 'sanction-defender-firebase'})

db = firestore.client()

# Search for STAUT in both collections by querying main_name
print("Searching for STAUT in Firestore...")
print("=" * 80)

# Query all sanctions_entities
query = db.collection('sanctions_entities')
docs = query.stream()

staut_records = []
for doc in docs:
    data = doc.to_dict()
    if 'STAUT' in data.get('main_name', ''):
        staut_records.append({
            'id': data.get('id'),
            'source': data.get('sanction_source'),
            'name': data.get('main_name'),
            'entity_type': data.get('entity_type'),
            'unique_id': data.get('unique_sanction_id')
        })

print(f"\nFound {len(staut_records)} STAUT records in Firestore:")
for rec in staut_records[:10]:  # Show first 10
    print(f"\n  ID: {rec['id']}")
    print(f"  Source: {rec['source']}")
    print(f"  Name: {rec['name']}")
    print(f"  Type: {rec['entity_type']}")
    print(f"  Unique ID: {rec['unique_id']}")

# Count by source
sources = {}
for rec in staut_records:
    source = rec['source']
    sources[source] = sources.get(source, 0) + 1

print(f"\n\nSTAUT records by source:")
for source, count in sources.items():
    print(f"  {source}: {count}")
