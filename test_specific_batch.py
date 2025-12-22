import requests
import time
import os
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8008"
USERNAME = "admin"
PASSWORD = "admin123"
FILE_PATH = r"c:\Users\Slavko\SanctionDefenderApp\test_data\Sifrant partnejev - test8 - samo nazivi.xlsx"

def run_test():
    # 1. Login
    print(f"Logging in as {USERNAME}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": USERNAME,
            "password": PASSWORD
        })
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Login failed: {e}")
        sys.exit(1)
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Upload File
    if not os.path.exists(FILE_PATH):
        print(f"Error: File not found at {FILE_PATH}")
        return

    print(f"Uploading {FILE_PATH}...")
    try:
        with open(FILE_PATH, "rb") as f:
            # Ensure filename is encoded correctly for upload
            filename = os.path.basename(FILE_PATH)
            # Determine mime type based on extension
            mime_type = "text/csv" if filename.endswith(".csv") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            files = {"file": (filename, f, mime_type)}
            response = requests.post(f"{BASE_URL}/api/v1/batch/upload", headers=headers, files=files)
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Upload failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

    batch_id = response.json()["id"]
    print(f"Upload successful. Batch ID: {batch_id}")

    # 3. Poll for Status
    print("Waiting for processing...")
    start_time = time.time()
    status = "PROCESSING"
    for _ in range(300): # Wait up to 300 seconds
        try:
            response = requests.get(f"{BASE_URL}/api/v1/batch/{batch_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            batch_info = data['batch']
            status = batch_info['status']
            print(f"Status: {status}")
            
            if status in ["COMPLETED", "FAILED"]:
                break
            time.sleep(5)
        except Exception as e:
            print(f"Polling failed: {e}")
            break

    # 4. Get Results
    if status == "COMPLETED":
        end_time = time.time()
        duration = end_time - start_time
        print(f"Processing complete in {duration:.2f} seconds.")
        print(f"Total records: {batch_info['total_records']}")
        print(f"Flagged count: {batch_info['flagged_count']}")
        
        print("\n--- Matches Found ---")
        results = data.get('results', [])
        match_count = 0
        for res in results:
            if res['match_status'] != 'NO_MATCH':
                match_count += 1
                if match_count <= 10: # Show first 10 matches
                    print(f"Name: {res['input_name']} -> Status: {res['match_status']} (Score: {res['match_score']:.2f})")
        
        if match_count > 10:
            print(f"... and {match_count - 10} more matches.")
            
    else:
        print("Batch processing failed or timed out.")

if __name__ == "__main__":
    run_test()
