import json

# Check one of the overlapping entities
sdn_data = [json.loads(line) for line in open('data/parsed/US_SDN_SIMPLE.jsonl')]
nonsdn_data = [json.loads(line) for line in open('data/parsed/US_NON_SDN_SIMPLE.jsonl')]

# Find 'STAUT COMPANY LIMITED'
sdn_staut = [r for r in sdn_data if 'STAUT' in r.get('main_name', '')]
nonsdn_staut = [r for r in nonsdn_data if 'STAUT' in r.get('main_name', '')]

print('STAUT COMPANY LIMITED in SDN_SIMPLE:')
if sdn_staut:
    print(f'  ID: {sdn_staut[0]["id"]}')
    print(f'  Unique Sanction ID: {sdn_staut[0]["unique_sanction_id"]}')
    print(f'  Entity Type: {sdn_staut[0]["entity_type"]}')
    print(f'  Name: {sdn_staut[0]["main_name"]}')
else:
    print('  Not found')

print('\nSTAUT COMPANY LIMITED in NON_SDN_SIMPLE:')
if nonsdn_staut:
    print(f'  ID: {nonsdn_staut[0]["id"]}')
    print(f'  Unique Sanction ID: {nonsdn_staut[0]["unique_sanction_id"]}')
    print(f'  Entity Type: {nonsdn_staut[0]["entity_type"]}')
    print(f'  Name: {nonsdn_staut[0]["main_name"]}')
else:
    print('  Not found')

print('\n' + '='*60)
print('Are they the same record (same unique_sanction_id)?')
if sdn_staut and nonsdn_staut:
    same_id = sdn_staut[0]["unique_sanction_id"] == nonsdn_staut[0]["unique_sanction_id"]
    print(f'  {same_id}')
    if same_id:
        print(f'  YES - This entity appears on BOTH sanction lists (legitimate overlap)')
    else:
        print(f'  NO - These are different entities with the same name')
