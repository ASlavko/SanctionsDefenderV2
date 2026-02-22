import requests

def test_api():
    base_url = "http://127.0.0.1:8001/api/v1/kpi/sanction-lists"
    
    print("Testing 1 Day Stats...")
    r1 = requests.get(f"{base_url}?days=1")
    us1 = next(item for item in r1.json() if item["source"] == "US")
    print(f"US Added (1d): {us1['records_added']}")
    
    print("\nTesting 7 Days Stats...")
    r7 = requests.get(f"{base_url}?days=7")
    us7 = next(item for item in r7.json() if item["source"] == "US")
    print(f"US Added (7d): {us7['records_added']}")
    
    if us7['records_added'] > us1['records_added']:
        print("\nSUCCESS: 7-day stats show more additions than 1-day stats.")
    else:
        print("\nWARNING: Counts are same. Check if there were any imports in the last 7 days.")

test_api()
