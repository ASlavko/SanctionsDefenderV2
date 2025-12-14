from matching import match_name

# Test cases for problem searches
test_records = [
    {'main_name': 'Rosneft', 'aliases': ['ROSNEFT OIL COMPANY'], 'entity_type': 'company'},
    {'main_name': 'Sberbank', 'aliases': ['SBERBANK OF RUSSIA', 'Sberbank Russia'], 'entity_type': 'company'},
]

queries = ['Resneft', 'Rosneft', 'Sbernak', 'Sberbank']

print("\n" + "="*60)
print("TESTING PROBLEM SEARCHES: Rosneft & Sberbank")
print("="*60)

for query in queries:
    print(f'\nQuery: "{query}"')
    for record in test_records:
        score = match_name(query, record, entity_type='company')
        status = "✓ MATCH" if score >= 50 else "✗ NO MATCH"
        print(f'  {status} vs {record["main_name"]}: {score}%')

print("\n" + "="*60)
