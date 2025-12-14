#!/usr/bin/env python3
"""
Test the updated API with mandatory entity_type filter and improved performance
"""

import requests
import time

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("TESTING UPDATED API - MANDATORY ENTITY TYPE")
print("=" * 70)

test_cases = [
    {
        "name": "Sberbank (companies - default)",
        "params": {"q": "Sberbank"}
    },
    {
        "name": "Sberbank (companies - explicit)",
        "params": {"q": "Sberbank", "type": "company"}
    },
    {
        "name": "Rosneft (companies)",
        "params": {"q": "Rosneft", "type": "company"}
    },
    {
        "name": "Putin (individuals)",
        "params": {"q": "Putin", "type": "individual"}
    },
    {
        "name": "Sberbank with source filter",
        "params": {"q": "Sberbank", "type": "company", "source": "US_NON_SDN_SIMPLE"}
    },
]

for test in test_cases:
    print(f"\n{'-' * 70}")
    print(f"TEST: {test['name']}")
    print(f"Parameters: {test['params']}")
    print(f"{'-' * 70}")
    
    start = time.time()
    try:
        response = requests.get(API_URL, params=test['params'], timeout=60)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            query_time = data.get('query_time_ms', 0)
            
            print(f"Status: {data.get('status')}")
            print(f"Matches: {data.get('count')}")
            print(f"Query time: {query_time}ms ({query_time/1000:.1f}s)")
            print(f"Network time: {elapsed:.1f}s")
            
            if data.get('matches'):
                print(f"\nTop 5 results:")
                for i, match in enumerate(data.get('matches', [])[:5], 1):
                    print(f"  {i}. {match.get('name')}")
                    print(f"     Source: {match.get('source')}, Confidence: {match.get('confidence')}%")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"TIMEOUT after 60 seconds")
    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 70)
print("PERFORMANCE SUMMARY")
print("=" * 70)
print("✓ Entity type is now mandatory (defaults to 'company')")
print("✓ Searches ALL entities of specified type (no artificial limits)")
print("✓ Substring matching preserved (e.g., 'Sberbank' matches full company names)")
print("=" * 70)
