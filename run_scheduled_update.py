import logging
import os
import sys
from dotenv import load_dotenv

# Configure logging
# We will log to both console and a file
log_file = "update_debug.log"

# Create a custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clear existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

# File Handler
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.updater import run_daily_update

if __name__ == "__main__":
    # Load env vars
    load_dotenv()
    
    print("!!! SCRIPT VERSION: 1.1 (With Debug Prints) !!!", flush=True)
    logger.info("Starting scheduled update script...")
    try:
        run_daily_update()
        logger.info("Scheduled update completed successfully.")
    except Exception as e:
        logger.error(f"Scheduled update failed: {e}", exc_info=True)
        raise
