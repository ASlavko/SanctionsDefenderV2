import os
from google.cloud import logging
from google.cloud.logging import DESCENDING

# Set the project ID
project_id = "sanction-defender-firebase"
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

def fetch_logs():
    client = logging.Client(project=project_id)
    
    # Filter for the specific function
    # filter_str = 'logName="projects/sanction-defender-firebase/logs/search_api_debug"'
    # filter_str = 'resource.type="cloud_run_revision"'
    filter_str = 'resource.type="cloud_run_revision" AND timestamp >= "2025-12-13T07:00:00Z"'
    
    print(f"Fetching logs with filter: {filter_str}")
    
    # List entries
    entries = client.list_entries(
        filter_=filter_str,
        order_by=DESCENDING,
        max_results=100
    )
    
    print("--- Logs ---")
    for entry in entries:
        print(entry.to_api_repr())

if __name__ == "__main__":
    fetch_logs()
