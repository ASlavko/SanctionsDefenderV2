import requests
import json

API_URL = "https://europe-west1-sanction-defender-firebase.cloudfunctions.net/search_sanctions"

def test_search():
    # Search for "Putin" - should definitely exist
    params = {
        "q": "Putin",
        "limit": 5
    }
    
    print(f"Testing Search API: {API_URL}")
    try:
        response = requests.get(API_URL, params=params, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Matches Found: {data.get('count')}")
            
            matches = data.get('matches', [])
            if matches:
                print("\nTop Match:")
                print(json.dumps(matches[0], indent=2))
                return True
            else:
                print("No matches found.")
                return False
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    test_search()
