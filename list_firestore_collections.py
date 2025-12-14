#!/usr/bin/env python3
"""
List all Firestore collections to understand the database structure
"""

import firebase_admin
from firebase_admin import firestore

# Initialize Firebase Admin using ADC
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

db = firestore.client()

print("=" * 70)
print("LISTING ALL FIRESTORE COLLECTIONS")
print("=" * 70)

try:
    collections = db.collections()
    
    collection_list = []
    for collection in collections:
        collection_list.append(collection.id)
    
    if collection_list:
        print(f"\nFound {len(collection_list)} collection(s):")
        for coll_name in collection_list:
            print(f"\n  📁 {coll_name}")
            
            # Get count for each collection
            try:
                coll_ref = db.collection(coll_name)
                count_query = coll_ref.count()
                count_result = count_query.get()
                count = count_result[0][0].value
                print(f"      Documents: {count:,}")
                
                # Get a sample document
                sample_docs = coll_ref.limit(1).stream()
                for doc in sample_docs:
                    print(f"      Sample ID: {doc.id}")
                    data = doc.to_dict()
                    # Show first few fields
                    fields = list(data.keys())[:5]
                    print(f"      Fields: {', '.join(fields)}")
                    break
                    
            except Exception as e:
                print(f"      Error getting count: {e}")
    else:
        print("\n❌ No collections found in the database!")
        print("\nThis means the database is empty or not yet initialized.")
        print("You may need to run the import script to populate it.")
        
except Exception as e:
    print(f"\n❌ Error listing collections: {e}")

print("\n" + "=" * 70)
