#!/usr/bin/env python3
"""
Test script to verify sanctions sources in Firestore
"""

import json
import subprocess
import requests
from datetime import datetime

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

def test_source_isolation():
    """Test that each source returns distinct data"""
    
    print("=" * 80)
    print("TESTING SOURCE ISOLATION AND DATA INTEGRITY")
    print("=" * 80)
    
    # Test 1: Search company in US_SDN_SIMPLE
    print("\n1. SEARCHING 'COMPANY' IN US_SDN_SIMPLE")
    params = {
        'q': 'company',
        'type': 'company',
        'source': 'US_SDN_SIMPLE',
        'limit': 10
    }
    
    response = requests.get(API_URL, params=params)
    data = response.json()
    
    print(f"\n   Status: {data.get('status')}")
    print(f"   Count: {data.get('count')}")
    
    results_sdn = data.get('matches', [])
    sources_sdn = {}
    for match in results_sdn:
        source = match.get('source', 'UNKNOWN')
        sources_sdn[source] = sources_sdn.get(source, 0) + 1
    
    print(f"   Source distribution: {sources_sdn}")
    if 'US_SDN_SIMPLE' in sources_sdn and 'US_NON_SDN_SIMPLE' in sources_sdn:
        print(f"   ⚠️  WARNING: Got results from both US_SDN_SIMPLE AND US_NON_SDN_SIMPLE!")
        print(f"       This indicates the source filter is not working correctly!")
    
    # Test 2: Search company in US_NON_SDN_SIMPLE  
    print("\n2. SEARCHING 'COMPANY' IN US_NON_SDN_SIMPLE")
    params = {
        'q': 'company',
        'type': 'company',
        'source': 'US_NON_SDN_SIMPLE',
        'limit': 10
    }
    
    response = requests.get(API_URL, params=params)
    data = response.json()
    
    print(f"\n   Status: {data.get('status')}")
    print(f"   Count: {data.get('count')}")
    
    results_nonsdn = data.get('matches', [])
    sources_nonsdn = {}
    for match in results_nonsdn:
        source = match.get('source', 'UNKNOWN')
        sources_nonsdn[source] = sources_nonsdn.get(source, 0) + 1
    
    print(f"   Source distribution: {sources_nonsdn}")
    if 'US_NON_SDN_SIMPLE' in sources_nonsdn and 'US_SDN_SIMPLE' in sources_nonsdn:
        print(f"   ⚠️  WARNING: Got results from both US_NON_SDN_SIMPLE AND US_SDN_SIMPLE!")
        print(f"       This indicates the source filter is not working correctly!")
    
    # Test 3: Check if results are identical
    print("\n3. COMPARING RESULTS BETWEEN SOURCES")
    sdn_names = {m['name'] for m in results_sdn}
    nonsdn_names = {m['name'] for m in results_nonsdn}
    
    overlap = sdn_names & nonsdn_names
    if overlap:
        print(f"\n   ⚠️  OVERLAP FOUND: {len(overlap)} entities appear in both lists:")
        for name in list(overlap)[:5]:
            print(f"      - {name}")
    else:
        print(f"\n   ✓ No overlap found between results")
    
    # Test 4: Check entity types in Non-SDN
    print("\n4. ENTITY TYPES IN RESULTS")
    
    if results_nonsdn:
        entity_types_nonsdn = {}
        for match in results_nonsdn:
            etype = match.get('entity_type', 'UNKNOWN')
            entity_types_nonsdn[etype] = entity_types_nonsdn.get(etype, 0) + 1
        
        print(f"\n   US_NON_SDN_SIMPLE results:")
        print(f"   Entity types: {entity_types_nonsdn}")
        
        # Show sample
        print(f"   Sample results:")
        for match in results_nonsdn[:3]:
            print(f"     - {match['name'][:40]:40} | Type: {match['entity_type']:12} | Confidence: {match['confidence']}%")

if __name__ == '__main__':
    test_source_isolation()

