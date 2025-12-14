import os
import requests
import tempfile
import logging
from src.db.session import SessionLocal
from src.etl.loader import SanctionLoader
from src.api.services.engine import search_engine

logger = logging.getLogger(__name__)

SANCTIONS_LIST_URLS = {
    "EU": "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw",
    "UK": "https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.xml",
    "US": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.XML",
    "US_NON_SDN": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/CONSOLIDATED.XML"
}

def download_to_temp(url: str, suffix: str = ".xml") -> str:
    """
    Downloads a file from a URL to a temporary file.
    Returns the path to the temporary file.
    The caller is responsible for deleting the file.
    """
    try:
        # delete=False is required for Windows if we want to close and reopen it elsewhere
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, 'wb') as tmp:
            logger.info(f"Downloading {url} to {path}...")
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
        return path
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        # Try to clean up if partial file exists
        if 'path' in locals() and os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass
        raise

def run_daily_update():
    logger.info("Starting daily sanctions update...")
    temp_files = {}
    
    try:
        # 1. Download all files
        for key, url in SANCTIONS_LIST_URLS.items():
            try:
                temp_path = download_to_temp(url)
                temp_files[key] = temp_path
            except Exception as e:
                logger.error(f"Skipping {key} due to download error: {e}")

        if not temp_files:
            logger.error("No files downloaded. Aborting update.")
            return

        # 2. Run Import
        db = SessionLocal()
        try:
            loader = SanctionLoader(db)
            stats = loader.run_update(temp_files)
            logger.info(f"Update completed. Stats: {stats}")
            
            # 3. Reload Search Engine
            logger.info("Reloading in-memory search engine...")
            search_engine.load_data(db)
            logger.info("Search engine reloaded.")
            
        except Exception as e:
            logger.error(f"Error during database update: {e}")
        finally:
            db.close()

    finally:
        # 4. Cleanup Temp Files
        for path in temp_files.values():
            if os.path.exists(path):
                try:
                    os.unlink(path)
                    logger.info(f"Cleaned up temp file: {path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {path}: {e}")
