"""
Real-world matching examples demonstrating the advanced algorithm improvements.
"""

from matching import NameMatcher

def example_comparisons():
    """Show before/after matching scores for common scenarios"""
    matcher = NameMatcher()
    
    print("\n" + "="*70)
    print("ADVANCED MATCHING ALGORITHM - REAL-WORLD EXAMPLES")
    print("="*70)
    
    # Example 1: International names with diacritics
    print("\n[EXAMPLE 1: Names with Diacritics]")
    query = "Jose Garcia"
    record = {
        'main_name': 'José García',
        'aliases': [],
        'entity_type': 'individual'
    }
    score = matcher.calculate_match_score(query, record, entity_type='individual')
    print(f"Query:  '{query}'")
    print(f"Record: '{record['main_name']}'")
    print(f"Score:  {score}%")
    print("→ Handles accent marks and diacritics perfectly")
    
    # Example 2: Typos and misspellings
    print("\n[EXAMPLE 2: Names with Typos]")
    query = "Vladmir Putin"  # Missing 'a' in Vladimir
    record = {
        'main_name': 'Vladimir Putin',
        'aliases': [],
        'entity_type': 'individual'
    }
    score = matcher.calculate_match_score(query, record, entity_type='individual')
    print(f"Query:  '{query}' (typo: missing 'a')")
    print(f"Record: '{record['main_name']}'")
    print(f"Score:  {score}%")
    print("→ Levenshtein distance catches single character typos")
    
    # Example 3: Names with suffixes and titles
    print("\n[EXAMPLE 3: Names with Titles & Suffixes]")
    query = "Dr. John Smith Jr."
    record = {
        'main_name': 'John Smith',
        'aliases': [],
        'entity_type': 'individual'
    }
    score = matcher.calculate_match_score(query, record, entity_type='individual')
    print(f"Query:  '{query}'")
    print(f"Record: '{record['main_name']}'")
    print(f"Score:  {score}%")
    print("→ Automatically removes titles and suffixes")
    
    # Example 4: Company names with business suffixes
    print("\n[EXAMPLE 4: Company Names]")
    query = "Apple"
    record = {
        'main_name': 'Apple Inc.',
        'aliases': [],
        'entity_type': 'company'
    }
    score = matcher.calculate_match_score(query, record, entity_type='company')
    print(f"Query:  '{query}'")
    print(f"Record: '{record['main_name']}'")
    print(f"Score:  {score}%")
    print("→ Removes business entity suffixes (Inc., Corp., Ltd., etc.)")
    
    # Example 5: Phonetically similar names
    print("\n[EXAMPLE 5: Phonetically Similar Names]")
    query = "Jon Smith"
    record = {
        'main_name': 'John Smith',
        'aliases': [],
        'entity_type': 'individual'
    }
    score = matcher.calculate_match_score(query, record, entity_type='individual')
    print(f"Query:  '{query}'")
    print(f"Record: '{record['main_name']}'")
    print(f"Score:  {score}%")
    print("→ Phonetic matching (Soundex) catches pronunciation-based variations")
    
    # Example 6: Partial names and aliases
    print("\n[EXAMPLE 6: Partial Names & Aliases]")
    query = "Vladimir Vladimirovich Putin"
    record = {
        'main_name': 'Vladimir Putin',
        'aliases': ['Vladimir Vladimirovich Putin'],
        'entity_type': 'individual'
    }
    score = matcher.calculate_match_score(query, record, entity_type='individual')
    print(f"Query:  '{query}' (full name with patronymic)")
    print(f"Record: '{record['main_name']}'")
    print(f"Alias:  '{record['aliases'][0]}'")
    print(f"Score:  {score}%")
    print("→ Matches against aliases for better coverage")
    
    # Example 7: Multiple tokens
    print("\n[EXAMPLE 7: Token-Based Matching]")
    query = "Smith, John"
    record = {
        'main_name': 'John Smith',
        'aliases': [],
        'entity_type': 'individual'
    }
    score = matcher.calculate_match_score(query, record, entity_type='individual')
    print(f"Query:  '{query}' (different word order)")
    print(f"Record: '{record['main_name']}'")
    print(f"Score:  {score}%")
    print("→ Token-based matching handles word order variations")
    
    # Example 8: International name formats
    print("\n[EXAMPLE 8: International Formats]")
    query = "Müller"
    record = {
        'main_name': 'Mueller',
        'aliases': [],
        'entity_type': 'individual'
    }
    score = matcher.calculate_match_score(query, record, entity_type='individual')
    print(f"Query:  '{query}' (German umlaut)")
    print(f"Record: '{record['main_name']}'")
    print(f"Score:  {score}%")
    print("→ Diacritic normalization: ü becomes u")
    
    # Example 9: False positive prevention
    print("\n[EXAMPLE 9: False Positive Prevention]")
    query = "John Smith"
    record = {
        'main_name': 'Jane Doe',
        'aliases': [],
        'entity_type': 'individual'
    }
    score = matcher.calculate_match_score(query, record, entity_type='individual')
    print(f"Query:  '{query}'")
    print(f"Record: '{record['main_name']}'")
    print(f"Score:  {score}%")
    print("→ No false matches on completely different names")
    
    print("\n" + "="*70)
    print("KEY FEATURES:")
    print("="*70)
    print("""
✓ Levenshtein Distance: Catches typos (edit distance ≤ 2)
✓ Soundex/Metaphone: Matches phonetically similar names
✓ Diacritic Normalization: José = Jose, Müller = Mueller
✓ Name Cleaning: Removes titles, suffixes, particles
✓ Company Normalization: Removes Inc., Corp., Ltd., etc.
✓ Alias Support: Checks multiple name variations
✓ Token Matching: Handles word order changes
✓ Multi-Language: Unicode support for international names
✓ Entity-Aware: Different rules for individuals vs companies
✓ Weighted Scoring: Combines multiple algorithms intelligently
    """)
    print("="*70 + "\n")

if __name__ == '__main__':
    example_comparisons()
