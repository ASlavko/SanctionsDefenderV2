
import firebase_admin
from firebase_admin import credentials, firestore
import json

if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'sanction-defender-firebase',
    })

db = firestore.client()

print("Checking 'import_sessions' collection...")
docs = db.collection('import_sessions').order_by('timestamp_start', direction=firestore.Query.DESCENDING).limit(1).stream()

for doc in docs:
    data = doc.to_dict()
    print(f"\nSession ID: {doc.id}")
    print(f"Status: {data.get('status')}")
    print(f"Error: {data.get('error')}")
    print(f"Stats: {json.dumps(data.get('statistics'), indent=2)}")
