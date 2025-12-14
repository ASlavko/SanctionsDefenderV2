#!/usr/bin/env python3
"""
Check the number of records in each sanction list collection via admin API
"""

import requests

# Use the deployed admin_dashboard function URL
API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

print("=" * 70)
print("SANCTION LIST DATABASE RECORD COUNTS")
print("=" * 70)

# Query with metric parameter to get stats
try:
    response = requests.get(API_URL, params={'metric': 'sanction-list-stats'}, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        print(f"DEBUG: Response data: {data}")
        
        total_records = 0
        for source, count in data.items():
            print(f"\n{source:20s}: {count:,} records")
            total_records += count
        
        print("\n" + "=" * 70)
        print(f"TOTAL RECORDS: {total_records:,}")
        print("=" * 70)
    else:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
    print("\nNote: The admin metrics endpoint may not be available.")
    print("Trying alternative method...")
    
    # Alternative: Sample searches to estimate
    print("\n" + "=" * 70)
    print("ESTIMATING DATABASE SIZE VIA SAMPLE SEARCHES")
    print("=" * 70)
    
    sources = ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']
    
    for source in sources:
        try:
            # Search for wildcard to get total count
            response = requests.get(API_URL, params={'q': '*', 'source': source, 'limit': 1}, timeout=60)
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 'Unknown')
                print(f"\n{source:20s}: ~{count} records (estimated from search)")
        except Exception as e:
            print(f"\n{source:20s}: Error - {e}")
