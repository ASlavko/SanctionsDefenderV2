#!/usr/bin/env python3
"""
Test searching in US_NON_SDN_SIMPLE source with longer timeout
"""

import requests

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("TESTING WITH FULL DATABASE SEARCH (timeout=60s)")
print("=" * 70)

test_cases = [
    {"q": "SBERBANK OF RUSSIA", "source": "US_NON_SDN_SIMPLE"},
    {"q": "Sberbank", "source": "US_NON_SDN_SIMPLE"},
    {"q": "ROSNEFT", "source": "US_NON_SDN_SIMPLE"},
    {"q": "Rosneft", "source": "US_NON_SDN_SIMPLE"},
]

for params in test_cases:
    print(f"\nQuery: {params['q']} (source: {params['source']})")
    
    try:
        response = requests.get(API_URL, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count')
            query_time = data.get('query_time_ms')
            print(f"  Status: {data.get('status')}")
            print(f"  Matches: {count}")
            print(f"  Query time: {query_time}ms")
            
            if data.get('matches'):
                for match in data.get('matches', [])[:5]:
                    print(f"    - {match.get('name')} ({match.get('confidence')}%)")
                    if 'SBERBANK' in match.get('name', '').upper() or 'ROSNEFT' in match.get('name', '').upper():
                        print(f"      ✓ FOUND TARGET ENTITY!")
            else:
                print("  NO MATCHES FOUND")
        else:
            print(f"  Error: HTTP {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"  TIMEOUT after 60 seconds")
    except Exception as e:
        print(f"  Error: {e}")
