#!/usr/bin/env python3
"""
Direct test of various searches to understand database contents
"""

import requests
import json

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("DATABASE CONTENT ANALYSIS")
print("=" * 70)

# Test 1: Known entities
print("\n1. Known Entity Searches:")
for entity in ["Sberbank", "Rosneft", "Putin", "Gazprom", "Abramovich"]:
    response = requests.get(API_URL, params={'q': entity, 'limit': 5}, timeout=60)
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print(f"  {entity:15s}: {count:3d} matches")
        if count > 0 and data.get('matches'):
            print(f"    Top match: {data['matches'][0].get('name')} - {data['matches'][0].get('source')}")

# Test 2: Common letters to find any records
print("\n2. Broad Letter Searches:")
for letter in ['a', 'b', 'c', 'd', 'e']:
    response = requests.get(API_URL, params={'q': letter, 'limit': 1}, timeout=60)
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print(f"  Letter '{letter}': {count} records")

# Test 3: Check by source with broad query
print("\n3. Source-Specific Searches (with query 'bank'):")
for source in ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']:
    response = requests.get(API_URL, params={'q': 'bank', 'source': source, 'limit': 1}, timeout=60)
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print(f"  {source:20s}: {count:3d} matches")
        if count > 0 and data.get('matches'):
            print(f"    Sample: {data['matches'][0].get('name')}")

# Test 4: Empty query with source filter
print("\n4. Source Filter Only (no query):")
for source in ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']:
    response = requests.get(API_URL, params={'source': source, 'limit': 10}, timeout=60)
    print(f"  {source:20s}: HTTP {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Response: {json.dumps(data)[:100]}...")

print("\n" + "=" * 70)
