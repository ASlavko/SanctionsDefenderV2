"""
Test cases for advanced name matching logic.
Tests cover: normalization, fuzzy matching, phonetic matching, and edge cases.
"""

import sys
sys.path.insert(0, '/functions')

from matching import NameMatcher, match_name


def test_name_normalization():
    """Test name normalization with diacritics and whitespace"""
    matcher = NameMatcher()
    
    test_cases = [
        ("José García", "jose garcia"),
        ("François Müller", "francois muller"),
        ("  John   Smith  ", "john smith"),
        ("Şukru Atalay", "sukru atalay"),
        ("Åsa Öberg", "asa oberg"),
    ]
    
    print("\n=== NAME NORMALIZATION ===")
    for input_name, expected in test_cases:
        result = matcher.normalize_name(input_name)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} | '{input_name}' -> '{result}' (expected: '{expected}')")


def test_prefix_suffix_removal():
    """Test removal of common name prefixes and suffixes"""
    matcher = NameMatcher()
    
    test_cases = [
        ("Dr. John Smith", "John Smith"),
        ("Juan Carlos Lopez Jr.", "Juan Carlos Lopez"),
        ("van Berg", "Berg"),
        ("Friedrich von Hayek", "Friedrich Hayek"),
        ("Maria de la Cruz Sr.", "Maria de la Cruz"),
    ]
    
    print("\n=== PREFIX/SUFFIX REMOVAL ===")
    for input_name, expected in test_cases:
        result = matcher.remove_prefixes_suffixes(input_name)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} | '{input_name}' -> '{result}' (expected: '{expected}')")


def test_company_normalization():
    """Test company name normalization"""
    matcher = NameMatcher()
    
    test_cases = [
        ("Apple Inc.", "apple"),
        ("Microsoft Corporation", "microsoft"),
        ("Samsung Ltd.", "samsung"),
        ("Sony AG", "sony"),
        ("Airbus S.A.S.", "airbus"),
    ]
    
    print("\n=== COMPANY NORMALIZATION ===")
    for input_name, expected in test_cases:
        result = matcher.normalize_company_name(input_name)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} | '{input_name}' -> '{result}' (expected: '{expected}')")


def test_levenshtein_distance():
    """Test Levenshtein distance calculation"""
    matcher = NameMatcher()
    
    test_cases = [
        ("smith", "smith", 0),      # Identical
        ("smith", "smyth", 1),      # 1 substitution
        ("smith", "smiths", 1),     # 1 insertion
        ("smith", "smith ", 1),     # 1 insertion (space)
        ("john", "jahn", 1),        # 1 substitution
    ]
    
    print("\n=== LEVENSHTEIN DISTANCE ===")
    for s1, s2, expected_dist in test_cases:
        distance = matcher.levenshtein_distance(s1, s2)
        status = "PASS" if distance == expected_dist else "FAIL"
        print(f"{status} | '{s1}' <-> '{s2}': distance={distance} (expected: {expected_dist})")


def test_levenshtein_ratio():
    """Test Levenshtein similarity ratio"""
    matcher = NameMatcher()
    
    test_cases = [
        ("smith", "smith", 100),    # Identical = 100%
        ("smith", "smyth", 80),     # Very similar
        ("john", "jahn", 75),       # Similar
    ]
    
    print("\n=== LEVENSHTEIN RATIO ===")
    for s1, s2, expected_min in test_cases:
        ratio = matcher.levenshtein_ratio(s1, s2)
        status = "PASS" if ratio >= expected_min - 5 else "FAIL"  # Allow 5% tolerance
        print(f"{status} | '{s1}' <-> '{s2}': ratio={ratio:.1f}% (expected: ~{expected_min}%)")


def test_soundex():
    """Test Soundex phonetic encoding"""
    matcher = NameMatcher()
    
    test_cases = [
        ("Smith", "S530"),
        ("Smyth", "S530"),          # Same as Smith
        ("Johnson", "J525"),
        ("Jonson", "J525"),         # Same as Johnson
        ("Robert", "R163"),
        ("Rupert", "R163"),         # Same as Robert
        ("Mueller", "M460"),
        ("Miller", "M460"),         # Similar phonetic to Mueller
    ]
    
    print("\n=== SOUNDEX ENCODING ===")
    for name, expected_code in test_cases:
        code = matcher.soundex(name)
        status = "PASS" if code == expected_code else "FAIL"
        print(f"{status} | {name:15} -> {code} (expected: {expected_code})")


