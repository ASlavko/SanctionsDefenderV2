import os
from src.db.session import SessionLocal, engine, Base
from src.etl.loader import SanctionLoader
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Ensure tables exist
    logger.info("Checking database schema...")
    Base.metadata.create_all(bind=engine)
    
    # Define paths to data files
    # Assuming data is in data/sanctions/ relative to project root
    base_path = os.path.join(os.getcwd(), "data", "sanctions")
    
    files = {
        "EU": os.path.join(base_path, "EU.xml"),
        "UK": os.path.join(base_path, "UK.xml"),
        "US": os.path.join(base_path, "US_SDN_SIMPLE.xml")
    }
    
    # Validate files exist
    valid_files = {}
    for key, path in files.items():
        if os.path.exists(path):
            valid_files[key] = path
        else:
            logger.warning(f"File not found for {key}: {path}")
    
    if not valid_files:
        logger.error("No valid data files found. Aborting import.")
        return

    # Run Import
    db = SessionLocal()
    try:
        loader = SanctionLoader(db)
        stats = loader.run_update(valid_files)
        logger.info("Import Summary:")
        logger.info(f"  New Records: {stats['new']}")
        logger.info(f"  Updated Records: {stats['updated']}")
        logger.info(f"  Marked Inactive: {stats['inactive']}")
    except Exception as e:
        logger.error(f"Import failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
