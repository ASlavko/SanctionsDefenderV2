#!/usr/bin/env python3
"""
Check Firestore collection size and distribution by source
"""

import requests
import json

# Test querying different sources
API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("TESTING FIRESTORE COLLECTION SIZE AND DISTRIBUTION")
print("=" * 70)

sources = ["EU", "UK", "US_SDN_SIMPLE", "US_NON_SDN_SIMPLE"]

for source in sources:
    # Query with a very generic search to get all records from this source
    params = {"q": "a", "source": source, "limit": 1}
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\nSource: {source}")
            print(f"  Sample query 'a': {data.get('count')} matches (limited to 1)")
            print(f"  Query time: {data.get('query_time_ms')}ms")
            if data.get('matches'):
                print(f"  First result: {data['matches'][0].get('name')}")
        else:
            print(f"\nSource {source}: HTTP {response.status_code}")
    except Exception as e:
        print(f"\nSource {source}: Error - {e}")

print("\n" + "=" * 70)
print("Testing with EU source specifically for Sberbank:")
print("=" * 70)

test_cases = [
    {"q": "Sberbank", "source": "EU"},
    {"q": "SBERBANK", "source": "EU"},
    {"q": "SBERBANK OF RUSSIA", "source": "EU"},
]

for params in test_cases:
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\nQuery: {params}")
            print(f"  Matches: {data.get('count')}")
            if data.get('matches'):
                for i, match in enumerate(data.get('matches', [])[:3], 1):
                    print(f"  {i}. {match.get('name')} - Confidence: {match.get('confidence')}%")
        else:
            print(f"\nQuery {params}: HTTP {response.status_code}")
    except Exception as e:
        print(f"\nQuery {params}: Error - {e}")