def test_token_overlap():
    """Test token-based matching"""
    matcher = NameMatcher()
    
    test_cases = [
        ("john smith", "john smith", 100),  # Identical tokens
        ("john smith", "smith john", 100),  # Same tokens, different order
        ("john smith", "john", 50),         # Partial overlap
        ("john smith", "jane doe", 0),      # No overlap
    ]
    
    print("\n=== TOKEN OVERLAP ===")
    for s1, s2, expected_score in test_cases:
        score = matcher.token_overlap(s1, s2)
        status = "PASS" if score == expected_score else "FAIL"
        print(f"{status} | '{s1}' <-> '{s2}': {score:.1f}% (expected: {expected_score}%)")


def test_comprehensive_matching():
    """Test the comprehensive matching algorithm"""
    matcher = NameMatcher()
    
    # Test records
    test_cases = [
        {
            'query': 'Putin',
            'record': {
                'main_name': 'Vladimir Putin',
                'aliases': [],
                'entity_type': 'individual'
            },
            'expected_min': 75,
            'description': 'Partial name match'
        },
        {
            'query': 'Vladimir Putin',
            'record': {
                'main_name': 'Vladimir Putin',
                'aliases': [],
                'entity_type': 'individual'
            },
            'expected_min': 99,
            'description': 'Exact name match'
        },
        {
            'query': 'Vladmir Putin',  # Typo: 'Vladmir' instead of 'Vladimir'
            'record': {
                'main_name': 'Vladimir Putin',
                'aliases': [],
                'entity_type': 'individual'
            },
            'expected_min': 75,
            'description': 'Name with typo'
        },
        {
            'query': 'Vladimir Vladimirovich Putin',
            'record': {
                'main_name': 'Vladimir Putin',
                'aliases': ['Vladimir Vladimirovich Putin'],
                'entity_type': 'individual'
            },
            'expected_min': 95,
            'description': 'Name with patronymic (alias)'
        },
        {
            'query': 'Apple',
            'record': {
                'main_name': 'Apple Inc.',
                'aliases': [],
                'entity_type': 'company'
            },
            'expected_min': 85,
            'description': 'Company name without suffix'
        },
        {
            'query': 'Jose Garcia',
            'record': {
                'main_name': 'José García',
                'aliases': [],
                'entity_type': 'individual'
            },
            'expected_min': 80,
            'description': 'Name with diacritics'
        },
        {
            'query': 'John Smith Sr.',
            'record': {
                'main_name': 'John Smith',
                'aliases': [],
                'entity_type': 'individual'
            },
            'expected_min': 80,
            'description': 'Query with suffix'
        },
    ]
    
    print("\n=== COMPREHENSIVE MATCHING ===")
    for i, test in enumerate(test_cases, 1):
        score = matcher.calculate_match_score(
            test['query'],
            test['record'],
            entity_type=test['record']['entity_type']
        )
        status = "PASS" if score >= test['expected_min'] else "FAIL"
        print(f"{status} | Test {i}: {test['description']}")
        print(f"   Query: '{test['query']}'")
        print(f"   Record: '{test['record']['main_name']}'")
        print(f"   Score: {score:.1f}% (expected: >{test['expected_min']}%)")


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    matcher = NameMatcher()
    
    test_cases = [
        {
            'query': '',
            'record': {'main_name': 'John Smith', 'aliases': []},
            'description': 'Empty query'
        },
        {
            'query': 'John',
            'record': {'main_name': '', 'aliases': []},
            'description': 'Empty record name'
        },
        {
            'query': '123',
            'record': {'main_name': 'John Smith', 'aliases': []},
            'description': 'Numeric query'
        },
        {
            'query': 'A',
            'record': {'main_name': 'John Smith', 'aliases': []},
            'description': 'Single character query'
        },
    ]
    
    print("\n=== EDGE CASES ===")
    for test in test_cases:
        try:
            score = matcher.calculate_match_score(test['query'], test['record'])
            print(f"PASS | {test['description']}: score={score:.1f}%")
        except Exception as e:
            print(f"FAIL | {test['description']}: ERROR - {str(e)}")


def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("ADVANCED MATCHING LOGIC TEST SUITE")
    print("=" * 60)
    
    test_name_normalization()
    test_prefix_suffix_removal()
    test_company_normalization()
    test_levenshtein_distance()
    test_levenshtein_ratio()
    test_soundex()
    test_token_overlap()
    test_comprehensive_matching()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()
