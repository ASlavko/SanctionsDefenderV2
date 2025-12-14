import functions_framework
import json
from google.cloud import firestore
from google.cloud import logging
from datetime import datetime
from flask import jsonify
import re
import uuid
import threading
from matching import match_name, NameMatcher

# Setup logging
def log_debug(message):
    print(f"[DEBUG] {message}")

db = None

def get_db():
    global db
    if db is None:
        db = firestore.Client()
    return db

@functions_framework.http
def search_sanctions(request):
    """
    Search sanctions database by name, country, program, or entity type.
    
    Query parameters:
    - q: Search query (name, country, program)
    - type: Filter by entity type (individual, company)
    - country: Filter by country
    - program: Filter by program (EU, SDN, NS-PLC, etc)
    - limit: Max results (default 50, max 500)
    - source: Filter by source (EU, UK, US_SDN_SIMPLE, US_NON_SDN_SIMPLE)
    
    Returns:
    - matches: Array of matching sanctions records with confidence scores
    - count: Total number of matches
    - query_time_ms: Query execution time
    """
    
    start_time = datetime.now()
    
    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)
    
    # Get query parameters
    query = request.args.get('q', '').strip().lower()
    entity_type = request.args.get('type', '').lower()
    country = request.args.get('country', '').strip().lower()
    program = request.args.get('program', '').strip().upper()
    source = request.args.get('source', '').upper()
    limit = min(int(request.args.get('limit', 50)), 500)
    
    # Validate
    if not query and not country and not program and not source:
        return jsonify({
            'error': 'At least one search parameter required (q, country, program, source)',
            'status': 'invalid_request'
        }), 400
    
    try:
        # Generate unique request ID for this search
        request_id = str(uuid.uuid4())
        
        # PHASE 1: Quick search - return immediately with basic matching
        quick_results = _quick_search(query, entity_type, country, program, source, limit)
        
        # Calculate execution time for quick search
        exec_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Store initial results in Firestore for polling
        search_doc_ref = get_db().collection('search_requests').document(request_id)
        search_doc_ref.set({
            'request_id': request_id,
            'status': 'partial',
            'created_at': datetime.now(),
            'query_params': {
                'q': query,
                'type': entity_type,
                'country': country,
                'program': program,
                'source': source,
                'limit': limit
            },
            'quick_results': quick_results,
            'quick_search_time_ms': round(exec_time_ms, 2)
        })
        
        # PHASE 2: Deep search - start in background thread
        thread = threading.Thread(
            target=_deep_search_background,
            args=(request_id, query, entity_type, country, program, source, limit)
        )
        thread.daemon = True
        thread.start()
        
        # Return quick results immediately
        response = {
            'status': 'partial',
            'request_id': request_id,
            'matches': quick_results,
            'count': len(quick_results),
            'query_time_ms': round(exec_time_ms, 2),
            'message': 'Quick search complete. Deep search running in background.',
            'query': {
                'search': query,
                'country': country if country else None,
                'program': program if program else None,
                'type': entity_type if entity_type else None,
                'source': source if source else None
            }
        }
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
        
        return (json.dumps(response, ensure_ascii=False), 200, headers)
    
    except Exception as e:
        exec_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        return jsonify({
            'status': 'error',
            'error': str(e),
            'query_time_ms': round(exec_time_ms, 2)
        }), 500


def _quick_search(query, entity_type, country, program, source, limit):
    """
    Phase 1: Quick search using indexed search tokens.
    Returns results within 1-2 seconds for immediate user feedback.
    """
    results = []
    
    # Build query with filters
    q = get_db().collection('sanctions_entities')
    
    if source:
        q = q.where('sanction_source', '==', source)
    
    if entity_type:
        q = q.where('entity_type', '==', entity_type)
    
    # Use indexed search if query is present
    if query:
        # Generate tokens from query
        tokens = NameMatcher.generate_search_tokens(query)
        log_debug(f"Query='{query}', Tokens={tokens}")
        if tokens:
            # Use the longest token for array-contains query (most specific)
            search_token = max(tokens, key=len)
            log_debug(f"Using search_token='{search_token}'")
            q = q.where('search_tokens', 'array_contains', search_token)
    
    # Limit to 1000 docs for quick scan
    q = q.limit(1000)
    
    docs = list(q.stream())
    log_debug(f"Found {len(docs)} docs in Firestore")
    
    for doc in docs:
        data = doc.to_dict()
        # Simple scoring for quick phase - just basic substring matching
        score = _simple_score(data, query, country, program)
        
        # Lower threshold for quick search (40%) to be more inclusive
        if score >= 40:
            results.append({
                'id': data.get('id'),
                'source': data.get('sanction_source'),
                'name': data.get('main_name'),
                'aliases': data.get('aliases', []),
                'entity_type': data.get('entity_type'),
                'country': data.get('country'),
                'gender': data.get('gender'),
                'dob': data.get('date_of_birth'),
                'programs': data.get('details', {}).get('programs', []),
                'confidence': round(score, 2)
            })
    
    # Sort by confidence and limit
    results.sort(key=lambda x: x['confidence'], reverse=True)
    return results[:limit]


