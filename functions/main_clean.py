import functions_framework
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import tempfile
import json
import firebase_admin
from firebase_admin import firestore
from flask import jsonify

# import local parsers
from parse_eu import parse_eu_to_jsonl
from parse_uk import parse_uk_to_jsonl
from parse_us_simple import parse_us_simple_to_jsonl

# --- Configuration ---
# Define the URLs for the sanctions lists
SANCTIONS_LIST_URLS = {
    "EU": "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw",
    "UK": "https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.xml",
    "US_SDN_SIMPLE": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.XML",
    "US_NON_SDN_SIMPLE": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/CONSOLIDATED.XML",
    # Using SIMPLE versions because they match our parser structure
}

# --- Helper function to perform the download and processing ---
def _perform_download():
    """
    Perform the actual download and processing logic.
    """
    print(f"[{datetime.now()}] Starting daily sanctions list download.")

    download_results = {}

    # Initialize Firestore (singleton)
    try:
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
        print(f"[{datetime.now()}] [OK] Firestore initialized")
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Could not initialize firebase_admin: {e}")
        db = None

    for source_name, url in SANCTIONS_LIST_URLS.items():
        print(f"[{datetime.now()}] Attempting to download {source_name} from: {url}")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            # Use /tmp in Cloud Run, local data/ path for local testing
            if os.environ.get('CLOUD_RUN_JOB') or os.path.exists('/workspace'):
                target_dir = '/tmp/sanctions'
                parsed_dir = '/tmp/parsed'
            else:
                target_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'sanctions')
                parsed_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'parsed')
            
            os.makedirs(target_dir, exist_ok=True)
            os.makedirs(parsed_dir, exist_ok=True)
            
            xml_path = os.path.join(target_dir, f"{source_name}.xml")
            with open(xml_path, 'wb') as f:
                f.write(response.content)

            print(f"[{datetime.now()}] Successfully saved {source_name} ({os.path.getsize(xml_path)} bytes).")

            # Attempt to parse into JSONL using available parsers
            parsed_path = os.path.join(parsed_dir, f"{source_name}.jsonl")
            parsed_file = None
            try:
                if source_name == 'EU':
                    parsed_file = parse_eu_to_jsonl(xml_path, parsed_path)
                elif source_name == 'UK':
                    parsed_file = parse_uk_to_jsonl(xml_path, parsed_path)
                else:
                    parsed_file = parse_us_simple_to_jsonl(xml_path, parsed_path, source_name)
            except Exception as pe:
                print(f"[{datetime.now()}] Parser error for {source_name}: {pe}")
                parsed_file = None

            download_results[source_name] = {
                'xml_path': xml_path,
                'parsed_path': parsed_file,
                'status': 'parsed_and_ready_for_import'
            }

        except requests.exceptions.RequestException as e:
            print(f"[{datetime.now()}] ERROR downloading {source_name}: {e}")
            download_results[source_name] = {'error': str(e)}
        except Exception as e:
            print(f"[{datetime.now()}] An unexpected error occurred for {source_name}: {e}")
            download_results[source_name] = {'unexpected_error': str(e)}

    print(f"[{datetime.now()}] Daily sanctions list download finished.")
    
    # After successful download and parsing, trigger the two-stage import
    print(f"[{datetime.now()}] Triggering two-stage import...")
    try:
        # Import the two-stage functions and get their module-level db
        from import_sanctions_two_stage import stage_1_validation, stage_2_commit, db as module_db
        
        if not module_db:
            print(f"[{datetime.now()}] [ERROR] Module db is None!")
            download_results['import_status'] = 'error_no_db'
            return {"status": "completed", "details": download_results}
        
        print(f"[{datetime.now()}] [OK] Using module_db from import_sanctions_two_stage")
        
        # Generate batch ID for this import
        import_batch_id = f"import_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Stage 1: Validate
        print(f"[{datetime.now()}] Stage 1: Validating...")
        reports = stage_1_validation(db=module_db)
        
        if reports:
            # Stage 2: Commit
            print(f"[{datetime.now()}] Stage 2: Committing...")
            try:
                stage_2_commit(reports, db=module_db)
                download_results['import_status'] = 'completed_with_validation'
                print(f"[{datetime.now()}] Two-stage import SUCCEEDED")
            except Exception as stage2_err:
                print(f"[{datetime.now()}] ERROR in Stage 2: {stage2_err}")
                import traceback
                traceback.print_exc()
                download_results['import_status'] = 'stage2_error'
                download_results['error'] = str(stage2_err)
                # Try fallback logging
                try:
                    module_db.collection('import_sessions').document(import_batch_id).set({
                        'import_session_id': import_batch_id,
                        'timestamp_start': datetime.utcnow().isoformat(),
                        'timestamp_end': datetime.utcnow().isoformat(),
                        'status': 'stage2_error',
                        'error': str(stage2_err)
                    })
                    print(f"[{datetime.now()}] [OK] Logged stage2 failure")
                except Exception as log_err:
                    print(f"[{datetime.now()}] [ERROR] Could not log stage2 failure: {log_err}")
        else:
            print(f"[{datetime.now()}] Validation FAILED or no data to import")
            download_results['import_status'] = 'validation_failed'
            # Log validation failure
            try:
                module_db.collection('import_sessions').document(import_batch_id).set({
                    'import_session_id': import_batch_id,
                    'timestamp_start': datetime.utcnow().isoformat(),
                    'timestamp_end': datetime.utcnow().isoformat(),
                    'status': 'validation_failed',
                    'error': 'No valid reports generated'
                })
                print(f"[{datetime.now()}] [OK] Logged validation failure")
            except Exception as log_err:
                print(f"[{datetime.now()}] [ERROR] Could not log validation failure: {log_err}")
    
    except Exception as import_err:
        print(f"[{datetime.now()}] ERROR in two-stage import: {import_err}")
        import traceback
        traceback.print_exc()
        download_results['import_status'] = 'import_error'
        download_results['error'] = str(import_err)
    
    return {"status": "completed", "details": download_results}


