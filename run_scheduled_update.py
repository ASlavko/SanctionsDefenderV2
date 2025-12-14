import logging
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.updater import run_daily_update

# Setup logging to file
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scheduler.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
