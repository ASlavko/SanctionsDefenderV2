from src.services.updater import run_daily_update
import logging

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Testing daily update logic...")
    run_daily_update()
    print("Test complete.")
