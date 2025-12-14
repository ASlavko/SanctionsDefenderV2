import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os

# Add functions directory to path to import matching
sys.path.append(os.path.join(os.getcwd(), 'functions'))
from matching import NameMatcher

def debug_search():
    print("Initializing Firestore...")
    os.environ["GOOGLE_CLOUD_PROJECT"] = "sanction-defender-firebase"
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    query_text = "Putin"
    print(f"\n--- Debugging Search for '{query_text}' ---")
    
    # 1. Check Token Generation
    tokens = NameMatcher.generate_search_tokens(query_text)
    print(f"Generated Tokens: {tokens}")
    
    if not tokens:
        print("No tokens generated!")
        return

    search_token = max(tokens, key=len)
    print(f"Search Token used for query: '{search_token}'")

    # 2. Check Firestore Direct Query
    print(f"\nQuerying Firestore 'sanctions_entities' where 'search_tokens' array_contains '{search_token}'...")
    
    docs = db.collection('sanctions_entities')\
             .where('search_tokens', 'array_contains', search_token)\
             .limit(5)\
             .stream()
             
    found = False
    for doc in docs:
        found = True
        data = doc.to_dict()
        print(f"\nFound Document ID: {doc.id}")
        print(f"Name: {data.get('main_name')}")
        print(f"Search Tokens (first 10): {data.get('search_tokens', [])[:10]}")
        
    if not found:
        print("No documents found in Firestore with this token.")
    else:
        print("\nFirestore query successful.")

if __name__ == "__main__":
    debug_search()
