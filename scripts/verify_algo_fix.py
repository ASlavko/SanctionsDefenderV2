
import requests
import json

def verify_putin():
    url = "http://localhost:8001/api/v1/single_screening/"
    payload = {
        "search_term": "vladimir putin",
        "threshold": 80
    }
    
    print(f"Testing search for: '{payload['search_term']}'")
    try:
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            matches = resp.json().get("matches", [])
            print(f"Found {len(matches)} matches.")
            for m in matches:
                name = m.get("record", {}).get("original_name")
                score = m.get("score")
                print(f"- Match: {name} (Score: {score:.1f}%)")
        else:
            print(f"Error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    verify_putin()
