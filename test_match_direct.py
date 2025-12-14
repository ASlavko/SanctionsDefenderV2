#!/usr/bin/env python3
"""
Debug script to test the matching algorithm directly against a Sberbank record
"""

import sys
import os

# Add functions directory to path to import matching module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions'))

from matching import match_name

# Create a test record similar to what's in Firestore for Sberbank
test_record = {
    'id': 'EU_EU.8537.32',
    'main_name': 'PUBLIC JOINT STOCK COMPANY SBERBANK OF RUSSIA',
    'aliases': [
        'SBERBANK ROSSII',
        'SBERBANK ROSSII OAO',
        'SBERBANK OF RUSSIA',
        'PJSC SBERBANK',
    ],
    'entity_type': 'company',
    'country': 'Russia',
    'sanction_source': 'EU'
}

print("=" * 70)
print("TESTING MATCH_NAME FUNCTION DIRECTLY")
print("=" * 70)

test_queries = [
    "Sberbank",
    "sberbank",
    "SBERBANK",
    "SBERBANK OF RUSSIA",
    "PUBLIC JOINT STOCK COMPANY SBERBANK OF RUSSIA",
    "PJSC SBERBANK",
    "SBERBANK ROSSII",
    "Sbernak",  # Typo
    "Sber",
]

for query in test_queries:
    score = match_name(query, test_record, entity_type='company', use_phonetic=True)
    print(f"\nQuery: '{query}'")
    print(f"Score: {score}%")
    print(f"Match: {'✓ YES' if score > 0 else '✗ NO'}")

print("\n" + "=" * 70)
print("Testing 'SBERBANK OF RUSSIA' against the whole record:")
print("=" * 70)

# Now test to see intermediate steps
from matching import get_matcher

matcher = get_matcher()
query = "SBERBANK OF RUSSIA"

# Normalize
query_normalized = matcher.normalize_name(query)
query_clean = matcher.remove_prefixes_suffixes(query_normalized)
query_clean = matcher.normalize_company_name(query_clean)

main_normalized = matcher.normalize_name(test_record['main_name'])
main_clean = matcher.remove_prefixes_suffixes(main_normalized)
main_clean = matcher.normalize_company_name(main_clean)

print(f"\nQuery original: '{query}'")
print(f"Query normalized: '{query_normalized}'")
print(f"Query cleaned: '{query_clean}'")

print(f"\nMain name original: '{test_record['main_name']}'")
print(f"Main name normalized: '{main_normalized}'")
print(f"Main name cleaned: '{main_clean}'")

# Check specific matches
print(f"\nExact match (normalized): {query_normalized == main_normalized}")
print(f"Exact match (cleaned): {query_clean == main_clean}")

# Substring check
lev_ratio = matcher.levenshtein_ratio(query_clean, main_clean)
print(f"Levenshtein ratio: {lev_ratio}%")

# Token overlap
token_score = matcher.token_overlap(query_clean, main_clean)
print(f"Token overlap: {token_score}%")

# Final score
score = match_name(query, test_record, entity_type='company', use_phonetic=True)
print(f"\nFinal score: {score}%")
