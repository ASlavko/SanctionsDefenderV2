#!/usr/bin/env python3
"""
Test to directly query Firestore and check what records exist
Uses the API to query by source to avoid authentication issues
"""

import requests
import json

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("TESTING API WITH SOURCE FILTERS TO FIND ACTUAL RECORDS")
print("=" * 70)

# Test to see ALL records by querying with a very generic term that should match anything
# We'll use very short common words that appear in many names

test_sources = {
    "EU": 100,
    "UK": 100,
    "US_SDN_SIMPLE": 100,
    "US_NON_SDN_SIMPLE": 100,
}

for source, limit in test_sources.items():
    print(f"\n{'-' * 70}")
    print(f"Testing source: {source}")
    print(f"{'-' * 70}")
    
    # Query with empty to see if we get any results
    params = {"source": source, "q": "a", "limit": 10}
    try:
        response = requests.get(API_URL, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count')
            print(f"Query results: {count} matches")
            print(f"Query time: {data.get('query_time_ms')}ms")
            
            if data.get('matches'):
                print("\nTop 5 matches:")
                for i, match in enumerate(data.get('matches', [])[:5], 1):
                    print(f"  {i}. ID: {match.get('id')}")
                    print(f"     Name: {match.get('name')}")
                    print(f"     Confidence: {match.get('confidence')}%")
        else:
            print(f"Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
print("Now testing specifically for known Sberbank entry")
print("=" * 70)

# The known ID is EU_EU.8537.32
# Test with more complete name variations
test_variations = [
    ("SBERBANK OF RUSSIA", None),
    ("SBERBANK OF RUSSIA", "EU"),
    ("PUBLIC JOINT", "EU"),
    ("PUBLIC JOINT STOCK COMPANY", "EU"),
]

for query, source in test_variations:
    params = {"q": query}
    if source:
        params["source"] = source
    
    print(f"\nQuery: '{query}' (source: {source if source else 'all'})")
    
    try:
        response = requests.get(API_URL, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count')
            print(f"  Matches: {count}")
            
            # Check if any match is the Sberbank record
            for match in data.get('matches', []):
                if 'SBERBANK' in match.get('name', '').upper():
                    print(f"  ✓ Found Sberbank-related: {match.get('name')} ({match.get('confidence')}%)")
        else:
            print(f"  Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
