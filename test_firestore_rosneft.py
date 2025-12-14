#!/usr/bin/env python3
"""
Diagnostic script to check if Rosneft and Sberbank exist in Firestore
"""

from google.cloud import firestore
import os
import json

# Set credentials from service account file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
    os.path.dirname(__file__), 'dummy-service-account.json'
)

# Initialize Firestore
try:
    db = firestore.Client()
except Exception as e:
    print(f"Error initializing Firestore: {e}")
    print("\nTrying with explicit project ID...")
    # Try with explicit project settings
    import google.cloud.firestore
    db = firestore.Client(project='sanction-defender-9f0d8')

# Search for Rosneft records
print("=" * 60)
print("SEARCHING FOR ROSNEFT RECORDS")
print("=" * 60)

collection = db.collection('sanctions_entities')

# Try searching by main_name
docs = collection.where('main_name', '==', 'Rosneft').stream()
rosneft_docs = list(docs)
print(f"\nExact search for 'Rosneft' by main_name: {len(rosneft_docs)} records found")
for doc in rosneft_docs:
    data = doc.to_dict()
    print(f"\n  ID: {data.get('id')}")
    print(f"  Main Name: {data.get('main_name')}")
    print(f"  Entity Type: {data.get('entity_type')}")
    print(f"  Country: {data.get('country')}")
    print(f"  Source: {data.get('sanction_source')}")
    print(f"  Aliases: {data.get('aliases', [])}")
    print(f"  Programs: {data.get('details', {}).get('programs', [])}")

# Try case-insensitive search by fetching all and checking
print("\n" + "-" * 60)
print("Searching all records containing 'Rosneft' (case-insensitive)...")
print("-" * 60)
all_docs = collection.limit(5000).stream()
rosneft_all = []
for doc in all_docs:
    data = doc.to_dict()
    main_name = data.get('main_name', '').lower()
    aliases = [a.lower() for a in data.get('aliases', [])]
    if 'rosneft' in main_name or any('rosneft' in a for a in aliases):
        rosneft_all.append(data)

print(f"Found {len(rosneft_all)} records with 'rosneft' in name or aliases")
for data in rosneft_all:
    print(f"\n  Main Name: {data.get('main_name')}")
    print(f"  Entity Type: {data.get('entity_type')}")
    print(f"  Country: {data.get('country')}")
    print(f"  Source: {data.get('sanction_source')}")
    print(f"  Aliases: {data.get('aliases', [])}")

# Now search for Sberbank
print("\n" + "=" * 60)
print("SEARCHING FOR SBERBANK RECORDS")
print("=" * 60)

# Try searching by main_name
docs = collection.where('main_name', '==', 'Sberbank').stream()
sberbank_docs = list(docs)
print(f"\nExact search for 'Sberbank' by main_name: {len(sberbank_docs)} records found")
for doc in sberbank_docs:
    data = doc.to_dict()
    print(f"\n  ID: {data.get('id')}")
    print(f"  Main Name: {data.get('main_name')}")
    print(f"  Entity Type: {data.get('entity_type')}")
    print(f"  Country: {data.get('country')}")
    print(f"  Source: {data.get('sanction_source')}")
    print(f"  Aliases: {data.get('aliases', [])}")
    print(f"  Programs: {data.get('details', {}).get('programs', [])}")

# Try case-insensitive search
print("\n" + "-" * 60)
print("Searching all records containing 'Sberbank' (case-insensitive)...")
print("-" * 60)
all_docs = collection.limit(5000).stream()
sberbank_all = []
for doc in all_docs:
    data = doc.to_dict()
    main_name = data.get('main_name', '').lower()
    aliases = [a.lower() for a in data.get('aliases', [])]
    if 'sberbank' in main_name or any('sberbank' in a for a in aliases):
        sberbank_all.append(data)

print(f"Found {len(sberbank_all)} records with 'sberbank' in name or aliases")
for data in sberbank_all:
    print(f"\n  Main Name: {data.get('main_name')}")
    print(f"  Entity Type: {data.get('entity_type')}")
    print(f"  Country: {data.get('country')}")
    print(f"  Source: {data.get('sanction_source')}")
    print(f"  Aliases: {data.get('aliases', [])}")

print("\n" + "=" * 60)
print("DATABASE STATISTICS")
print("=" * 60)
all_docs = collection.limit(5000).stream()
total = 0
by_type = {}
by_source = {}
for doc in all_docs:
    data = doc.to_dict()
    total += 1
    etype = data.get('entity_type', 'unknown')
    source = data.get('sanction_source', 'unknown')
    by_type[etype] = by_type.get(etype, 0) + 1
    by_source[source] = by_source.get(source, 0) + 1

print(f"Total records queried: {total}")
print(f"\nBy Entity Type:")
for etype, count in sorted(by_type.items()):
    print(f"  {etype}: {count}")
print(f"\nBy Source:")
for source, count in sorted(by_source.items()):
    print(f"  {source}: {count}")
