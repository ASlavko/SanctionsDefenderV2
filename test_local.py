"""
Local test script to run the download_sanctions_lists function
without needing Firebase emulator or cloud infrastructure.
"""
import sys
from datetime import datetime
from functions.main import download_sanctions_lists

# Create a mock cloud event object
class MockCloudEvent:
    def __init__(self):
        self.data = {}
        self.event_id = "test-event-123"
        self.event_type = "test"
        self.timestamp = datetime.now().isoformat()

if __name__ == "__main__":
    print("=" * 70)
    print("Testing Sanctions List Download Function Locally")
    print("=" * 70)
    
    mock_event = MockCloudEvent()
    
    try:
        result = download_sanctions_lists(mock_event)
        print("\n" + "=" * 70)
        print("FUNCTION COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Result: {result}")
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