# --- Cloud Function Entry Points ---

@functions_framework.http
def download_sanctions_lists(request):
    """
    HTTP entry point for Cloud Functions 2nd gen.
    Can be triggered via HTTP POST or by Pub/Sub via Cloud Run.
    """
    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        result = _perform_download()
        response = jsonify(result)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 200
    except Exception as e:
        print(f"[{datetime.now()}] Error in download_sanctions_lists: {e}")
        import traceback
        traceback.print_exc()
        error_response = jsonify({"error": str(e)})
        error_response.headers['Access-Control-Allow-Origin'] = '*'
        return error_response, 500


@functions_framework.cloud_event
def download_sanctions_lists_event(cloud_event):
    """
    Event handler for Pub/Sub messages (alternative trigger).
    """
    _perform_download()


@functions_framework.http
def admin_dashboard_api(request):
    """
    Admin Dashboard API - provides statistics and system health data.
    """
    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Allow manual run trigger via action=run_update
        payload = request.get_json(silent=True) or {}
        action = request.args.get('action') or payload.get('action')
        if action == 'run_update':
            result = _perform_download()
            response = jsonify({'status': 'triggered', 'result': result})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 200

        # Initialize Firestore
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()
        
        # Get statistics from cached metadata
        sources_stats = {}
        sources = ['EU', 'UK', 'US_SDN_SIMPLE', 'US_NON_SDN_SIMPLE']
        
        # Try to get from latest_import_session document
        try:
            latest_doc = db.collection('import_sessions').document('latest_import_session').get()
            
            latest_stats = None
            latest_session_data = None
            
            if latest_doc.exists:
                latest_session_data = latest_doc.to_dict()
                latest_stats = latest_session_data.get('statistics', {}).get('by_source', {})
            
            if latest_stats:
                for source in sources:
                    src_stats = latest_stats.get(source, {})
                    record_count = src_stats.get('after_update', 0)
                    sources_stats[source] = {
                        'current_count': record_count,
                        'health': 'healthy' if record_count > 0 else 'warning'
                    }
            else:
                # No import sessions yet, return zeros
                for source in sources:
                    sources_stats[source] = {
                        'current_count': 0,
                        'health': 'warning'
                    }
        except Exception as e:
            print(f"[{datetime.now()}] Error reading import session stats: {e}")
            # Return zeros on error
            for source in sources:
                sources_stats[source] = {
                    'current_count': 0,
                    'health': 'error'
                }
        
        # Get last 10 import sessions for history
        sessions_history = []
        try:
            sessions = db.collection('import_sessions').limit(20).stream()
            
            all_sessions = []
            for session in sessions:
                if session.id == 'latest_import_session':
                    continue
                session_data = session.to_dict()
                all_sessions.append(session_data)
            
            # Sort by timestamp_end in memory
            all_sessions.sort(key=lambda x: x.get('timestamp_end', ''), reverse=True)
            
            # Take top 10
            for session_data in all_sessions[:10]:
                sessions_history.append({
                    'id': session_data.get('import_session_id'),
                    'timestamp': session_data.get('timestamp_end'),
                    'duration': session_data.get('duration_seconds'),
                    'status': session_data.get('status'),
                    'total_changes': session_data.get('total_changes', 0),
                    'statistics': session_data.get('statistics', {})
                })
        except Exception as e:
            print(f"[{datetime.now()}] Error reading import session history: {e}")
        
        # Calculate total database size
        total_records = sum(s['current_count'] for s in sources_stats.values())
        
        # Get next scheduled run
        from datetime import timedelta
        now = datetime.utcnow()
        next_run = datetime(now.year, now.month, now.day, 4, 0, 0)
        if now.hour >= 4:
            next_run += timedelta(days=1)
        
        response_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_health': 'healthy' if total_records > 0 else 'error',
            'total_records': total_records,
            'sources': sources_stats,
            'latest_import': latest_session_data,
            'import_history': sessions_history,
            'next_scheduled_run': next_run.isoformat() + 'Z',
            'scheduler': {
                'enabled': True,
                'schedule': '0 4 * * *',
                'description': 'Daily at 4:00 AM UTC'
            }
        }
        
        return (jsonify(response_data), 200, headers)
        
    except Exception as e:
        print(f"[{datetime.now()}] Error in admin dashboard API: {e}")
        import traceback
        traceback.print_exc()
        return (jsonify({"error": str(e)}), 500, headers)
