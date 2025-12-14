#!/usr/bin/env python3
"""
Test searches to determine database status
"""

import requests

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("DATABASE STATUS CHECK")
print("=" * 70)

test_queries = [
    ("Sberbank", None),
    ("Rosneft", None),
    ("Putin", None),
    ("", "EU"),
    ("", "UK"),
    ("", "US_SDN_SIMPLE"),
    ("", "US_NON_SDN_SIMPLE"),
]

for query, source in test_queries:
    params = {}
    if query:
        params['q'] = query
    if source:
        params['source'] = source
        
    label = f"Query: '{query}'" if query else f"Source: {source} (all records)"
    print(f"\n{label}")
    
    try:
        response = requests.get(API_URL, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            matches = len(data.get('matches', []))
            print(f"  Total count: {count}")
            print(f"  Matches returned: {matches}")
            
            if matches > 0:
                print(f"  Sample: {data['matches'][0].get('name', 'N/A')}")
        else:
            print(f"  Error: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 70)
