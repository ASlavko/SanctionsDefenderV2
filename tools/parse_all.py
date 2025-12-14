"""
Runner script: parse EU and simple US files and write JSONL outputs to data/parsed/
"""
import os
import sys
# Ensure repo root is importable so `functions` package modules can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from functions.parse_eu import parse_eu_to_jsonl
from functions.parse_us_simple import parse_us_simple_to_jsonl
from functions.parse_uk import parse_uk_to_jsonl

BASE = os.path.join(os.path.dirname(__file__), '..')
SAN_DIR = os.path.join(BASE, 'data', 'sanctions')
PARSED_DIR = os.path.join(BASE, 'data', 'parsed')

os.makedirs(PARSED_DIR, exist_ok=True)

files = [
    (os.path.join(SAN_DIR, 'EU.xml'), os.path.join(PARSED_DIR, 'EU.jsonl'), 'EU'),
    (os.path.join(SAN_DIR, 'UK.xml'), os.path.join(PARSED_DIR, 'UK.jsonl'), 'UK'),
    (os.path.join(SAN_DIR, 'US_SDN_SIMPLE.xml'), os.path.join(PARSED_DIR, 'US_SDN_SIMPLE.jsonl'), 'US_SDN_SIMPLE'),
    (os.path.join(SAN_DIR, 'US_NON_SDN_SIMPLE.xml'), os.path.join(PARSED_DIR, 'US_NON_SDN_SIMPLE.jsonl'), 'US_NON_SDN_SIMPLE'),
]

for xml, out, src in files:
    if not os.path.exists(xml):
        print('Missing', xml)
        continue
    print(f'Parsing {xml} -> {out}')
    if src == 'EU':
        parse_eu_to_jsonl(xml, out)
    elif src == 'UK':
        parse_uk_to_jsonl(xml, out)
    else:
        parse_us_simple_to_jsonl(xml, out, src)
print('All done')
