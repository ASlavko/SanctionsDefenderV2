#!/usr/bin/env python3
"""
Check the number of records in each sanction list collection
"""

import firebase_admin
from firebase_admin import firestore
import os

# Initialize Firebase Admin using Application Default Credentials
try:
    firebase_admin.get_app()
except ValueError:
    # Initialize without explicit credentials (uses ADC)
    firebase_admin.initialize_app()

db = firestore.client()

print("=" * 70)
print("SANCTION LIST DATABASE RECORD COUNTS")
print("=" * 70)

sources = ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']
total_records = 0

for source in sources:
    collection_name = f'sanctions_{source}'
    try:
        # Get count using aggregation query
        collection_ref = db.collection(collection_name)
        count_query = collection_ref.count()
        count_result = count_query.get()
        
        # Extract the count value
        count = count_result[0][0].value
        total_records += count
        
        print(f"\n{source:20s}: {count:,} records")
        
    except Exception as e:
        print(f"\n{source:20s}: Error - {e}")

print("\n" + "=" * 70)
print(f"TOTAL RECORDS: {total_records:,}")
print("=" * 70)
