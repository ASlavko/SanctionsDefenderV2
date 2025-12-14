from matching import match_name

# Test cases
test_records = [
    {'main_name': 'Rosneft', 'aliases': ['ROSNEFT OIL COMPANY'], 'entity_type': 'company'},
    {'main_name': 'Sberbank', 'aliases': ['SBERBANK OF RUSSIA', 'Sberbank Russia'], 'entity_type': 'company'},
]

queries = ['Resneft', 'Rosneft', 'Sbernak', 'Sberbank']

for query in queries:
    print(f'\nQuery: "{query}"')
    for record in test_records:
        score = match_name(query, record, entity_type='company')
        print(f'  vs {record["main_name"]}: {score}%')
