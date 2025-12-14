
import firebase_admin
from firebase_admin import credentials, firestore
import sys

print("Initializing...")
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'sanction-defender-firebase',
    })

db = firestore.client()

print("Checking for search_tokens in 'sanctions_entities' collection...")
try:
    docs = db.collection('sanctions_entities').limit(5).stream()
    
    count = 0
    for doc in docs:
        count += 1
        data = doc.to_dict()
        print(f"\nDocument ID: {doc.id}")
        print(f"Name: {data.get('main_name')}")
        tokens = data.get('search_tokens')
        if tokens:
            print(f"Search Tokens: {tokens[:10]} ... (Total: {len(tokens)})")
        else:
            print("Search Tokens: [MISSING]")
            
    if count == 0:
        print("No documents found in 'sanctions' collection.")
        
except Exception as e:
    print(f"Error: {e}")
