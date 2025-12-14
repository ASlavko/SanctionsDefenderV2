#!/usr/bin/env python3
"""
Test the actual deployed search API to see if Rosneft and Sberbank are found
"""

import requests
import json

# The deployed search API endpoint
API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("TESTING DEPLOYED SEARCH API")
print("=" * 70)

test_cases = [
    {
        "name": "Rosneft (exact)",
        "params": {"q": "Rosneft"}
    },
    {
        "name": "rosneft (lowercase)",
        "params": {"q": "rosneft"}
    },
    {
        "name": "Resneft (typo)",
        "params": {"q": "Resneft"}
    },
    {
        "name": "Sberbank (exact)",
        "params": {"q": "Sberbank"}
    },
    {
        "name": "sberbank (lowercase)",
        "params": {"q": "sberbank"}
    },
    {
        "name": "Sbernak (typo)",
        "params": {"q": "Sbernak"}
    },
    {
        "name": "Rosneft (company filter)",
        "params": {"q": "Rosneft", "type": "company"}
    },
    {
        "name": "Sberbank (company filter)",
        "params": {"q": "Sberbank", "type": "company"}
    },
]

for test in test_cases:
    print(f"\n{'-' * 70}")
    print(f"TEST: {test['name']}")
    print(f"Parameters: {test['params']}")
    print(f"{'-' * 70}")
    
    try:
        response = requests.get(API_URL, params=test['params'], timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Matches found: {data.get('count')}")
            print(f"Query time: {data.get('query_time_ms')}ms")
            
            if data.get('matches'):
                print(f"\nTop matches:")
                for i, match in enumerate(data.get('matches', [])[:3], 1):
                    print(f"  {i}. {match.get('name')} ({match.get('source')})")
                    print(f"     Confidence: {match.get('confidence')}%")
                    print(f"     Type: {match.get('entity_type')}")
                    print(f"     Country: {match.get('country')}")
                    if match.get('aliases'):
                        print(f"     Aliases: {', '.join(match.get('aliases', [])[:3])}")
            else:
                print("NO MATCHES FOUND!")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 70)
