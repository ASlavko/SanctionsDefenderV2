import functions_framework
import json
from google.cloud import firestore
from flask import jsonify
from datetime import datetime
from matching import match_name

db = firestore.Client()

@functions_framework.http
def search_status(request):
    """
    Check the status of a deep search request.
    
    Query parameters:
    - request_id: The unique ID returned from initial search
    
    Returns:
    - status: 'partial' (quick search only), 'success' (deep search complete), or 'error'
    - matches: Results (quick or deep depending on status)
    - query_time_ms: Execution time
    """
    
    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)
    
    request_id = request.args.get('request_id', '').strip()
    
    if not request_id:
        return jsonify({
            'error': 'request_id parameter required',
            'status': 'invalid_request'
        }), 400
    
    try:
        # Fetch search request from Firestore
        doc_ref = db.collection('search_requests').document(request_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({
                'error': 'Search request not found',
                'status': 'not_found'
            }), 404
        
        data = doc.to_dict()
        status = data.get('status', 'partial')
        
        response = {
            'status': status,
            'request_id': request_id
        }
        
        if status == 'success':
            # Deep search complete - return deep results
            response['matches'] = data.get('deep_results', [])
            response['count'] = len(response['matches'])
            response['quick_search_time_ms'] = data.get('quick_search_time_ms', 0)
            response['deep_search_time_ms'] = data.get('deep_search_time_ms', 0)
            response['total_time_ms'] = response['quick_search_time_ms'] + response['deep_search_time_ms']
            response['query'] = data.get('query_params', {})
            
        elif status == 'partial':
            # If deep results are not yet computed, run deep search synchronously as a fallback
            deep_results = data.get('deep_results')
            if not deep_results:
                deep_results, deep_time_ms = _run_deep_search(data)
                # Persist completion so subsequent polls return immediately
                doc_ref.update({
                    'status': 'success',
                    'deep_results': deep_results,
                    'deep_search_time_ms': deep_time_ms,
                    'completed_at': datetime.now(),
                    'total_found': len(deep_results)
                })
                status = 'success'
                response['status'] = 'success'
                response['matches'] = deep_results
                response['count'] = len(deep_results)
                response['quick_search_time_ms'] = data.get('quick_search_time_ms', 0)
                response['deep_search_time_ms'] = deep_time_ms
                response['total_time_ms'] = response['quick_search_time_ms'] + deep_time_ms
                response['query'] = data.get('query_params', {})
            else:
                # Deep search still running - return quick results
                response['matches'] = data.get('quick_results', [])
                response['count'] = len(response['matches'])
                response['query_time_ms'] = data.get('quick_search_time_ms', 0)
                response['message'] = 'Deep search in progress...'
                response['query'] = data.get('query_params', {})
            
        elif status == 'error':
            response['error'] = data.get('error', 'Unknown error occurred')
            response['matches'] = data.get('quick_results', [])
            response['count'] = len(response['matches'])
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
        
        return (json.dumps(response, ensure_ascii=False), 200, headers)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


def _run_deep_search(data):
    """Run deep search synchronously as a fallback when background thread did not complete."""
    start_time = datetime.now()
    params = data.get('query_params', {}) or {}
    query = (params.get('q') or '').lower()
    entity_type = (params.get('type') or '').lower()
    country = (params.get('country') or '').lower()
    program = (params.get('program') or '').upper()
    source = (params.get('source') or '').upper()
    limit = int(params.get('limit') or 50)
    limit = min(limit, 500)

    results = []

    q = db.collection('sanctions_entities')
    if source:
        q = q.where('sanction_source', '==', source)
    if entity_type:
        q = q.where('entity_type', '==', entity_type)
    q = q.limit(5000)

    docs = list(q.stream())

    for doc in docs:
        record = doc.to_dict()
        score = _calculate_score(record, query, country, program, source)
        if score >= 50:
            results.append({
                'id': record.get('id'),
                'source': record.get('sanction_source'),
                'name': record.get('main_name'),
                'aliases': record.get('aliases', []),
                'entity_type': record.get('entity_type'),
                'country': record.get('country'),
                'gender': record.get('gender'),
                'dob': record.get('date_of_birth'),
                'programs': record.get('details', {}).get('programs', []),
                'confidence': round(score, 2)
            })

    results.sort(key=lambda x: x['confidence'], reverse=True)
    results = results[:limit]

    exec_time_ms = (datetime.now() - start_time).total_seconds() * 1000
    return results, round(exec_time_ms, 2)


def _calculate_score(record, query, country, program, source):
    """Match scoring copied from deep search to keep behavior consistent."""
    score = 0

    if query:
        entity_type = record.get('entity_type', 'individual').lower()
        entity_category = 'company' if entity_type == 'company' else 'individual'
        name_score = match_name(query, record, entity_type=entity_category, use_phonetic=True)
        score = name_score

    if country:
        record_country = record.get('country', '')
        if record_country:
            record_country = record_country.lower()
            if country in record_country or record_country in country:
                score = min(score + 15, 100)

    if program:
        programs = [p.upper() for p in record.get('details', {}).get('programs', [])]
        if program in programs:
            score = min(score + 15, 100)

    return score
