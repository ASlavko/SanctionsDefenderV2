#!/usr/bin/env python3
"""
Two-stage sanctions data update with comprehensive audit logging.

Stage 1: VALIDATION
- Load new data from source files
- Validate data integrity (no duplicates, required fields, etc.)
- Compare with existing Firestore data
- Generate detailed change report (added, updated, removed)
- Create audit log entries

Stage 2: COMMIT
- Execute the changes (only if validation passed)
- Record transaction IDs and timestamps
- Update metadata (last import date, etc.)
- Generate summary report

This ensures:
1. No data corruption from failed imports
2. Complete audit trail for compliance
3. Ability to detect and handle removed entities
4. Transaction safety
"""

import os
import json
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import hashlib
from matching import NameMatcher  # Import NameMatcher for token generation

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    print(f"[>] Current working directory: {os.getcwd()}")
    print(f"[>] Script directory: {os.path.dirname(os.path.abspath(__file__))}")

    # Clear emulator-related environment variables to avoid writing to emulator in CF runtime
    for env_var in ['FIRESTORE_EMULATOR_HOST', 'FIRESTORE_PROJECT_ID', 'GCLOUD_PROJECT']:
        if os.environ.get(env_var):
            print(f"[>] Clearing emulator env var {env_var}={os.environ.get(env_var)}")
            os.environ.pop(env_var, None)

    # Initialize Firebase Admin SDK using the active project from the runtime
    # to avoid accidentally pointing at a different project via local files.
    if not firebase_admin._apps:
        cred = None
        cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

        if cred_path:
            print(f"[>] Using GOOGLE_APPLICATION_CREDENTIALS: {cred_path}")
            try:
                with open(cred_path, 'r') as f:
                    cred_data = json.load(f)
                    if cred_data.get('type') == 'service_account':
                        cred = credentials.Certificate(cred_path)
                    else:
                        print("[>] Detected user credentials, using ApplicationDefault")
                        cred = credentials.ApplicationDefault()
            except Exception as e:
                print(f"[!] Error reading credentials file: {e}, falling back to ApplicationDefault")
                cred = credentials.ApplicationDefault()

        if cred:
            firebase_admin.initialize_app(cred, options={'projectId': 'sanction-defender-firebase'})
        else:
            print("[>] Using Application Default Credentials (gcloud/CF runtime)")
            firebase_admin.initialize_app(options={'projectId': 'sanction-defender-firebase'})

    db = firestore.client()
    try:
        app = firebase_admin.get_app()
        print(f"[OK] Connected to Firestore (project: {getattr(app, 'project_id', 'unknown')})")
    except Exception:
        print("[OK] Connected to Firestore")

    # Debug marker to confirm module init wrote to expected project
    try:
        db.collection('_debug_imports').document('module_init').set({
            'ts': datetime.utcnow().isoformat(),
            'source': 'import_sanctions_two_stage',
            'project': getattr(firebase_admin.get_app(), 'project_id', 'unknown')
        })
        print("[OK] Wrote module_init debug marker")
    except Exception as dbg_err:
        print(f"[WARN] Could not write module_init debug marker: {dbg_err}")

except Exception as e:
    print(f"[X] Firebase initialization failed: {e}")
    print(f"[X] Make sure GOOGLE_APPLICATION_CREDENTIALS env var is set or you have gcloud authenticated")
    sys.exit(1)


