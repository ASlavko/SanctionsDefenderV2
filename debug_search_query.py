import firebase_admin
from firebase_admin import firestore
import sys
import os

# Add functions directory to path to import matching
sys.path.append(os.path.join(os.getcwd(), 'functions'))
from matching import NameMatcher

def debug_search(query_text):
    print(f"Initializing Firestore...")
    if not firebase_admin._apps:
        # Use Application Default Credentials
        cred = firebase_admin.credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {'projectId': 'sanction-defender-firebase'})
    db = firestore.client()

    print(f"Query: '{query_text}'")
    
    # Generate tokens
    tokens = NameMatcher.generate_search_tokens(query_text)
    print(f"Tokens: {tokens}")
    
    if not tokens:
        print("No tokens generated.")
        return

    search_token = max(tokens, key=len)
    print(f"Using search_token: '{search_token}'")

    # Query
    collection_ref = db.collection('sanctions_entities')
    q = collection_ref.where('search_tokens', 'array_contains', search_token).limit(10)
    
    print("Executing query...")
    docs = list(q.stream())
    print(f"Found {len(docs)} documents.")
    
    for doc in docs:
        data = doc.to_dict()
        print(f"ID: {doc.id}, Name: {data.get('main_name')}, Source: {data.get('sanction_source')}")
        print(f"Search Tokens (first 10): {data.get('search_tokens', [])[:10]}")

if __name__ == "__main__":
    # Test with a known entity name, e.g., "Putin" or "Sberbank" or "Rosneft"
    # Based on previous context, "Rosneft" was used in tests.
    debug_search("Rosneft")
