from sqlalchemy.orm import Session
from src.db.models import SanctionRecord, MatchDecision, ImportLog, ChangeLog
from src.etl.parsers import EUParser, UKParser, USParser
from src.core.matching import NameMatcher
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SanctionLoader:
    def __init__(self, db: Session):
        self.db = db
        self.parsers = {
            "EU": EUParser(),
            "UK": UKParser(),
            "US": USParser(),
            "US_NON_SDN": USParser()
        }

    def run_update(self, file_paths: dict):
        """
        file_paths: dict like {"EU": "path/to/eu.xml", "UK": "path/to/uk.xml", ...}
        """
        logger.info("Starting Sanctions Update...")
        
        # 1. Load all current active IDs from DB to track what's missing
        # Map ID -> SanctionRecord object
        current_records = {
            r.id: r for r in self.db.query(SanctionRecord).filter(SanctionRecord.is_active == True).all()
        }
        
        seen_ids = set()
        
        # Initialize ImportLogs for each source
        import_logs = {}
        for list_type in file_paths.keys():
            log = ImportLog(
                source=list_type,
                status="IN_PROGRESS",
                timestamp=datetime.utcnow()
            )
            self.db.add(log)
            self.db.flush() # Get ID
            import_logs[list_type] = log

        # 2. Process each source
        for list_type, file_path in file_paths.items():
            parser = self.parsers.get(list_type)
            if not parser:
                logger.warning(f"No parser for {list_type}")
                continue
                
            logger.info(f"Processing {list_type} from {file_path}...")
            current_log = import_logs[list_type]
            
            try:
                for record_dict in parser.parse(file_path):
                    record_id = record_dict["id"]
                    seen_ids.add(record_id)
                    
                    normalized_name = NameMatcher.normalize_name(record_dict.get("original_name", ""))
                    
                    if record_id in current_records:
                        # Update existing
                        existing = current_records[record_id]
                        
                        # Check for changes
                        changes = []
                        fields_to_check = [
                            ("original_name", record_dict.get("original_name")),
                            ("entity_type", record_dict.get("entity_type")),
                            ("gender", record_dict.get("gender")),
                            ("url", record_dict.get("url")),
                            ("un_id", record_dict.get("un_id")),
                            ("remark", record_dict.get("remark")),
                            ("function", record_dict.get("function")),
                            ("program", record_dict.get("program")),
                            ("nationality", record_dict.get("nationality")),
                            ("birth_date", record_dict.get("birth_date"))
                        ]
                        
                        is_changed = False
                        for field, new_val in fields_to_check:
                            old_val = getattr(existing, field)
                            # Simple equality check (handle None vs "")
                            if (old_val or "") != (new_val or ""):
                                is_changed = True
                                changes.append((field, old_val, new_val))
                                setattr(existing, field, new_val)
                        
                        # Always update normalized name if original changed
                        if existing.normalized_name != normalized_name:
                            existing.normalized_name = normalized_name
                            # We don't necessarily log normalized name change as it's derived
                        
                        # Update alias_names if changed
                        if existing.alias_names != record_dict.get("alias_names"):
                            is_changed = True
                            # changes.append(("alias_names", "...", "...")) # Too verbose to log full JSON diff?
                            existing.alias_names = record_dict.get("alias_names")

                        if is_changed:
                            existing.last_updated = datetime.utcnow()
                            existing.last_seen = datetime.utcnow()
                            current_log.records_updated += 1
                            
                            # Log changes
                            for field, old_v, new_v in changes:
                                change_log = ChangeLog(
                                    import_log_id=current_log.id,
                                    record_id=record_id,
                                    change_type="UPDATED",
                                    field_changed=field,
                                    old_value=str(old_v) if old_v else None,
                                    new_value=str(new_v) if new_v else None
                                )
                                self.db.add(change_log)
                        else:
                            existing.last_seen = datetime.utcnow()
                            
                    else:
                        # Insert new
                        new_record = SanctionRecord(
                            id=record_id,
                            list_type=list_type,
                            original_name=record_dict["original_name"],
                            normalized_name=normalized_name,
                            alias_names=record_dict.get("alias_names"),
                            program=record_dict.get("program"),
                            nationality=record_dict.get("nationality"),
                            birth_date=record_dict.get("birth_date"),
                            entity_type=record_dict.get("entity_type"),
                            gender=record_dict.get("gender"),
                            url=record_dict.get("url"),
                            un_id=record_dict.get("un_id"),
                            remark=record_dict.get("remark"),
                            function=record_dict.get("function"),
                            is_active=True,
                            first_seen=datetime.utcnow(),
                            last_seen=datetime.utcnow()
                        )
                        self.db.add(new_record)
                        current_log.records_added += 1
                        
                        # Log Addition
                        change_log = ChangeLog(
                            import_log_id=current_log.id,
                            record_id=record_id,
                            change_type="ADDED",
                            new_value=f"Name: {record_dict.get('original_name')}"
                        )
                        self.db.add(change_log)
            
            except Exception as e:
                logger.error(f"Error processing {list_type}: {e}")
                current_log.status = "FAILED"
                current_log.error_message = str(e)
        
        # 3. Mark missing as inactive
        # We need to attribute removals to the correct source log
        for record_id, record in current_records.items():
            if record_id not in seen_ids:
                record.is_active = False
                record.last_updated = datetime.utcnow()
                
                # Find which log this belongs to
                # If we have a log for this record's list_type, use it
                if record.list_type in import_logs:
                    log = import_logs[record.list_type]
                    log.records_removed += 1
                    
                    change_log = ChangeLog(
                        import_log_id=log.id,
                        record_id=record_id,
                        change_type="REMOVED",
                        old_value=f"Name: {record.original_name}"
                    )
                    self.db.add(change_log)
                else:
                    # If we are not updating this source today, we shouldn't mark it inactive?
                    # But run_update assumes we are updating everything provided in file_paths.
                    # If file_paths covers all sources, this is fine.
                    pass

        # Finalize logs
        total_new = 0
        total_updated = 0
        total_inactive = 0
        
        for log in import_logs.values():
            if log.status == "IN_PROGRESS":
                log.status = "SUCCESS"
            total_new += log.records_added
            total_updated += log.records_updated
            total_inactive += log.records_removed

        self.db.commit()
        logger.info(f"Update Complete. New: {total_new}, Updated: {total_updated}, Inactive: {total_inactive}")
        return {
            "new": total_new,
            "updated": total_updated,
            "inactive": total_inactive
        }
