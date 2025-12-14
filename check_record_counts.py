#!/usr/bin/env python3
"""
Get accurate count of records per sanction source from the unified collection
"""

import requests

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("SANCTION LIST DATABASE RECORD COUNTS")
print("=" * 70)

sources = ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']
total_records = 0

for source in sources:
    try:
        # Use a very broad search with high limit to get accurate counts
        response = requests.get(
            API_URL, 
            params={
                'source': source,
                'q': 'a',  # Match anything with 'a' (most names have this)
                'limit': 1
            }, 
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            total_records += count
            
            print(f"\n{source:20s}: {count:,} records")
            
            # Show a sample record if available
            if data.get('matches'):
                sample = data['matches'][0]
                print(f"  Sample: {sample.get('name')} ({sample.get('entity_type', 'unknown')})")
        else:
            print(f"\n{source:20s}: Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"\n{source:20s}: Error - {e}")

print("\n" + "=" * 70)
print(f"TOTAL RECORDS: {total_records:,}")
print("=" * 70)

# Also check the unified collection
print("\nChecking unified collection (all sources)...")
try:
    response = requests.get(
        API_URL, 
        params={
            'q': 'a',
            'limit': 1
        }, 
        timeout=120
    )
    
    if response.status_code == 200:
        data = response.json()
        total_unified = data.get('count', 0)
        print(f"Total in unified 'sanctions_entities' collection: {total_unified:,} records")
        
        if total_unified != total_records:
            print(f"Note: Difference of {abs(total_unified - total_records):,} records")
except Exception as e:
    print(f"Error checking unified collection: {e}")

print("\n" + "=" * 70)
