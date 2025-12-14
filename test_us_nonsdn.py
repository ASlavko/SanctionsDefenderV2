#!/usr/bin/env python3
"""
Test searching in US_NON_SDN_SIMPLE source where we know Sberbank exists
"""

import requests

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("TESTING US_NON_SDN_SIMPLE SOURCE FOR SBERBANK")
print("=" * 70)

test_cases = [
    {"q": "Sberbank", "source": "US_NON_SDN_SIMPLE"},
    {"q": "SBERBANK", "source": "US_NON_SDN_SIMPLE"},
    {"q": "SBERBANK OF RUSSIA", "source": "US_NON_SDN_SIMPLE"},
    {"q": "PJSC SBERBANK", "source": "US_NON_SDN_SIMPLE"},
    {"q": "Rosneft", "source": "US_NON_SDN_SIMPLE"},
    {"q": "ROSNEFT", "source": "US_NON_SDN_SIMPLE"},
    {"q": "OPEN JOINT-STOCK COMPANY ROSNEFT", "source": "US_NON_SDN_SIMPLE"},
]

for params in test_cases:
    print(f"\nQuery: {params['q']} (source: {params['source']})")
    
    try:
        response = requests.get(API_URL, params=params, timeout=20)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count')
            print(f"  Matches: {count}")
            
            if data.get('matches'):
                for match in data.get('matches', [])[:3]:
                    print(f"    - {match.get('name')} ({match.get('confidence')}%)")
                    if 'SBERBANK' in match.get('name', '').upper() or 'ROSNEFT' in match.get('name', '').upper():
                        print(f"      ✓ FOUND TARGET ENTITY!")
        else:
            print(f"  Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