class SanctionsDataValidator:
    """Validates and compares sanctions data"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.required_fields = ['id', 'sanction_source', 'main_name', 'entity_type']
    
    def validate_record(self, record: Dict, line_num: int, source: str) -> bool:
        """Validate a single record"""
        # Check required fields
        for field in self.required_fields:
            if field not in record or not record[field]:
                self.errors.append(f"Line {line_num} ({source}): Missing required field '{field}'")
                return False
        
        # Verify source matches filename
        if record.get('sanction_source') != source:
            self.errors.append(
                f"Line {line_num} ({source}): Record has sanction_source='{record.get('sanction_source')}' "
                f"but expected '{source}'"
            )
            return False
        
        # Entity type must be valid
        if record.get('entity_type') not in ['company', 'individual']:
            self.errors.append(
                f"Line {line_num} ({source}): Invalid entity_type '{record.get('entity_type')}' "
                f"(must be 'company' or 'individual')"
            )
            return False
        
        return True
    
    def load_source_data(self, source_name: str, file_path: str) -> Dict[str, Dict]:
        """Load and validate data from a single source file"""
        records = {}
        
        if not os.path.exists(file_path):
            self.errors.append(f"File not found: {file_path}")
            return records
        
        print(f"\n[>] Loading {source_name} from {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Show progress every 1000 lines
                if line_num % 1000 == 0:
                    print(f"    Processing line {line_num}...")
                
                try:
                    record = json.loads(line)
                    
                    # Skip error records
                    if 'error' in record:
                        continue
                    
                    # Validate record
                    if not self.validate_record(record, line_num, source_name):
                        continue
                    
                    # Generate search tokens for indexed search
                    main_name = record.get('main_name', '')
                    aliases = record.get('aliases', [])
                    
                    # Collect all searchable text
                    search_text = [main_name] + aliases
                    all_tokens = set()
                    
                    for text in search_text:
                        tokens = NameMatcher.generate_search_tokens(text)
                        all_tokens.update(tokens)
                    
                    # Add tokens to record
                    record['search_tokens'] = list(all_tokens)
                    
                    # Check for duplicate IDs within the file
                    rec_id = record.get('id')
                    if rec_id in records:
                        self.warnings.append(
                            f"Duplicate ID in {source_name}: '{rec_id}' "
                            f"(line {line_num}, previously at line {records[rec_id].get('_line_num')})"
                        )
                        continue  # Skip duplicate
                    
                    record['_line_num'] = line_num
                    records[rec_id] = record
                
                except json.JSONDecodeError as e:
                    self.errors.append(f"Line {line_num} ({source_name}): Invalid JSON: {e}")
        
        print(f"   [OK] Loaded {len(records)} valid records")
        return records


class SanctionsDataComparator:
    """Compares new data with existing Firestore data"""
    
    def __init__(self, db):
        self.db = db
    
    def get_existing_data(self, source: str) -> Dict[str, Dict]:
        """Fetch all existing records for a source from Firestore"""
        print(f"\n[>] Fetching existing {source} data from Firestore...")
        
        records = {}
        query = self.db.collection('sanctions_entities').where('sanction_source', '==', source)
        
        doc_count = 0
        for doc in query.stream():
            doc_count += 1
            if doc_count % 500 == 0:
                print(f"    Downloaded {doc_count} documents...")
            data = doc.to_dict()
            doc_id = data.get('id')
            records[doc_id] = data
        
        print(f"   [OK] Found {len(records)} existing records")
        return records
    
    def compute_record_hash(self, record: Dict) -> str:
        """Compute hash of record content (excluding metadata fields)"""
        # Remove metadata fields from hash calculation
        fields_to_hash = {k: v for k, v in record.items() 
                         if k not in ['_line_num', '_hash', '_imported_at', 'id']}
        
        content = json.dumps(fields_to_hash, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def compare(self, new_data: Dict, existing_data: Dict, source: str) -> Dict:
        """Compare new data with existing data and generate change report"""
        
        print(f"\n[>] Comparing {source} data...")
        
        new_ids = set(new_data.keys())
        existing_ids = set(existing_data.keys())
        
        report = {
            'source': source,
            'new_ids': new_ids,
            'existing_ids': existing_ids,
            'added': {},      # New records
            'updated': {},    # Modified records
            'unchanged': {},  # Same records
            'removed': {},    # Deleted records
        }
        
        # Find added records
        for rec_id in new_ids - existing_ids:
            report['added'][rec_id] = new_data[rec_id]
        
        # Find updated and unchanged records
        for idx, rec_id in enumerate(new_ids & existing_ids, 1):
            if idx % 1000 == 0:
                print(f"    Compared {idx} overlapping records...")
            new_record = new_data[rec_id]
            existing_record = existing_data[rec_id]
            
            new_hash = self.compute_record_hash(new_record)
            existing_hash = self.compute_record_hash(existing_record)
            
            if new_hash != existing_hash:
                report['updated'][rec_id] = {
                    'old': existing_record,
                    'new': new_record,
                    'changed_fields': self._detect_changes(existing_record, new_record)
                }
            else:
                report['unchanged'][rec_id] = existing_record
        
        # Find removed records
        for idx, rec_id in enumerate(existing_ids - new_ids, 1):
            if idx % 1000 == 0:
                print(f"    Processed {idx} removals...")
            report['removed'][rec_id] = existing_data[rec_id]
        
        # Print summary
        print(f"\n   Summary for {source}:")
        print(f"     Added:    {len(report['added']):6} new entities")
        print(f"     Updated:  {len(report['updated']):6} modified entities")
        print(f"     Unchanged:{len(report['unchanged']):6} unchanged entities")
        print(f"     Removed:  {len(report['removed']):6} deleted entities")
        print(f"     Total in new data: {len(new_ids)}")
        print(f"     Total in existing: {len(existing_ids)}")
        
        return report
    
    @staticmethod
    def _detect_changes(old_record: Dict, new_record: Dict) -> Dict:
        """Detect which fields changed"""
        changes = {}
        all_keys = set(old_record.keys()) | set(new_record.keys())
        
        for key in all_keys:
            if key.startswith('_'):
                continue  # Skip metadata fields
            
            old_val = old_record.get(key)
            new_val = new_record.get(key)
            
            if old_val != new_val:
                changes[key] = {'from': old_val, 'to': new_val}
        
        return changes


class ImportSessionLogger:
    """Manages import session logging with aggregated statistics for admin dashboard"""
    
    def __init__(self, db):
        self.db = db
        self.log_entries = []
        self.timestamp_start = datetime.utcnow()
        self.timestamp_end = None
        self.statistics = {
            'total': {
                'downloaded': 0,
                'before_update': 0,
                'added': 0,
                'updated': 0,
                'deleted': 0,
                'after_update': 0,
                'unchanged': 0
            },
            'by_source': {}
        }
        self.downloads = []
    
    def log_change(self, change_type: str, entity_id: str, entity_name: str, source: str, 
                   old_data: Dict = None, new_data: Dict = None, changed_fields: Dict = None, 
                   reason: str = None):
        """
        Log a single entity change with optimized storage:
        - ADD: minimal fields (can query from database)
        - UPDATE: only changed field names (can query from database)
        - DELETE: full record (for recovery/audit trail)
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'change_type': change_type,  # 'ADD', 'UPDATE', 'REMOVE'
            'entity_id': entity_id,
            'entity_name': entity_name,
            'source': source,
            'reason': reason,
            'user': 'system_import',
        }
        
        # Store data strategically
        if change_type == 'REMOVE':
            # Store full deleted record for audit trail and recovery
            entry['deleted_data'] = old_data
        elif change_type == 'UPDATE':
            # Store only changed field names, not values
            if changed_fields:
                entry['changed_fields'] = list(changed_fields.keys())
        # For ADD: store nothing extra (can query from sanctions_entities)
        
        self.log_entries.append(entry)
    
    def add_download_info(self, source: str, url: str, status: str, file_size_bytes: int, 
                         downloaded_records: int, downloaded_at: str = None):
        """Record download information"""
        self.downloads.append({
            'source': source,
            'url': url,
            'status': status,
            'file_size_bytes': file_size_bytes,
            'downloaded_records': downloaded_records,
            'downloaded_at': downloaded_at or datetime.utcnow().isoformat()
        })
    
    def calculate_statistics(self, reports: Dict):
        """Calculate aggregated statistics from reports"""
        self.statistics['by_source'] = {}
        
        total_downloaded = 0
        total_before = 0
        total_added = 0
        total_updated = 0
        total_deleted = 0
        total_unchanged = 0
        
        for source, report in reports.items():
            added = len(report.get('added', {}))
            updated = len(report.get('updated', {}))
            deleted = len(report.get('removed', {}))
            unchanged = len(report.get('unchanged', {}))
            
            before_update = updated + unchanged + deleted
            downloaded = added + updated + unchanged
            after_update = added + updated + unchanged
            
            self.statistics['by_source'][source] = {
                'downloaded': downloaded,
                'before_update': before_update,
                'added': added,
                'updated': updated,
                'deleted': deleted,
                'after_update': after_update,
                'unchanged': unchanged
            }
            
            total_downloaded += downloaded
            total_before += before_update
            total_added += added
            total_updated += updated
            total_deleted += deleted
            total_unchanged += unchanged
        
        total_after = total_before + total_added - total_deleted
        
        self.statistics['total'] = {
            'downloaded': total_downloaded,
            'before_update': total_before,
            'added': total_added,
            'updated': total_updated,
            'deleted': total_deleted,
            'after_update': total_after,
            'unchanged': total_unchanged
        }
    
    def save_import_session(self, import_batch_id: str, status: str = 'completed_successfully', 
                           error: str = None):
        """Save import session with statistics to Firestore (replaces audit_logs)"""
        self.timestamp_end = datetime.utcnow()
        duration_seconds = (self.timestamp_end - self.timestamp_start).total_seconds()
        
        print(f"\n[>] Saving import session {import_batch_id}...")
        print(f"[DEBUG] Using Firestore client: {self.db}")
        
        try:
            # First, test that Firestore is working by writing a debug marker
            print(f"[DEBUG] Testing Firestore write...")
            test_write = self.db.collection('_debug_imports').document('test').set({
                'test': True,
                'timestamp': datetime.utcnow().isoformat()
            })
            print(f"[DEBUG] Test write successful: {test_write}")
            
            sessions_coll = self.db.collection('import_sessions')
            session_doc = sessions_coll.document(import_batch_id)
            
            # Create session metadata with statistics
            session_data = {
                'import_session_id': import_batch_id,
                'timestamp_start': self.timestamp_start.isoformat(),
                'timestamp_end': self.timestamp_end.isoformat(),
                'duration_seconds': int(duration_seconds),
                'status': status,
                'error': error,
                'statistics': self.statistics,
                'downloads': self.downloads,
                'total_changes': len(self.log_entries),
                'change_types': self._count_entry_types(),
            }
            
            print(f"   [*] Writing session document to 'import_sessions/{import_batch_id}'...")
            print(f"[DEBUG] Session data keys: {list(session_data.keys())}")
            result1 = session_doc.set(session_data)
            print(f"   [OK] Session document written: {result1}")
            
            # Also write to latest_import_session for instant dashboard reads
            print(f"   [*] Writing to 'latest_import_session'...")
            result2 = sessions_coll.document('latest_import_session').set(session_data)
            print(f"   [OK] Latest session updated: {result2}")
            
            # Save individual change entries as subcollection
            print(f"   [*] Writing {len(self.log_entries)} change entries...")
            write_count = 0
            for i, entry in enumerate(self.log_entries):
                session_doc.collection('entries').document(str(i)).set(entry)
                write_count += 1
                if write_count % 100 == 0:
                    print(f"      ... {write_count} entries written")
            print(f"   [OK] All {len(self.log_entries)} change entries written")
            
            print(f"\n[OK] Import session saved successfully to 'import_sessions/{import_batch_id}'")
            return import_batch_id
            
        except Exception as e:
            print(f"\n[X] ERROR saving import session: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _count_entry_types(self) -> Dict[str, int]:
        """Count changes by type"""
        counts = defaultdict(int)
        for entry in self.log_entries:
            counts[entry['change_type']] += 1
        return dict(counts)


def stage_1_validation(db=None):
    """STAGE 1: Validate new data and generate change report"""
    
    # Use provided db or fall back to module-level db
    _db = db if db is not None else globals()['db']
    print(f"[DEBUG] stage_1_validation using db: {_db}")
    
    print("=" * 80)
    print("STAGE 1: VALIDATION")
    print("=" * 80)
    
    validator = SanctionsDataValidator()
    comparator = SanctionsDataComparator(_db)
    
    sources = ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']
    
    # Determine parsed directory based on environment
    if os.environ.get('CLOUD_RUN_JOB') or os.path.exists('/workspace'):
        # Running in Cloud Run/Functions
        parsed_dir = '/tmp/parsed'
    else:
        # Running locally
        parsed_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'parsed')
    
    print(f"[>] Looking for parsed files in: {parsed_dir}")
    
    all_reports = {}
    
    # Load and validate new data
    print("\n[STEP 1] Loading and validating new data...")
    new_data_by_source = {}
    
    for source in sources:
        file_path = os.path.join(parsed_dir, f"{source}.jsonl")
        new_data_by_source[source] = validator.load_source_data(source, file_path)
    
    # Check for validation errors
    if validator.errors:
        print(f"\n[X] Validation failed with {len(validator.errors)} errors:")
        for error in validator.errors[:10]:  # Show first 10
            print(f"    - {error}")
        if len(validator.errors) > 10:
            print(f"    ... and {len(validator.errors) - 10} more errors")
        return None
    
    if validator.warnings:
        print(f"\n[!] {len(validator.warnings)} warnings:")
        for warning in validator.warnings[:5]:
            print(f"    - {warning}")
    
    # Compare with existing data
    print("\n[STEP 2] Comparing with existing Firestore data...")
    print("[>] Querying existing data (this may take a moment)...")
    
    for source in sources:
        try:
            print(f"[>] Checking {source}...")
            existing_data = comparator.get_existing_data(source)
            new_data = new_data_by_source[source]
            report = comparator.compare(new_data, existing_data, source)
            all_reports[source] = report
        except Exception as e:
            print(f"[ERROR] Failed to compare {source}: {e}")
            print("[!] Continuing with next source...")
            import traceback
            traceback.print_exc()
            continue
    
    # Generate summary
    print("\n" + "=" * 80)
    print("VALIDATION REPORT SUMMARY")
    print("=" * 80)
    
    if not all_reports:
        print("[X] No reports generated. Import aborted.")
        return None
    
    total_added = sum(len(r.get('added', {})) for r in all_reports.values() if r)
    total_updated = sum(len(r.get('updated', {})) for r in all_reports.values() if r)
    total_removed = sum(len(r.get('removed', {})) for r in all_reports.values() if r)
    total_unchanged = sum(len(r.get('unchanged', {})) for r in all_reports.values() if r)
    
    print(f"\nGrand Total:")
    print(f"  Added:     {total_added:6} entities")
    print(f"  Updated:   {total_updated:6} entities")
    print(f"  Removed:   {total_removed:6} entities")
    print(f"  Unchanged: {total_unchanged:6} entities")
    
    if total_removed > 0:
        print(f"\n[!] WARNING: {total_removed} entities will be REMOVED from the database!")
        print("   This may indicate data quality issues in the source files.")
        print("   Review the removed entities before proceeding:")
        for source, report in all_reports.items():
            if report and report.get('removed'):
                print(f"\n   {source} ({len(report['removed'])} removed):")
                for entity_id in list(report['removed'].keys())[:5]:
                    entity = report['removed'][entity_id]
                    print(f"     - {entity.get('main_name')} (ID: {entity_id})")
                if len(report['removed']) > 5:
                    print(f"     ... and {len(report['removed']) - 5} more")
    
    return all_reports


