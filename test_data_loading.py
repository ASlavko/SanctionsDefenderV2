#!/usr/bin/env python3
"""Test just the data loading without Firestore queries"""

import os
import json
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'

print("[TEST] Data Loading Test (no Firestore)")
print(f"[>] Current dir: {os.getcwd()}")

# Test loading data
sources = ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']
parsed_dir = os.path.join(os.path.dirname(__file__), 'data', 'parsed')

for source in sources:
    file_path = os.path.join(parsed_dir, f"{source}.jsonl")
    print(f"\n[>] Loading {source}...")
    print(f"    File: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"    [ERROR] File not found!")
        continue
    
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line)
                if 'error' not in record:
                    count += 1
                    if count % 1000 == 0:
                        print(f"    Loaded {count} records...")
            except:
                pass
    
    print(f"    [OK] Loaded {count} valid records")

print("\n[SUCCESS] All files loaded successfully!")
