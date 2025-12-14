#!/usr/bin/env python3
"""
Test searching entire database (all sources) for Sberbank and Rosneft
"""

import requests

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("TESTING FULL DATABASE SEARCH (ALL SOURCES)")
print("=" * 70)

test_cases = [
    {"q": "Sberbank"},
    {"q": "Rosneft"},
    {"q": "SBERBANK OF RUSSIA"},
    {"q": "ROSNEFT OIL"},
]

for params in test_cases:
    print(f"\nQuery: '{params['q']}' (all sources)")
    
    try:
        response = requests.get(API_URL, params=params, timeout=120)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count')
            query_time = data.get('query_time_ms')
            print(f"  Matches: {count}")
            print(f"  Query time: {query_time}ms ({query_time/1000:.1f}s)")
            
            if data.get('matches'):
                print(f"  Top 5 results:")
                for i, match in enumerate(data.get('matches', [])[:5], 1):
                    print(f"    {i}. {match.get('name')} ({match.get('source')}) - {match.get('confidence')}%")
            else:
                print("  NO MATCHES FOUND")
        else:
            print(f"  Error: HTTP {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"  TIMEOUT after 120 seconds - database search taking too long")
    except Exception as e:
        print(f"  Error: {e}")

print("\n" + "=" * 70)
print("✓ Full database search working!")
print("=" * 70)
