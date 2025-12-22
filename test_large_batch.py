import requests
import time
import os
import sys
import csv
import random

# Configuration
BASE_URL = "http://127.0.0.1:8012"
USERNAME = "admin"
PASSWORD = "admin123"
FILE_PATH = "large_test.csv"
NUM_RECORDS = 8000

KNOWN_SANCTIONED = [
    "Gazprom neft",
    "Sberbank",
    "VTB Bank",
    "Rosneft",
    "Iran Air",
    "Mahan Air",
    "Bank Mellat",
    "Islamic Revolutionary Guard Corps",
    "Hezbollah",
    "Hamas"
]

def generate_file():
    print(f"Generating {FILE_PATH} with {NUM_RECORDS} records...")
    with open(FILE_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # No header, as per the user's scenario
        
        for i in range(NUM_RECORDS):
            if i < len(KNOWN_SANCTIONED):
                name = KNOWN_SANCTIONED[i]
            else:
                name = f"Test Company {i}"
            writer.writerow([name])
    print("Generation complete.")

def run_test():
    # 0. Generate File
    generate_file()

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
    print(f"Uploading {FILE_PATH}...")
    try:
        with open(FILE_PATH, "rb") as f:
            files = {"file": (FILE_PATH, f, "text/csv")}
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
    for _ in range(600): # Wait up to 10 minutes
        try:
            response = requests.get(f"{BASE_URL}/api/v1/batch/{batch_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            batch_info = data['batch']
            status = batch_info['status']
            
            if status in ["COMPLETED", "FAILED"]:
                break
            time.sleep(2)
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
        
        # Calculate rate
        rate = batch_info['total_records'] / duration
        print(f"Processing Rate: {rate:.2f} records/second")
            
    else:
        print(f"Batch processing failed with status: {status}")

if __name__ == "__main__":
    run_test()
