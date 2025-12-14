import logging
import os
import sys
from dotenv import load_dotenv

# Configure logging IMMEDIATELY, before any imports
# Use force=True to override any other config
# Log to stdout so GitHub Actions captures it
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.updater import run_daily_update

if __name__ == "__main__":
    # Load env vars
    load_dotenv()
    
    logging.info("Starting scheduled update script...")
    try:
        run_daily_update()
        logging.info("Scheduled update completed successfully.")
    except Exception as e:
        logging.error(f"Scheduled update failed: {e}")
        raise