def stage_2_commit(reports: Dict, db=None):
    """STAGE 2: Commit changes to Firestore with optimized import session logging"""
    
    # Use provided db or fall back to module-level db
    _db = db if db is not None else globals()['db']
    print(f"[DEBUG] stage_2_commit called with reports: {type(reports)}")
    print(f"[DEBUG] stage_2_commit using db: {_db}")
    
    if not reports:
        print("\n[!] No reports to commit. Aborting.")
        return
    
    print("\n" + "=" * 80)
    print("STAGE 2: COMMIT")
    print("=" * 80)
    
    print("\n[>] Auto-committing changes (no manual intervention required)...")
    
    # Initialize import session logger
    import_batch_id = f"import_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    print(f"[DEBUG] Creating ImportSessionLogger with db type: {type(_db)}")
    session_logger = ImportSessionLogger(_db)
    
    # Calculate statistics for admin dashboard
    print(f"[DEBUG] Calculating statistics...")
    session_logger.calculate_statistics(reports)
    print(f"[DEBUG] Statistics calculated: {session_logger.statistics['total']}")
    
    print(f"\n[>] Starting data commit with batch ID: {import_batch_id}")
    
    # Commit changes
    coll = _db.collection('sanctions_entities')
    total_committed = 0
    
    for source, report in reports.items():
        print(f"\n[>] Committing {source}...")
        
        # Add new records
        for idx, (entity_id, record) in enumerate(report['added'].items(), 1):
            coll.document(entity_id).set(record, merge=False)
            entity_name = record.get('main_name', entity_id)
            session_logger.log_change('ADD', entity_id, entity_name, source,
                                     reason='New entity in sanctions list')
            total_committed += 1
            if idx % 1000 == 0:
                print(f"    Added {idx} records...")
        
        # Update modified records
        for idx, (entity_id, changes) in enumerate(report['updated'].items(), 1):
            coll.document(entity_id).set(changes['new'], merge=False)
            entity_name = changes['new'].get('main_name', entity_id)
            session_logger.log_change('UPDATE', entity_id, entity_name, source,
                                     old_data=changes['old'],
                                     changed_fields=changes['changed_fields'],
                                     reason=f"Updated fields: {list(changes['changed_fields'].keys())}")
            total_committed += 1
            if idx % 1000 == 0:
                print(f"    Updated {idx} records...")
        
        # Remove deleted records (with confirmation)
        if report['removed']:
            print(f"\n   [!] Removing {len(report['removed'])} entities from {source}...")
            for idx, (entity_id, record) in enumerate(report['removed'].items(), 1):
                coll.document(entity_id).delete()
                entity_name = record.get('main_name', entity_id)
                session_logger.log_change('REMOVE', entity_id, entity_name, source, 
                                         old_data=record,
                                         reason='Entity no longer in sanctions list')
                total_committed += 1
                if idx % 1000 == 0:
                    print(f"    Removed {idx} records...")
    
    # Save import session with statistics
    try:
        # Write a pre-session marker to confirm we reach this point
        try:
            _db.collection('_debug_imports').document('pre_session_save').set({
                'ts': datetime.utcnow().isoformat(),
                'import_batch_probe': True
            })
            print(f"[DEBUG] Wrote pre_session_save marker")
        except Exception as pre_marker_err:
            print(f"[WARNING] Could not write pre_session_save marker: {pre_marker_err}")

        session_logger.save_import_session(import_batch_id)

        # Write a post-session marker to confirm success
        try:
            _db.collection('_debug_imports').document('post_session_save').set({
                'ts': datetime.utcnow().isoformat(),
                'saved_session_id': import_batch_id
            })
            print(f"[DEBUG] Wrote post_session_save marker")
        except Exception as post_marker_err:
            print(f"[WARNING] Could not write post_session_save marker: {post_marker_err}")
    except Exception as session_err:
        print(f"\n[X] CRITICAL: Failed to save import session: {session_err}")
        import traceback
        traceback.print_exc()
        # Try to at least log failure status to Firebase
        try:
            db.collection('import_sessions').document(import_batch_id).set({
                'import_session_id': import_batch_id,
                'status': 'completed_with_session_logging_failure',
                'error': f'Session save failed: {str(session_err)}',
                'timestamp_start': session_logger.timestamp_start.isoformat(),
                'timestamp_end': datetime.utcnow().isoformat(),
            })
            print(f"[OK] Logged failure status to 'import_sessions/{import_batch_id}'")
        except Exception as fallback_err:
            print(f"[X] CRITICAL: Even fallback session logging failed: {fallback_err}")
        raise  # Re-raise so caller knows about this failure
    
    # Print statistics summary
    stats = session_logger.statistics['total']
    print(f"\n" + "=" * 80)
    print(f"IMPORT STATISTICS SUMMARY")
    print(f"=" * 80)
    print(f"\nRecords by source:")
    for source, src_stats in session_logger.statistics['by_source'].items():
        print(f"\n  {source}:")
        print(f"    Downloaded:     {src_stats['downloaded']:6}")
        print(f"    Before update:  {src_stats['before_update']:6}")
        print(f"    Added:          {src_stats['added']:6}")
        print(f"    Updated:        {src_stats['updated']:6}")
        print(f"    Deleted:        {src_stats['deleted']:6}")
        print(f"    After update:   {src_stats['after_update']:6}")
    
    print(f"\nGrand Total:")
    print(f"  Downloaded:     {stats['downloaded']:6}")
    print(f"  Before update:  {stats['before_update']:6}")
    print(f"  Added:          {stats['added']:6}")
    print(f"  Updated:        {stats['updated']:6}")
    print(f"  Deleted:        {stats['deleted']:6}")
    print(f"  After update:   {stats['after_update']:6}")
    
    print(f"\n" + "=" * 80)
    print(f"[OK] COMMIT SUCCESSFUL")
    print(f"=" * 80)
    print(f"\nTotal changes committed: {total_committed}")
    print(f"Import session ID: {import_batch_id}")
    print(f"Duration: {int(session_logger.statistics['total'].get('duration_seconds', 0))} seconds")
    print(f"\nYou can review the import session at:")
    print(f"  Firestore > import_sessions > {import_batch_id}")


if __name__ == '__main__':
    # Stage 1: Validate
    reports = stage_1_validation()
    
    if reports:
        # Stage 2: Commit (with confirmation)
        stage_2_commit(reports)
    else:
        print("\n[X] Validation failed. No changes committed.")
        sys.exit(1)