def _simple_score(record, query, country, program):
    """
    Simple scoring for quick search - uses basic string matching.
    Fast but less accurate than deep search.
    """
    score = 0
    
    if query:
        query_lower = query.lower()
        main_name = record.get('main_name', '').lower()
        
        # Exact substring match
        if query_lower in main_name:
            score = 70
        # Check aliases
        else:
            aliases = record.get('aliases', [])
            for alias in aliases:
                if query_lower in alias.lower():
                    score = 60
                    break
        
        # Check if main name in query (reversed)
        if score == 0 and main_name and main_name in query_lower:
            score = 50
    
    # Country bonus
    if country and score > 0:
        record_country = record.get('country', '').lower()
        if country in record_country:
            score = min(score + 10, 100)
    
    # Program bonus
    if program and score > 0:
        programs = [p.upper() for p in record.get('details', {}).get('programs', [])]
        if program in programs:
            score = min(score + 10, 100)
    
    return score


def _deep_search_background(request_id, query, entity_type, country, program, source, limit):
    """
    Phase 2: Deep search with advanced fuzzy matching.
    Runs in background thread and updates Firestore when complete.
    """
    try:
        start_time = datetime.now()
        results = []
        
        # Query with higher limit for comprehensive search
        q = get_db().collection('sanctions_entities')
        
        if source:
            q = q.where('sanction_source', '==', source)
        
        if entity_type:
            q = q.where('entity_type', '==', entity_type)
        
        # Scan more documents for thorough search
        q = q.limit(5000)
        
        docs = list(q.stream())
        
        # Use advanced matching for accurate scoring
        for doc in docs:
            data = doc.to_dict()
            score = _calculate_score(data, query, country, program, source)
            
            # Standard threshold (50%) for deep search
            if score >= 50:
                results.append({
                    'id': data.get('id'),
                    'source': data.get('sanction_source'),
                    'name': data.get('main_name'),
                    'aliases': data.get('aliases', []),
                    'entity_type': data.get('entity_type'),
                    'country': data.get('country'),
                    'gender': data.get('gender'),
                    'dob': data.get('date_of_birth'),
                    'programs': data.get('details', {}).get('programs', []),
                    'confidence': round(score, 2)
                })
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        results = results[:limit]
        
        exec_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Update Firestore with deep search results
        search_doc_ref = get_db().collection('search_requests').document(request_id)
        search_doc_ref.update({
            'status': 'success',
            'deep_results': results,
            'deep_search_time_ms': round(exec_time_ms, 2),
            'completed_at': datetime.now(),
            'total_found': len(results)
        })
        
    except Exception as e:
        # Log error and update status
        try:
            get_db().collection('search_requests').document(request_id).update({
                'status': 'error',
                'error': str(e),
                'completed_at': datetime.now()
            })
        except:
            pass  # If update fails, silently continue


def _calculate_score(record, query, country, program, source):
    """
    Calculate match confidence score (0-100) using advanced fuzzy matching.
    
    Scoring priority:
    1. Query name match (advanced fuzzy with phonetic): 0-100
    2. Country match: +10-15 points
    3. Program match: +10-15 points
    4. Source match: +5 points (implicit from filtering)
    """
    score = 0
    
    # Name matching (highest priority) - uses advanced fuzzy matching
    if query:
        entity_type = record.get('entity_type', 'individual').lower()
        # Determine if entity is company or individual for normalization
        entity_category = 'company' if entity_type == 'company' else 'individual'
        
        # Use advanced matching algorithm
        name_score = match_name(query, record, entity_type=entity_category, use_phonetic=True)
        score = name_score  # Base score from name matching
    
    # Country matching (bonus)
    if country:
        record_country = record.get('country', '')
        if record_country:  # Check if country field exists before calling .lower()
            record_country = record_country.lower()
            if country in record_country or record_country in country:
                score = min(score + 15, 100)  # Add up to 15 points, cap at 100
    
    # Program matching (bonus)
    if program:
        programs = [p.upper() for p in record.get('details', {}).get('programs', [])]
        if program in programs:
            score = min(score + 15, 100)  # Add up to 15 points, cap at 100
    
    return score

