#!/usr/bin/env python3
"""
Test searching for the specific Sberbank record and debug why it's not found
"""

import requests
import json

# The deployed search API endpoint
API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("TESTING SEARCH API WITH KNOWN SBERBANK RECORD")
print("=" * 70)

# Test cases for Sberbank with different search parameters
test_cases = [
    {
        "name": "Sberbank (no filters)",
        "params": {"q": "Sberbank"}
    },
    {
        "name": "Sberbank (with EU source)",
        "params": {"q": "Sberbank", "source": "EU"}
    },
    {
        "name": "SBERBANK OF RUSSIA (exact from main_name)",
        "params": {"q": "SBERBANK OF RUSSIA"}
    },
    {
        "name": "PUBLIC JOINT STOCK COMPANY SBERBANK (exact name start)",
        "params": {"q": "PUBLIC JOINT STOCK COMPANY SBERBANK"}
    },
    {
        "name": "Test with very low limit",
        "params": {"q": "Sberbank", "limit": 100}
    },
    {
        "name": "Test with country=Russia",
        "params": {"q": "Sberbank", "country": "Russia"}
    },
    {
        "name": "Test with type=company",
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
                print(f"\nMatches:")
                for i, match in enumerate(data.get('matches', []), 1):
                    print(f"  {i}. {match.get('name')} ({match.get('source')})")
                    print(f"     ID: {match.get('id')}")
                    print(f"     Confidence: {match.get('confidence')}%")
                    print(f"     Type: {match.get('entity_type')}")
                    print(f"     Country: {match.get('country')}")
                    if match.get('aliases'):
                        print(f"     Aliases (first 3): {', '.join(match.get('aliases', [])[:3])}")
            else:
                print("NO MATCHES FOUND!")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 70)
print("\nNOTE: Known Sberbank record in database:")
print("  ID: EU_EU.8537.32")
print("  Expected to contain 'SBERBANK' in main_name or aliases")
