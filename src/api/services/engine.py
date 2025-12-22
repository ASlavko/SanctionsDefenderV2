import rapidfuzz
import json
from sqlalchemy.orm import Session
from src.db.models import SanctionRecord, MatchDecision, MatchStatus
from src.core.matching import NameMatcher
from typing import List, Dict, Tuple
import time

class SearchEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchEngine, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        self.names: List[str] = []        # Normalized names for RapidFuzz
        self.ids: List[str] = []          # Corresponding IDs
        self.records: Dict[str, SanctionRecord] = {} # Map ID -> Record
        self.decisions: Dict[str, MatchDecision] = {} # Map "normalized_search_term" -> Decision
        self.initialized = True

    def load_data(self, db: Session):
        """
        Loads all active sanctions and user decisions into memory.
        Call this on startup and after daily updates.
        """
        print("Loading Sanctions Data into Memory...")
        start = time.time()
        
        # 1. Load Sanctions
        # Check if table exists first (for fresh init)
        try:
            sanctions = db.query(SanctionRecord).filter(SanctionRecord.is_active == True).all()
            
            self.names = []
            self.ids = []
            self.records = {}
            
            for s in sanctions:
                self.records[s.id] = s
                
                # 1. Add Primary Name
                if s.normalized_name:
                    self.names.append(s.normalized_name)
                    self.ids.append(s.id)
                
                # 2. Add Aliases
                if s.alias_names:
                    try:
                        # Handle both JSON string and potential list (if DB adapter converts it)
                        aliases = s.alias_names
                        if isinstance(aliases, str):
                            if aliases.startswith("["):
                                aliases = json.loads(aliases)
                            else:
                                # Fallback for pipe-separated or other formats if any
                                # Attempt to split on common delimiters
                                if "|" in aliases:
                                    aliases = [x.strip() for x in aliases.split("|") if x.strip()]
                                elif ";" in aliases:
                                    aliases = [x.strip() for x in aliases.split(";") if x.strip()]
                                else:
                                    aliases = [aliases]
                        
                        if isinstance(aliases, list):
                            for alias in aliases:
                                norm_alias = NameMatcher.normalize_name(alias)
                                if norm_alias and norm_alias != s.normalized_name:
                                    self.names.append(norm_alias)
                                    self.ids.append(s.id)
                    except Exception:
                        # Ignore alias parsing errors to keep loading safe
                        pass

            # 2. Load Decisions (Memory)
            decisions = db.query(MatchDecision).all()
            self.decisions = {d.search_term_normalized: d for d in decisions}
            
            print(
                f"Loaded {len(self.records)} active sanctions, "
                f"{len(self.names)} names (primary + aliases), "
                f"{len(self.decisions)} decisions in {time.time() - start:.2f}s"
            )
        except Exception as e:
            print(f"Warning: Could not load data (tables might be empty): {e}")

    def search(self, query_name: str, limit: int = 5, threshold: int = 85) -> List[Dict]:
        """
        Performs a single search.
        Returns a list of matches with scores and status (PENDING/CLEARED/CONFIRMED).
        """
        normalized_query = NameMatcher.normalize_name(query_name)
        
        # 1. Check "Memory" (User Decisions)
        if normalized_query in self.decisions:
            decision = self.decisions[normalized_query]
            if decision.decision == MatchStatus.FALSE_POSITIVE:
                return [] # Auto-cleared
            elif decision.decision == MatchStatus.TRUE_MATCH and decision.sanction_id:
                record = self.records.get(decision.sanction_id)
                if record:
                    return [{
                        "record": record,
                        "score": 100.0,
                        "status": MatchStatus.TRUE_MATCH,
                        "auto_resolved": True
                    }]

        # 2. Fuzzy Search
        if not self.names:
            return []

        results = rapidfuzz.process.extract(
            normalized_query,
            self.names,
            limit=limit,
            scorer=rapidfuzz.fuzz.token_sort_ratio
        )
        
        matches = []
        for match_name, score, idx in results:
            if score < threshold:
                continue
                
            record_id = self.ids[idx]
            record = self.records.get(record_id)
            
            matches.append({
                "record": record,
                "score": score,
                "status": MatchStatus.PENDING,
                "auto_resolved": False
            })
            
        return matches

    def batch_search(self, names: List[str], threshold: int = 85) -> List[Dict]:
        """
        Optimized for batch processing using rapidfuzz.process.cdist (Vectorized).
        """
        import numpy as np
        
        # If no names to search, return empty
        if not names:
            return []
            
        # If no sanctions loaded, return no matches
        if not self.names:
            return [{
                "input_name": name,
                "match_status": MatchStatus.NO_MATCH,
                "max_score": 0.0,
                "potential_match": None
            } for name in names]

        results = []
        chunk_size = 500 # Process 500 names at a time against 80k sanctions
        
        for i in range(0, len(names), chunk_size):
            chunk = names[i:i+chunk_size]
            
            # Normalize chunk names to match the normalized names in self.names
            normalized_chunk = [NameMatcher.normalize_name(n) for n in chunk]
            
            # Calculate distance matrix
            # Returns (len(chunk), len(self.names)) matrix of scores
            matrix = rapidfuzz.process.cdist(
                normalized_chunk, 
                self.names, 
                scorer=rapidfuzz.fuzz.token_sort_ratio,
                dtype=np.float32
            )
            
            # Find best match for each query in the chunk
            max_scores = np.max(matrix, axis=1)
            max_indices = np.argmax(matrix, axis=1)
            
            for j, score in enumerate(max_scores):
                input_name = chunk[j]
                
                if score < threshold:
                    results.append({
                        "input_name": input_name,
                        "match_status": MatchStatus.NO_MATCH,
                        "max_score": float(score),
                        "potential_match": None
                    })
                else:
                    idx = max_indices[j]
                    record_id = self.ids[idx]
                    record = self.records.get(record_id)
                    
                    results.append({
                        "input_name": input_name,
                        "match_status": MatchStatus.PENDING,
                        "max_score": float(score),
                        "potential_match": record
                    })
                    
        return results

    def get_status(self) -> Dict[str, any]:
        """
        Returns runtime details useful for diagnostics and status checks.
        """
        try:
            sanctions_loaded = len(self.names)
            unique_records = len(self.records)
            decisions_loaded = len(self.decisions)
        except Exception:
            sanctions_loaded = 0
            unique_records = 0
            decisions_loaded = 0

        return {
            "engine_initialized": self.initialized,
            "sanctions_loaded": sanctions_loaded,
            "unique_records": unique_records,
            "decisions_loaded": decisions_loaded,
            "scorer": "rapidfuzz.fuzz.token_sort_ratio",
            "threshold_default": 85,
            "chunk_size": 500,
            "vectorized_batch": True,
            "include_aliases": True
        }

search_engine = SearchEngine()
